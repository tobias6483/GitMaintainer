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

GitMaintainer publishes pre-release Python package artifacts on GitHub
Releases. Download the latest `.whl` file from the release page, then install
that local wheel:

```sh
python -m pip install gitmaintainer-X.Y.Z-py3-none-any.whl
```

The source archive is also attached for inspection or source-based installs.
Until PyPI publication is configured, a local editable install is supported:

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

Dependency count parsing currently covers `package.json`, `requirements.txt`,
`composer.json`, `go.mod`, and `Cargo.toml`. Other supported manifests are reported as
metadata without parsing their dependency lists yet.

## Privacy

GitMaintainer reads public GitHub API data and prints results locally. It does not store repository data, tokens, analytics, or telemetry. See `PRIVACY.md`.

## Documentation

- `docs/development.md`
- `docs/requirements.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/release.md`

## Development

Clone, build, and test from a fresh checkout:

```sh
git clone https://github.com/tobias6483/GitMaintainer.git
cd GitMaintainer
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
python -m build
```

Run the CLI locally:

```sh
python -m gitmaintainer pallets/flask
```

## Contributing

Contributions should follow the focused branch and pull request flow in
`CONTRIBUTING.md`. Run the documented checks before opening a PR, and call out
privacy, security, or packaging impact when a change touches tokens, network
access, persisted data, telemetry, hosted services, or release artifacts.

## License

MIT
