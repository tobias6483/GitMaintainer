from __future__ import annotations

import datetime as dt
import json
import os
from collections import Counter
from dataclasses import dataclass
from email.message import Message
from statistics import median
from typing import Callable
from urllib.error import HTTPError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

from .models import ApiBudget, DependencySummary, PackageManifest, RepoMetrics

GITHUB_API = "https://api.github.com"
PACKAGE_MANIFESTS = {
    "package.json": ("JavaScript", "npm"),
    "pnpm-lock.yaml": ("JavaScript", "pnpm"),
    "yarn.lock": ("JavaScript", "Yarn"),
    "pyproject.toml": ("Python", None),
    "requirements.txt": ("Python", "pip"),
    "Pipfile": ("Python", "Pipenv"),
    "poetry.lock": ("Python", "Poetry"),
    "Cargo.toml": ("Rust", "Cargo"),
    "go.mod": ("Go", "Go modules"),
    "Gemfile": ("Ruby", "Bundler"),
    "composer.json": ("PHP", "Composer"),
    "pom.xml": ("Java", "Maven"),
    "build.gradle": ("Java", "Gradle"),
    "build.gradle.kts": ("Java", "Gradle"),
    "mix.exs": ("Elixir", "Mix"),
    "Package.swift": ("Swift", "Swift Package Manager"),
    "pubspec.yaml": ("Dart", "pub"),
    "packages.config": (".NET", "NuGet"),
}


class GitHubError(RuntimeError):
    pass


@dataclass(frozen=True)
class _JsonResponse:
    payload: object
    headers: Message


def parse_repo(value: str) -> tuple[str, str]:
    cleaned = value.strip().removesuffix(".git").rstrip("/")
    if cleaned.startswith("git@github.com:"):
        cleaned = cleaned.removeprefix("git@github.com:")
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
    def __init__(
        self,
        token: str | None = None,
        clock: Callable[[], dt.datetime] | None = None,
    ) -> None:
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self._clock = clock or (lambda: dt.datetime.now(dt.timezone.utc))
        self._api_budget: ApiBudget | None = None

    def metrics(self, owner: str, repo: str) -> RepoMetrics:
        now = self._clock()
        repo_path = f"/repos/{quote(owner)}/{quote(repo)}"

        repository = self._get_object(repo_path)
        default_branch = repository.get("default_branch")
        commits = self._get_paginated(f"{repo_path}/commits?per_page=30", max_pages=3)
        releases = self._get(f"{repo_path}/releases?per_page=1")
        issues = self._get_paginated(
            f"{repo_path}/issues?state=all&per_page=30&sort=created&direction=desc",
            max_pages=2,
        )
        pulls = self._get_paginated(
            f"{repo_path}/pulls?state=open&per_page=30&sort=created&direction=asc",
            max_pages=2,
        )

        latest_commit_days = _days_since(_latest_commit_at(commits), now)
        latest_release_days = _days_since(_latest_release_at(releases), now)
        issue_response = self._median_issue_response_hours(issues)
        oldest_pr_days = _oldest_pr_age_days(pulls, now)
        bus_factor = _bus_factor(commits)
        package_manifests = self._package_manifests(repo_path, default_branch)

        return RepoMetrics(
            owner=owner,
            name=repo,
            default_branch=default_branch,
            is_archived=bool(repository.get("archived")),
            is_fork=bool(repository.get("fork")),
            latest_commit_days=latest_commit_days,
            latest_release_days=latest_release_days,
            median_issue_response_hours=issue_response,
            oldest_open_pr_days=oldest_pr_days,
            open_pr_count=len(pulls),
            bus_factor_estimate=bus_factor,
            package_manifests=package_manifests,
            api_budget=self._api_budget,
        )

    def _get(self, path: str) -> list[dict]:
        return self._get_url(f"{GITHUB_API}{path}")

    def _get_paginated(self, path: str, max_pages: int) -> list[dict]:
        return self._get_url_paginated(f"{GITHUB_API}{path}", max_pages=max_pages)

    def _get_object(self, path: str) -> dict:
        payload = self._get_json(f"{GITHUB_API}{path}")
        if isinstance(payload, dict):
            return payload
        raise GitHubError("GitHub API returned an unexpected response")

    def _get_url(self, url: str) -> list[dict]:
        payload = self._get_json(url)
        if isinstance(payload, list):
            return payload
        raise GitHubError("GitHub API returned an unexpected response")

    def _get_url_paginated(self, url: str, max_pages: int) -> list[dict]:
        if max_pages < 1:
            raise ValueError("max_pages must be at least 1")

        items: list[dict] = []
        next_url: str | None = url
        pages = 0
        while next_url and pages < max_pages:
            response = self._request_json(next_url)
            if not isinstance(response.payload, list):
                raise GitHubError("GitHub API returned an unexpected response")
            items.extend(response.payload)
            pages += 1
            next_url = _next_link(response.headers.get("Link"))
        return items

    def _get_json(self, url: str) -> object:
        return self._request_json(url).payload

    def _request_json(self, url: str) -> _JsonResponse:
        request = Request(url)
        request.add_header("Accept", "application/vnd.github+json")
        request.add_header("X-GitHub-Api-Version", "2022-11-28")
        if self.token:
            request.add_header("Authorization", f"Bearer {self.token}")

        try:
            with urlopen(request, timeout=20) as response:
                headers = response.headers
                self._record_rate_limit(headers)
                payload = json.loads(response.read().decode("utf-8"))
                return _JsonResponse(payload=payload, headers=headers)
        except HTTPError as error:
            raise GitHubError(_http_error_message(error, url)) from error

    def _get_text_url(self, url: str) -> str:
        request = Request(url)
        if self.token and url.startswith(GITHUB_API):
            request.add_header("Authorization", f"Bearer {self.token}")

        try:
            with urlopen(request, timeout=20) as response:
                return response.read().decode("utf-8")
        except HTTPError as error:
            raise GitHubError(_http_error_message(error, url)) from error

    def _record_rate_limit(self, headers: Message) -> None:
        limit = _parse_int(headers.get("X-RateLimit-Limit"))
        remaining = _parse_int(headers.get("X-RateLimit-Remaining"))
        reset_at = _reset_at(headers.get("X-RateLimit-Reset"))

        if limit is None and remaining is None and reset_at is None:
            return

        if self._api_budget is None:
            self._api_budget = ApiBudget(limit=limit, remaining=remaining, reset_at=reset_at)
            return

        current = self._api_budget
        lowest_remaining = _min_known(current.remaining, remaining)
        self._api_budget = ApiBudget(
            limit=limit if limit is not None else current.limit,
            remaining=lowest_remaining,
            reset_at=reset_at or current.reset_at,
        )

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

            comments = self._get_url(_with_per_page(comments_url, 30))
            first_response = _first_non_author_comment(comments, author)
            if first_response:
                response_times.append((first_response - created).total_seconds() / 3600)

        if not response_times:
            return None
        return float(median(response_times))

    def _package_manifests(
        self,
        repo_path: str,
        default_branch: object,
    ) -> tuple[PackageManifest, ...]:
        path = f"{repo_path}/contents"
        if isinstance(default_branch, str) and default_branch:
            path = f"{path}?ref={quote(default_branch, safe='')}"

        try:
            contents = self._get(path)
        except GitHubError as error:
            if "not found" in str(error).lower():
                return ()
            raise

        return _package_manifests_from_contents(contents, fetch_text=self._get_text_url)


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


