from gitmaintainer.github import _bus_factor, _first_non_author_comment, _with_per_page


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
