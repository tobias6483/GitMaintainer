from gitmaintainer.models import RepoMetrics
from gitmaintainer.scoring import score_repository


def test_scores_active_repository() -> None:
    metrics = RepoMetrics(
        owner="owner",
        name="repo",
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
