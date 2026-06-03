# Contributing

Thanks for helping improve GitMaintainer.

## Development setup

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
```

## Pull requests

- Keep changes focused.
- Add or update tests for scoring, parsing, or output changes.
- Run `python -m pytest` before opening a pull request.
- Explain user-facing scoring changes clearly in the PR description.
- Use draft PRs while work is incomplete.
- Prefer squash merge after checks pass.

## Issues

Use the issue templates for bug reports, feature requests, documentation issues, and privacy/security review proposals.

Good bug reports include:

- the repository checked
- the exact command
- expected output
- actual output
- whether `GITHUB_TOKEN` was used, without sharing the token

## Maintainer notes

Scoring should stay explainable. Prefer small, auditable heuristics over opaque weighting.
