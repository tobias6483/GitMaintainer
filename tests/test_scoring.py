from gitmaintainer.models import RepoMetrics
from gitmaintainer.scoring import score_repository


def test_scores_active_repository() -> None:
    metrics = RepoMetrics(
        owner="owner",
        name="repo",
        default_branch="main",
        is_archived=False,
        is_fork=False,
        latest_commit_days=5,
        latest_release_days=30,
        median_issue_response_hours=12,
        oldest_open_pr_days=14,
        open_pr_count=2,
        bus_factor_estimate=4,
    )

    result = score_repository(metrics)

    assert result.status == "Active"
    assert result.score >= 80


def test_scores_abandoned_repository() -> None:
    metrics = RepoMetrics(
        owner="owner",
        name="repo",
        default_branch="main",
        is_archived=False,
        is_fork=False,
        latest_commit_days=900,
        latest_release_days=1200,
        median_issue_response_hours=24 * 90,
        oldest_open_pr_days=365,
        open_pr_count=12,
        bus_factor_estimate=1,
    )

    result = score_repository(metrics)

    assert result.status == "Abandoned"
    assert result.score < 35


def test_active_repository_without_github_releases_is_not_risky_for_old_pr_backlog() -> None:
    metrics = RepoMetrics(
        owner="rust-lang",
        name="cargo",
        default_branch="master",
        is_archived=False,
        is_fork=False,
        latest_commit_days=0,
        latest_release_days=None,
        median_issue_response_hours=2,
        oldest_open_pr_days=1983,
        open_pr_count=60,
        bus_factor_estimate=3,
    )

    result = score_repository(metrics)

    assert result.status == "Active"
    assert result.score == 80
    assert "No GitHub releases found" in result.reasons
    assert "Oldest open PR is over 180 days old" in result.reasons


def test_archived_repository_is_risky_even_with_recent_activity() -> None:
    metrics = RepoMetrics(
        owner="owner",
        name="repo",
        default_branch="main",
        is_archived=True,
        is_fork=False,
        latest_commit_days=5,
        latest_release_days=30,
        median_issue_response_hours=12,
        oldest_open_pr_days=None,
        open_pr_count=0,
        bus_factor_estimate=3,
    )

    result = score_repository(metrics)

    assert result.status == "Risky"
    assert "Repository is archived" in result.reasons
