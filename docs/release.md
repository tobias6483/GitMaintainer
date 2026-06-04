# Release Process

GitMaintainer is pre-release software.

## Pre-Release Decision

The first release should be published as a GitHub pre-release with attached
source and wheel artifacts. PyPI publication is deferred until the maintainer
explicitly opts into package ownership and configures Trusted Publishing.

Do not upload to PyPI with an API token. Future PyPI publication should use
Trusted Publishing from GitHub Actions.

## Release Checklist

1. Update `CHANGELOG.md`.
2. Run `python -m pytest`.
3. Run `python -m build`.
4. Run manual CLI QA from `docs/development.md`.
5. Confirm README install and usage instructions are current.
6. Confirm `PRIVACY.md` and `SECURITY.md` still match implementation.
7. Tag the release.
8. Publish the GitHub pre-release with build artifacts.

## Manual GitHub Pre-Release Flow

Run this from a clean, up-to-date `main` after CI is green:

```sh
git switch main
git pull --ff-only
python -m pytest
python -m build
python -m gitmaintainer --version
git tag -a vX.Y.Z -m "GitMaintainer vX.Y.Z"
git push origin vX.Y.Z
gh release create vX.Y.Z dist/* \
  --title "GitMaintainer vX.Y.Z" \
  --notes-file docs/vX.Y.Z-release-notes.md \
  --prerelease
```

Verify the release page shows the pre-release marker, release notes, and both
distribution artifacts from `dist/`.

## Downloading Release Artifacts

GitMaintainer release artifacts are Python packages, not a macOS app bundle.
Download the source distribution and wheel from the GitHub release, then install
the wheel with an isolated tool runner:

```sh
pipx install gitmaintainer-X.Y.Z-py3-none-any.whl
gitmaintainer --version
```

If a release also publishes checksums, verify the downloaded files before
installing them:

```sh
shasum -a 256 -c SHA256SUMS
```

## Packaging Status

The project has `pyproject.toml` metadata, console scripts, local package build verification, and a non-required CI package job. Automated PyPI publication is not configured yet.

Package artifacts should be build-verified before attachment to a GitHub
pre-release. They are not uploaded to PyPI yet.

## Security Gate

Before release, confirm token handling and network destinations still match `PRIVACY.md` and `SECURITY.md`.
