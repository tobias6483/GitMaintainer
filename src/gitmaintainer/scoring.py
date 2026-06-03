from __future__ import annotations

from .models import RepoMetrics, ScoreResult


def score_repository(metrics: RepoMetrics) -> ScoreResult:
    score = 100
    reasons: list[str] = []

    if metrics.is_archived:
        score -= 60
        reasons.append("Repository is archived")

    if metrics.is_fork:
        score -= 5
        reasons.append("Repository is a fork")

    score -= _age_penalty(
        metrics.latest_commit_days,
        [(30, 0), (90, 10), (180, 25), (365, 45)],
        "No recent commits",
        reasons,
    )
    score -= _age_penalty(
        metrics.latest_release_days,
        [(90, 0), (180, 8), (365, 18), (730, 35)],
        "No recent releases",
        reasons,
    )

    if metrics.median_issue_response_hours is None:
        score -= 10
        reasons.append("Issue response time is unknown")
    elif metrics.median_issue_response_hours > 24 * 30:
        score -= 25
        reasons.append("Median issue response is over 30 days")
    elif metrics.median_issue_response_hours > 24 * 7:
        score -= 12
        reasons.append("Median issue response is over 7 days")

    if metrics.oldest_open_pr_days is not None:
        if metrics.oldest_open_pr_days > 180:
            score -= 20
            reasons.append("Oldest open PR is over 180 days old")
        elif metrics.oldest_open_pr_days > 60:
            score -= 10
            reasons.append("Oldest open PR is over 60 days old")

    if metrics.bus_factor_estimate is not None and metrics.bus_factor_estimate <= 1:
        score -= 10
        reasons.append("Recent commits appear concentrated in one maintainer")

    score = max(0, min(100, score))
    if score >= 80:
        status = "Active"
    elif score >= 60:
        status = "Slow"
    elif score >= 35:
        status = "Risky"
    else:
        status = "Abandoned"

    if not reasons:
        reasons.append("Maintenance signals look healthy")

    return ScoreResult(status=status, score=score, reasons=tuple(reasons))


def _age_penalty(
    days: int | None,
    thresholds: list[tuple[int, int]],
    unknown_reason: str,
    reasons: list[str],
) -> int:
    if days is None:
        reasons.append(unknown_reason)
        return thresholds[-1][1]

    penalty = 0
    for max_days, value in thresholds:
        if days <= max_days:
            penalty = value
            break
    else:
        penalty = thresholds[-1][1]

    if penalty:
        reasons.append(f"{unknown_reason}: {days} days")
    return penalty
