from email.message import Message

from gitmaintainer.github import (
    GitHubClient,
    _JsonResponse,
    _bus_factor,
    _first_non_author_comment,
    _parse_link_header,
    _with_per_page,
)


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
