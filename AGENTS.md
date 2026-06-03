# Agent Instructions

Follow the global agent workflow for this repository.

## Project

GitMaintainer is a Python CLI. Keep runtime dependencies minimal and prefer stdlib for GitHub API access unless a feature clearly needs a dependency.

## Checks

Run before reporting done or committing:

```sh
python -m pytest
```

## GitHub

The default branch is `main`. This repository is intended to use pull requests before merging to `main`, with zero required approving reviews for solo-maintainer flow unless the maintainer changes that policy.

Required status checks on `main`:

- `test (3.10)`
- `test (3.11)`
- `test (3.12)`

Use squash merge for agent-created PRs and delete branches after merge.
