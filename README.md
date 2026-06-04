# GitMaintainer

GitMaintainer answers a practical dependency question: is this GitHub repository still alive?

It inspects public GitHub activity and reports a maintenance status:

- **Active**: current releases, recent commits, responsive issues, and healthy PR flow
- **Slow**: maintained, but with slower response or release cadence
- **Risky**: notable stale signals
- **Abandoned**: little evidence of ongoing maintenance

## Status

GitMaintainer is an early CLI MVP. The scoring model is explainable by design and will change as signals improve.

## Install

GitMaintainer is preparing for its first pre-release. Until PyPI publication is
configured, install from a local checkout:

```sh
python -m pip install -e .
```

After PyPI publication:

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

Check the installed CLI version:

```sh
gitmaintainer --version
```

Set `GITHUB_TOKEN` to increase API limits:

```sh
GITHUB_TOKEN=ghp_... gitmaintainer pallets/flask
```

## Signals

GitMaintainer combines:

- repository metadata such as default branch, archived status, and fork status
- days since the latest commit
- days since the latest release
- median issue response time
- age of open pull requests
- recent commit author concentration as a bus-factor-ish estimate
- detected package manifest files and dependency counts where supported

The score is intentionally explainable and conservative. It should guide human review, not replace it.

GitMaintainer follows GitHub pagination for sampled activity endpoints with bounded page caps so CLI runs stay predictable. JSON output includes the observed GitHub API budget, and text output warns only when the remaining budget is low.

Dependency count parsing currently covers `package.json` and `requirements.txt`. Other supported manifests are reported as metadata without parsing their dependency lists yet.

## Privacy

GitMaintainer reads public GitHub API data and prints results locally. It does not store repository data, tokens, analytics, or telemetry. See `PRIVACY.md`.

## Documentation

- `docs/development.md`
- `docs/requirements.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/release.md`

## Development

```sh
python -m pytest
python -m gitmaintainer pallets/flask
```

## License

MIT
