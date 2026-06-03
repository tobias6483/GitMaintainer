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

Scoring is intentionally explainable. Avoid opaque models until the project has clear validation data and a documented evaluation process.

GitHub error handling should return actionable CLI messages. Avoid exposing raw API JSON unless a debug mode is added.

## Future Separation Points

- API pagination and rate-limit handling
- richer maintainer identity/contributor analysis beyond recent commit authors
- package ecosystem integrations
- web or browser extension frontend
