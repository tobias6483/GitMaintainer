# Privacy

GitMaintainer is designed to be privacy-light.

## Data handled

The CLI reads public GitHub repository metadata through the GitHub API:

- commits
- releases
- issues and issue comments
- open pull requests
- contributor counts

When `GITHUB_TOKEN` or `--token` is used, the token is sent only to GitHub as an API authorization header.

## Data storage

GitMaintainer does not store repository data, tokens, analytics, or telemetry. Results are printed to stdout.

## Network access

GitMaintainer currently contacts only `api.github.com`.

## Future changes

Any future telemetry, persistence, hosted service, browser extension, or third-party API integration must be opt-in and documented before release.
