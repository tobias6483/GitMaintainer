import datetime as dt
import json
from email.message import Message
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from gitmaintainer.github import (
    GITHUB_API,
    GitHubClient,
    _JsonResponse,
    _bus_factor,
    _first_non_author_comment,
    _package_manifests_from_contents,
    _parse_link_header,
    _with_per_page,
)

FIXTURES = Path(__file__).parent / "fixtures" / "github"


def _fixture(name: str) -> object:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_bus_factor_estimates_authors_needed_for_80_percent_of_recent_commits() -> None:
    commits = [
        {"author": {"login": "a"}},
        {"author": {"login": "a"}},
        {"author": {"login": "a"}},
        {"author": {"login": "b"}},
        {"author": {"login": "c"}},
    ]

    assert _bus_factor(commits) == 2


def test_bus_factor_falls_back_to_commit_email() -> None:
    commits = [
        {"author": None, "commit": {"author": {"email": "a@example.com"}}},
        {"author": None, "commit": {"author": {"email": "b@example.com"}}},
    ]

    assert _bus_factor(commits) == 2


def test_first_non_author_comment_ignores_issue_author() -> None:
    comments = [
        {"user": {"login": "reporter"}, "created_at": "2026-01-01T00:00:00Z"},
        {"user": {"login": "maintainer"}, "created_at": "2026-01-02T00:00:00Z"},
    ]

    first_response = _first_non_author_comment(comments, "reporter")

    assert first_response is not None
    assert first_response.isoformat() == "2026-01-02T00:00:00+00:00"


def test_with_per_page_preserves_existing_query_string() -> None:
    assert _with_per_page("https://api.github.com/issues?state=all", 30).endswith(
        "?state=all&per_page=30"
    )


def test_parse_link_header_extracts_next_url() -> None:
    links = _parse_link_header(
        '<https://api.github.com/repos/o/r/commits?page=2>; rel="next", '
        '<https://api.github.com/repos/o/r/commits?page=4>; rel="last"'
    )

    assert links["next"].endswith("page=2")
    assert links["last"].endswith("page=4")


def test_paginated_get_follows_next_until_max_pages() -> None:
    client = GitHubClient(token="token")
    calls: list[str] = []

    def request_json(url: str) -> _JsonResponse:
        calls.append(url)
        headers = Message()
        if len(calls) < 3:
            headers["Link"] = (
                f'<https://api.github.com/repos/o/r/commits?page={len(calls) + 1}>; '
                'rel="next"'
            )
        return _JsonResponse(payload=[{"page": len(calls)}], headers=headers)

    client._request_json = request_json  # type: ignore[method-assign]

    payload = client._get_url_paginated("https://api.github.com/repos/o/r/commits", max_pages=2)

    assert payload == [{"page": 1}, {"page": 2}]
    assert len(calls) == 2


def test_rate_limit_headers_are_recorded_as_lowest_remaining_budget() -> None:
    client = GitHubClient(token="token")
    first = Message()
    first["X-RateLimit-Limit"] = "5000"
    first["X-RateLimit-Remaining"] = "4999"
    first["X-RateLimit-Reset"] = "1767225600"
    second = Message()
    second["X-RateLimit-Limit"] = "5000"
    second["X-RateLimit-Remaining"] = "42"

    client._record_rate_limit(first)
    client._record_rate_limit(second)

    assert client._api_budget is not None
    assert client._api_budget.limit == 5000
    assert client._api_budget.remaining == 42
    assert client._api_budget.reset_at == "2026-01-01T00:00:00Z"


def test_package_manifest_detection_uses_known_root_files_only() -> None:
    manifests = _package_manifests_from_contents(_fixture("contents.json"))  # type: ignore[arg-type]

    assert [(manifest.path, manifest.ecosystem, manifest.package_manager) for manifest in manifests] == [
        ("pyproject.toml", "Python", None),
        ("package.json", "JavaScript", "npm"),
    ]


def test_metrics_are_extracted_from_github_api_fixtures() -> None:
    client = GitHubClient(
        token="token",
        clock=lambda: dt.datetime(2026, 6, 3, 12, tzinfo=dt.timezone.utc),
    )
    calls: list[str] = []

    def request_json(url: str) -> _JsonResponse:
        calls.append(url)
        headers = Message()
        headers["X-RateLimit-Limit"] = "5000"
        headers["X-RateLimit-Remaining"] = str(5000 - len(calls))
        headers["X-RateLimit-Reset"] = "1767225600"
        client._record_rate_limit(headers)

        parsed = urlparse(url)
        query = parse_qs(parsed.query)

        if parsed.path == "/repos/octo/widget":
            return _JsonResponse(payload=_fixture("repository.json"), headers=headers)
        if parsed.path == "/repos/octo/widget/commits":
            page = query.get("page", ["1"])[0]
            if page == "1":
                headers["Link"] = (
                    f"<{GITHUB_API}/repos/octo/widget/commits?per_page=30&page=2>; "
                    'rel="next"'
                )
                return _JsonResponse(payload=_fixture("commits_page_1.json"), headers=headers)
            return _JsonResponse(payload=_fixture("commits_page_2.json"), headers=headers)
        if parsed.path == "/repos/octo/widget/releases":
            return _JsonResponse(payload=_fixture("releases.json"), headers=headers)
        if parsed.path == "/repos/octo/widget/issues":
            return _JsonResponse(payload=_fixture("issues.json"), headers=headers)
        if parsed.path == "/repos/octo/widget/pulls":
            return _JsonResponse(payload=_fixture("pulls.json"), headers=headers)
        if parsed.path == "/repos/octo/widget/contents":
            assert query.get("ref") == ["main"]
            return _JsonResponse(payload=_fixture("contents.json"), headers=headers)
        if parsed.path == "/repos/octo/widget/issues/1/comments":
            return _JsonResponse(payload=_fixture("comments_issue_1.json"), headers=headers)
        if parsed.path == "/repos/octo/widget/issues/2/comments":
            return _JsonResponse(payload=_fixture("comments_issue_2.json"), headers=headers)

        raise AssertionError(f"unexpected URL: {url}")

    client._request_json = request_json  # type: ignore[method-assign]

    metrics = client.metrics("octo", "widget")

    assert metrics.owner == "octo"
    assert metrics.name == "widget"
    assert metrics.default_branch == "main"
    assert metrics.is_archived is False
    assert metrics.is_fork is False
    assert metrics.latest_commit_days == 2
    assert metrics.latest_release_days == 14
    assert metrics.median_issue_response_hours == 30
    assert metrics.oldest_open_pr_days == 40
    assert metrics.open_pr_count == 2
    assert metrics.bus_factor_estimate == 2
    assert [
        (manifest.path, manifest.ecosystem, manifest.package_manager)
        for manifest in metrics.package_manifests
    ] == [
        ("pyproject.toml", "Python", None),
        ("package.json", "JavaScript", "npm"),
    ]
    assert metrics.api_budget is not None
    assert metrics.api_budget.limit == 5000
    assert metrics.api_budget.remaining == 4991
    assert metrics.api_budget.reset_at == "2026-01-01T00:00:00Z"