def _bus_factor(commits: list[dict]) -> int | None:
    if not commits:
        return None

    counts = Counter(author for author in (_commit_author(commit) for commit in commits) if author)
    if not counts:
        return None

    total = sum(counts.values())
    covered = 0
    for index, count in enumerate(sorted(counts.values(), reverse=True), start=1):
        covered += count
        if covered / total >= 0.8:
            return index
    return len(counts)


def _commit_author(commit: dict) -> str | None:
    author = commit.get("author") or {}
    login = author.get("login")
    if login:
        return login
    return commit.get("commit", {}).get("author", {}).get("email")


def _package_manifests_from_contents(
    contents: list[dict],
    fetch_text: Callable[[str], str] | None = None,
) -> tuple[PackageManifest, ...]:
    manifests: list[PackageManifest] = []
    for item in contents:
        if item.get("type") != "file":
            continue
        name = item.get("name")
        path = item.get("path")
        if not isinstance(name, str) or not isinstance(path, str):
            continue

        metadata = PACKAGE_MANIFESTS.get(name)
        if metadata is None:
            continue
        ecosystem, package_manager = metadata
        dependency_summary = _dependency_summary(name, item, fetch_text)
        manifests.append(
            PackageManifest(
                path=path,
                ecosystem=ecosystem,
                package_manager=package_manager,
                dependency_summary=dependency_summary,
            )
        )
    return tuple(manifests)


def _dependency_summary(
    name: str,
    item: dict,
    fetch_text: Callable[[str], str] | None,
) -> DependencySummary | None:
    if name not in {"package.json", "requirements.txt", "composer.json", "go.mod"}:
        return DependencySummary(parsed=False, note="Dependency parsing is not supported yet")
    if fetch_text is None:
        return None

    download_url = item.get("download_url")
    if not isinstance(download_url, str) or not download_url:
        return DependencySummary(parsed=False, note="Dependency file content is unavailable")

    try:
        text = fetch_text(download_url)
    except GitHubError:
        return DependencySummary(parsed=False, note="Dependency file could not be fetched")

    if name == "package.json":
        return _package_json_dependency_summary(text)
    if name == "requirements.txt":
        return _requirements_dependency_summary(text)
    if name == "composer.json":
        return _composer_json_dependency_summary(text)
    return _go_mod_dependency_summary(text)


