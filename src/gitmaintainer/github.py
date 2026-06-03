from __future__ import annotations

import datetime as dt
import json
import os
from collections import Counter
from statistics import median
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .models import RepoMetrics

GITHUB_API = "https://api.github.com"


class GitHubError(RuntimeError):
    pass


def parse_repo(value: str) -> tuple[str, str]:
    cleaned = value.strip().removesuffix(".git").rstrip("/")
    if cleaned.startswith("https://github.com/"):
        cleaned = cleaned.removeprefix("https://github.com/")
    elif cleaned.startswith("http://github.com/"):
        cleaned = cleaned.removeprefix("http://github.com/")
    elif cleaned.startswith("github.com/"):
        cleaned = cleaned.removeprefix("github.com/")

    parts = cleaned.split("/")
    if len(parts) < 2 or not parts[0] or not parts[1]:
        raise ValueError("Repository must look like owner/repo or github.com/owner/repo")
    return parts[0], parts[1]


class GitHubClient:
    def __init__(self, token: str | None = None) -> None:
        self.token = token or os.environ.get("GITHUB_TOKEN")

    def metrics(self, owner: str, repo: str) -> RepoMetrics:
        now = dt.datetime.now(dt.timezone.utc)
        repo_path = f"/repos/{quote(owner)}/{quote(repo)}"

        commits = self._get(f"{repo_path}/commits?per_page=30")
        releases = self._get(f"{repo_path}/releases?per_page=1")
        issues = self._get(
            f"{repo_path}/issues?state=all&per_page=30&sort=created&direction=desc"
        )
        pulls = self._get(f"{repo_path}/pulls?state=open&per_page=30&sort=created&direction=asc")
        contributors = self._get(f"{repo_path}/contributors?per_page=20")

        latest_commit_days = _days_since(_latest_commit_at(commits), now)
        latest_release_days = _days_since(_latest_release_at(releases), now)
        issue_response = self._median_issue_response_hours(issues)
        oldest_pr_days = _oldest_pr_age_days(pulls, now)
        bus_factor = _bus_factor(contributors)

        return RepoMetrics(
            owner=owner,
            name=repo,
            latest_commit_days=latest_commit_days,
            latest_release_days=latest_release_days,
            median_issue_response_hours=issue_response,
            oldest_open_pr_days=oldest_pr_days,
            open_pr_count=len(pulls),
            bus_factor_estimate=bus_factor,
        )

    def _get(self, path: str) -> list[dict]:
        return self._get_url(f"{GITHUB_API}{path}")

    def _get_url(self, url: str) -> list[dict]:
        request = Request(url)
        request.add_header("Accept", "application/vnd.github+json")
        request.add_header("X-GitHub-Api-Version", "2022-11-28")
        if self.token:
            request.add_header("Authorization", f"Bearer {self.token}")

        try:
            with urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")
            raise GitHubError(f"GitHub API request failed: {error.code} {details}") from error

        if isinstance(payload, list):
            return payload
        raise GitHubError("GitHub API returned an unexpected response")

    def _median_issue_response_hours(self, issues: list[dict]) -> float | None:
        response_times: list[float] = []
        for issue in issues:
            if "pull_request" in issue or not issue.get("comments"):
                continue

            created = _parse_time(issue.get("created_at"))
            author = issue.get("user", {}).get("login")
            comments_url = issue.get("comments_url")
            if not created or not author or not comments_url:
                continue

            comments = self._get_url(f"{comments_url}?per_page=30")
            first_response = _first_non_author_comment(comments, author)
            if first_response:
                response_times.append((first_response - created).total_seconds() / 3600)

        if not response_times:
            return None
        return float(median(response_times))


def _latest_commit_at(commits: list[dict]) -> dt.datetime | None:
    if not commits:
        return None
    value = commits[0].get("commit", {}).get("committer", {}).get("date")
    return _parse_time(value)


def _latest_release_at(releases: list[dict]) -> dt.datetime | None:
    if not releases:
        return None
    value = releases[0].get("published_at") or releases[0].get("created_at")
    return _parse_time(value)


def _first_non_author_comment(comments: list[dict], author: str) -> dt.datetime | None:
    for comment in comments:
        commenter = comment.get("user", {}).get("login")
        if commenter and commenter != author:
            return _parse_time(comment.get("created_at"))
    return None


def _oldest_pr_age_days(pulls: list[dict], now: dt.datetime) -> int | None:
    if not pulls:
        return None
    created_values = [_parse_time(pr.get("created_at")) for pr in pulls]
    created_values = [value for value in created_values if value is not None]
    if not created_values:
        return None
    return _days_since(min(created_values), now)


def _bus_factor(contributors: list[dict]) -> int | None:
    if not contributors:
        return None
    counts = Counter(
        contributor.get("login")
        for contributor in contributors
        if contributor.get("login") and contributor.get("contributions")
    )
    return len(counts) or None


def _days_since(value: dt.datetime | None, now: dt.datetime) -> int | None:
    if value is None:
        return None
    return max(0, (now - value).days)


def _parse_time(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
