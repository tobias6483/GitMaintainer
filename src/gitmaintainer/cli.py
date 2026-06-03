from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .badge import badge_markdown
from .github import GitHubClient, GitHubError, parse_repo
from .models import ApiBudget, DependencySummary, PackageManifest, RepoMetrics
from .scoring import score_repository


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gitmaintainer",
        description="Estimate whether a GitHub repository is actively maintained.",
    )
    parser.add_argument("repository", help="Repository as owner/repo or github.com/owner/repo")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--badge", action="store_true", help="Print a shields.io badge snippet")
    parser.add_argument("--token", help="GitHub token. Defaults to GITHUB_TOKEN.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    try:
        owner, repo = parse_repo(args.repository)
        metrics = GitHubClient(token=args.token).metrics(owner, repo)
    except (GitHubError, ValueError) as error:
        print(f"gitmaintainer: {error}", file=sys.stderr)
        return 2

    result = score_repository(metrics)

    if args.badge:
        print(badge_markdown(owner, repo, result.status))
    elif args.json:
        print(
            json.dumps(
                {
                    "repository": f"{owner}/{repo}",
                    "status": result.status,
                    "score": result.score,
                    "metrics": _metrics_dict(metrics),
                    "api_budget": _api_budget_dict(metrics.api_budget),
                    "reasons": list(result.reasons),
                },
                indent=2,
            )
        )
    else:
        print(f"GitMaintainer: {owner}/{repo}")
        print(f"Status: {result.status} ({result.score}/100)")
        print(f"Default branch: {metrics.default_branch or 'unknown'}")
        print(f"Archived: {'yes' if metrics.is_archived else 'no'}")
        print(f"Fork: {'yes' if metrics.is_fork else 'no'}")
        print(f"Last commit: {_days(metrics.latest_commit_days)}")
        print(f"Last release: {_days(metrics.latest_release_days)}")
        print(f"Median issue response: {_hours(metrics.median_issue_response_hours)}")
        print(f"Open PRs: {metrics.open_pr_count}")
        print(f"Oldest open PR: {_days(metrics.oldest_open_pr_days)}")
        print(f"Bus factor-ish estimate: {metrics.bus_factor_estimate or 'unknown'}")
        print(f"Package manifests: {_package_manifests_text(metrics.package_manifests)}")
        warning = _api_budget_warning(metrics.api_budget)
        if warning:
            print(f"GitHub API budget: {warning}")
        print("Reasons:")
        for reason in result.reasons:
            print(f"- {reason}")

    return 0


def _metrics_dict(metrics: RepoMetrics) -> dict[str, object]:
    return {
        "default_branch": metrics.default_branch,
        "is_archived": metrics.is_archived,
        "is_fork": metrics.is_fork,
        "latest_commit_days": metrics.latest_commit_days,
        "latest_release_days": metrics.latest_release_days,
        "median_issue_response_hours": metrics.median_issue_response_hours,
        "oldest_open_pr_days": metrics.oldest_open_pr_days,
        "open_pr_count": metrics.open_pr_count,
        "bus_factor_estimate": metrics.bus_factor_estimate,
        "package_manifests": [
            {
                "path": manifest.path,
                "ecosystem": manifest.ecosystem,
                "package_manager": manifest.package_manager,
                "dependency_summary": _dependency_summary_dict(manifest.dependency_summary),
            }
            for manifest in metrics.package_manifests
        ],
    }


def _package_manifests_text(manifests: tuple[PackageManifest, ...]) -> str:
    if not manifests:
        return "none detected"
    return ", ".join(
        f"{manifest.path} ({manifest.package_manager or manifest.ecosystem}{_dependency_summary_text(manifest.dependency_summary)})"
        for manifest in manifests
    )


def _dependency_summary_dict(summary: DependencySummary | None) -> dict[str, object] | None:
    if summary is None:
        return None
    return {
        "parsed": summary.parsed,
        "dependency_count": summary.dependency_count,
        "dev_dependency_count": summary.dev_dependency_count,
        "optional_dependency_count": summary.optional_dependency_count,
        "note": summary.note,
    }


def _dependency_summary_text(summary: DependencySummary | None) -> str:
    if summary is None:
        return ""
    if not summary.parsed:
        return ", dependencies not parsed"
    return (
        f", deps {summary.dependency_count or 0}"
        f", dev {summary.dev_dependency_count or 0}"
        f", optional {summary.optional_dependency_count or 0}"
    )


def _api_budget_dict(api_budget: ApiBudget | None) -> dict[str, object] | None:
    if api_budget is None:
        return None
    return {
        "limit": api_budget.limit,
        "remaining": api_budget.remaining,
        "reset_at": api_budget.reset_at,
    }


def _api_budget_warning(api_budget: ApiBudget | None) -> str | None:
    if api_budget is None or api_budget.limit is None or api_budget.remaining is None:
        return None
    if api_budget.limit <= 0:
        return None
    if api_budget.remaining > 60 and api_budget.remaining / api_budget.limit > 0.1:
        return None

    reset = f"; resets at {api_budget.reset_at}" if api_budget.reset_at else ""
    return f"low ({api_budget.remaining}/{api_budget.limit} remaining{reset})"


def _days(value: int | None) -> str:
    if value is None:
        return "unknown"
    if value == 0:
        return "today"
    return f"{value} days ago"


def _hours(value: float | None) -> str:
    if value is None:
        return "unknown"
    if value < 48:
        return f"{value:.1f} hours"
    return f"{value / 24:.1f} days"
