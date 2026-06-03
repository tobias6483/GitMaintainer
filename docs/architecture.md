# Architecture

GitMaintainer is a small Python CLI with no runtime dependencies.

## Modules

- `gitmaintainer.cli`: argument parsing, output modes, and exit codes
- `gitmaintainer.github`: GitHub API access and metric extraction
- `gitmaintainer.scoring`: maintenance score heuristic
- `gitmaintainer.badge`: shields.io badge generation
- `gitmaintainer.models`: typed result dataclasses

## Boundaries

GitHub API access is kept separate from scoring so metrics can later come from cached data, fixtures, a browser extension, or a hosted API.

Metric extraction tests use local GitHub API JSON fixtures to cover end-to-end mapping without live network access. Fixtures should stay small and focused on stable response fields used by the metric extractor.

GitHub pagination is bounded per endpoint to keep CLI runtime predictable. Commit sampling follows up to three pages, issue and open pull request sampling follow up to two pages, and issue comments stay capped to the first page for median response-time cost control.

Rate-limit headers are captured during API access and attached to metrics as API budget metadata. JSON output exposes the budget directly, while text output only warns when remaining requests are low.

Package manifest detection uses the GitHub Contents API for root-level files on the repository default branch. It records ecosystem/package-manager metadata only; dependency parsing is a future separation point.

Scoring is intentionally explainable. Avoid opaque models until the project has clear validation data and a documented evaluation process.

GitHub error handling should return actionable CLI messages. Avoid exposing raw API JSON unless a debug mode is added.

## Future Separation Points

- richer maintainer identity/contributor analysis beyond recent commit authors
- dependency parsing for supported package ecosystems
- web or browser extension frontend
