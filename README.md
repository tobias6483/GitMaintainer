# GitMaintainer

GitMaintainer answers a practical dependency question: is this GitHub repository still alive?

It inspects public GitHub activity and reports a maintenance status:

- **Active**: current releases, recent commits, responsive issues, and healthy PR flow
- **Slow**: maintained, but with slower response or release cadence
- **Risky**: notable stale signals
- **Abandoned**: little evidence of ongoing maintenance

## Status

GitMaintainer is an early CLI MVP. The scoring model is explainable by design and will change as signals improve.

## Download And Install

GitMaintainer is preparing for its first pre-release. Until PyPI publication is
configured, install from a local checkout:

```sh
python -m pip install -e .
```

When GitHub pre-release artifacts are published, download the source
distribution and wheel from the release page. Install the wheel in an isolated
tool environment:

```sh
pipx install gitmaintainer-0.1.1-py3-none-any.whl
```

After PyPI publication:

```sh
pipx install gitmaintainer
```

## Clone, Build, And Test

Clone the repository and create a local development environment:

```sh
git clone https://github.com/tobias6483/GitMaintainer.git
cd GitMaintainer
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run the test suite:

```sh
python -m pytest
```

Build local package artifacts:

```sh
python -m build
```

Run the CLI from the checkout:

```sh
python -m gitmaintainer pallets/flask
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

## Contribution Flow

Contributions should use the normal fork-based GitHub pull request flow:

1. Fork the repository.
2. Clone your fork.
3. Create a focused branch.
4. Build and test locally with `python -m pytest`.
5. Open a pull request against `tobias6483/GitMaintainer:main`.

Maintainers and project agents with write access should still use a branch and
pull request. Required checks are listed in [AGENTS.md](AGENTS.md), and release
or packaging changes should also run `python -m build`.

Use GitHub issues for bugs, support, feature requests, and documentation gaps.
Report security-sensitive issues privately as described in [SECURITY.md](SECURITY.md).
Changes that add tokens, persistence, telemetry, hosted services, or new network
destinations need privacy and security review against [PRIVACY.md](PRIVACY.md)
and [SECURITY.md](SECURITY.md).

See [CONTRIBUTING.md](CONTRIBUTING.md) for contributor expectations.

## License

MIT
