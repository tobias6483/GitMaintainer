# Contributing

Thanks for helping improve GitMaintainer.

## Development setup

```sh
git clone https://github.com/tobias6483/GitMaintainer.git
cd GitMaintainer
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
```

## Pull requests

- Fork the repository if you do not have push access.
- Create a focused branch for the change.
- Keep changes focused.
- Add or update tests for scoring, parsing, or output changes.
- Run `python -m pytest` before opening a pull request.
- Run `python -m build` for packaging, release, console script, or project
  metadata changes.
- Explain user-facing scoring changes clearly in the PR description.
- Explain privacy, security, or packaging impact when relevant.
- Use draft PRs while work is incomplete.
- Prefer squash merge after checks pass.

Required checks on `main` are:

- `test (3.10)`
- `test (3.11)`
- `test (3.12)`

The `package` check is expected for packaging and release-related changes.

## Privacy and security review

Request privacy or security review when a change affects token handling,
network destinations, local persistence, analytics or telemetry, hosted
services, release packaging, or artifact contents. Changes should preserve the
project's local-first posture and avoid storing GitHub tokens or repository
scan data unless the behavior is explicitly designed, documented, and reviewed.

## Issues

Use the issue templates for bug reports, feature requests, documentation issues, and privacy/security review proposals.

Good bug reports include:

- the repository checked
- the exact command
- expected output
- actual output
- whether `GITHUB_TOKEN` was used, without sharing the token

Use GitHub issues for bugs, support questions, and non-sensitive feature or
documentation requests. Report vulnerabilities privately using the process in
`SECURITY.md`; do not include secrets, tokens, or private repository data in a
public issue.

## Maintainer notes

Scoring should stay explainable. Prefer small, auditable heuristics over opaque weighting.
