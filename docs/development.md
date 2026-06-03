# Development

## Requirements

- Python 3.10 or newer
- Git

## Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Run

```sh
python -m gitmaintainer pallets/flask
python -m gitmaintainer pallets/flask --json
python -m gitmaintainer pallets/flask --badge
```

Set `GITHUB_TOKEN` for higher GitHub API limits.

## Test

```sh
python -m pytest
```

GitHub metric extraction tests use local JSON fixtures under `tests/fixtures/github/`.
Keep fixtures small, representative, and free of tokens or private repository data.

## Build

```sh
python -m build
```

The build command creates source and wheel artifacts in `dist/`, which is ignored locally.

## Manual QA

- Check invalid input returns exit code `2`.
- Check JSON output is valid.
- Check badge output is Markdown.
- Check at least one popular public repository through the live GitHub API.
- Check a missing repository returns an actionable 404 message.
