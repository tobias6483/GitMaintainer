from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RepoMetrics:
    owner: str
    name: str
    latest_commit_days: int | None
    latest_release_days: int | None
    median_issue_response_hours: float | None
    oldest_open_pr_days: int | None
    open_pr_count: int
    bus_factor_estimate: int | None


@dataclass(frozen=True)
class ScoreResult:
    status: str
    score: int
    reasons: tuple[str, ...]
