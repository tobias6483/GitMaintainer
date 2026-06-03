# GitMaintainer

GitMaintainer answers a practical dependency question: is this GitHub repository still alive?

It inspects public GitHub activity and reports a maintenance status:

- **Active**: current releases, recent commits, responsive issues, and healthy PR flow
- **Slow**: maintained, but with slower response or release cadence
- **Risky**: notable stale signals
- **Abandoned**: little evidence of ongoing maintenance

## Install

```sh
pipx install gitmaintainer
```

For local development:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Usage

```sh
gitmaintainer github.com/pallets/flask
```

Optional JSON output:

```sh
gitmaintainer https://github.com/pallets/flask --json
```

Generate a README badge:

```sh
gitmaintainer pallets/flask --badge
```

Set `GITHUB_TOKEN` to increase API limits:

```sh
GITHUB_TOKEN=ghp_... gitmaintainer pallets/flask
```

## Signals

GitMaintainer combines:

- days since the latest commit
- days since the latest release
- median issue response time
- age of open pull requests
- contributor concentration as a bus-factor-ish estimate

The score is intentionally explainable and conservative. It should guide human review, not replace it.

## Development

```sh
python -m pytest
python -m gitmaintainer pallets/flask
```

## License

MIT
