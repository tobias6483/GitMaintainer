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

## Maintainer notes

Scoring should stay explainable. Prefer small, auditable heuristics over opaque weighting.
