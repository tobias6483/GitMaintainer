# Contributing

Thanks for helping improve GitMaintainer.

## Development Setup

```sh
git clone https://github.com/tobias6483/GitMaintainer.git
cd GitMaintainer
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
```

Build package artifacts when touching packaging, release behavior, project
metadata, or console scripts:

```sh
python -m build
```

## Fork, Branch, And Pull Request Flow

External contributors should use the standard GitHub fork workflow:

1. Fork the repository.
2. Clone your fork.
3. Create a focused branch for the change.
4. Run `python -m pytest`.
5. Push your branch.
6. Open a pull request against `tobias6483/GitMaintainer:main`.

Maintainers and project agents with write access should still work on a branch
and open a pull request before merging to `main`. Required checks are:

- `test (3.10)`
- `test (3.11)`
- `test (3.12)`

The `package` CI job is non-required, but release or packaging changes should
keep it passing. Prefer squash merge after checks pass.

## Pull Request Expectations

- Keep changes focused.
- Add or update tests for scoring, parsing, output, or package behavior changes.
- Explain user-facing scoring changes clearly in the PR description.
- Include the commands you ran, especially `python -m pytest`.
- Use draft PRs while work is incomplete.
- Call out privacy or security impact in the PR when relevant.

## Issues

Use the issue templates for bug reports, feature requests, documentation issues, and privacy/security review proposals.

Good bug reports include:

- the repository checked
- the exact command
- expected output
- actual output
- whether `GITHUB_TOKEN` was used, without sharing the token

Use [SUPPORT.md](SUPPORT.md) for support scope. Do not put active tokens,
private repository data, or other secrets in public issues.

## Privacy And Security Review

Treat changes as privacy- or security-sensitive when they affect:

- GitHub token handling
- new network destinations
- local persistence
- telemetry or analytics
- hosted services
- output that could expose private repository data
- release packaging or install instructions

Review those changes against [PRIVACY.md](PRIVACY.md) and
[SECURITY.md](SECURITY.md) before opening the pull request. Report
vulnerabilities privately as described in [SECURITY.md](SECURITY.md), not in a
public issue.

## Maintainer notes

Scoring should stay explainable. Prefer small, auditable heuristics over opaque weighting.
