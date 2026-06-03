# Release Process

GitMaintainer is pre-release software.

## Release Checklist

1. Update `CHANGELOG.md`.
2. Run `python -m pytest`.
3. Run `python -m build`.
4. Run manual CLI QA from `docs/development.md`.
5. Confirm README install and usage instructions are current.
6. Tag the release.
7. Publish package artifacts when PyPI publication is ready.

## Packaging Status

The project has `pyproject.toml` metadata, console scripts, local package build verification, and a non-required CI package job. Automated PyPI publication is not configured yet.

## Security Gate

Before release, confirm token handling and network destinations still match `PRIVACY.md` and `SECURITY.md`.
