# Release Process

GitMaintainer is pre-release software.

## Release Checklist

1. Update `CHANGELOG.md`.
2. Run `python -m pytest`.
3. Run manual CLI QA from `docs/development.md`.
4. Confirm README install and usage instructions are current.
5. Tag the release.
6. Publish package artifacts when packaging is ready.

## Packaging Status

The project has `pyproject.toml` metadata and console scripts, but no automated PyPI publication workflow yet.

## Security Gate

Before release, confirm token handling and network destinations still match `PRIVACY.md` and `SECURITY.md`.