def _package_json_dependency_summary(text: str) -> DependencySummary:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return DependencySummary(parsed=False, note="package.json is invalid JSON")

    if not isinstance(payload, dict):
        return DependencySummary(parsed=False, note="package.json root is not an object")

    return DependencySummary(
        parsed=True,
        dependency_count=_dependency_object_size(payload.get("dependencies")),
        dev_dependency_count=_dependency_object_size(payload.get("devDependencies")),
        optional_dependency_count=_dependency_object_size(payload.get("optionalDependencies")),
    )


def _dependency_object_size(value: object) -> int:
    if isinstance(value, dict):
        return len(value)
    return 0


def _requirements_dependency_summary(text: str) -> DependencySummary:
    dependency_count = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith(("-", "http://", "https://", "git+")):
            continue
        dependency_count += 1

    return DependencySummary(
        parsed=True,
        dependency_count=dependency_count,
        dev_dependency_count=0,
        optional_dependency_count=0,
    )


def _composer_json_dependency_summary(text: str) -> DependencySummary:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return DependencySummary(parsed=False, note="composer.json is invalid JSON")

    if not isinstance(payload, dict):
        return DependencySummary(parsed=False, note="composer.json root is not an object")

    return DependencySummary(
        parsed=True,
        dependency_count=_composer_dependency_count(payload.get("require")),
        dev_dependency_count=_dependency_object_size(payload.get("require-dev")),
        optional_dependency_count=0,
    )


def _composer_dependency_count(value: object) -> int:
    if not isinstance(value, dict):
        return 0
    return sum(
        1
        for name in value
        if isinstance(name, str) and name != "php" and not name.startswith("ext-")
    )


def _go_mod_dependency_summary(text: str) -> DependencySummary:
    return DependencySummary(
        parsed=True,
        dependency_count=_go_mod_require_count(text),
        dev_dependency_count=0,
        optional_dependency_count=0,
    )


def _go_mod_require_count(text: str) -> int:
    dependency_count = 0
    in_require_block = False

    for raw_line in text.splitlines():
        line = raw_line.split("//", 1)[0].strip()
        if not line:
            continue

        if in_require_block:
            if line == ")":
                in_require_block = False
                continue
            if line:
                dependency_count += 1
            continue

        if line == "require (":
            in_require_block = True
            continue
        if line.startswith("require "):
            dependency_count += 1

    return dependency_count


def _days_since(value: dt.datetime | None, now: dt.datetime) -> int | None:
    if value is None:
        return None
    return max(0, (now - value).days)


def _parse_time(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def _with_per_page(url: str, per_page: int) -> str:
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}per_page={per_page}"


def _next_link(value: str | None) -> str | None:
    links = _parse_link_header(value)
    return links.get("next")


def _parse_link_header(value: str | None) -> dict[str, str]:
    if not value:
        return {}

    links: dict[str, str] = {}
    for part in value.split(","):
        section = part.strip()
        if not section.startswith("<") or ">;" not in section:
            continue

        url, params = section[1:].split(">;", 1)
        rel = None
        for param in params.split(";"):
            key, _, raw = param.strip().partition("=")
            if key == "rel":
                rel = raw.strip('"')
                break
        if rel:
            links[rel] = url
    return links


def _parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _reset_at(value: str | None) -> str | None:
    timestamp = _parse_int(value)
    if timestamp is None:
        return None
    reset = dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc)
    return reset.isoformat().replace("+00:00", "Z")


def _min_known(current: int | None, candidate: int | None) -> int | None:
    if current is None:
        return candidate
    if candidate is None:
        return current
    return min(current, candidate)


def _http_error_message(error: HTTPError, url: str) -> str:
    body = error.read().decode("utf-8", errors="replace")
    message = _github_message(body)
    path = urlparse(url).path

    if error.code == 404:
        return f"Repository or endpoint not found: {path}"
    if error.code in {401, 403} and "rate limit" in message.lower():
        return "GitHub API rate limit exceeded. Set GITHUB_TOKEN or pass --token."
    if error.code == 401:
        return "GitHub API authentication failed. Check GITHUB_TOKEN or --token."
    if error.code == 403:
        return f"GitHub API request forbidden: {message or path}"
    return f"GitHub API request failed ({error.code}): {message or path}"


def _github_message(body: str) -> str:
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return body.strip()

    if isinstance(payload, dict):
        message = payload.get("message")
        if isinstance(message, str):
            return message
    return body.strip()
