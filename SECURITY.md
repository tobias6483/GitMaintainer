# Security Policy

## Supported versions

GitMaintainer is pre-1.0. Security fixes will target the latest released version.

## Security principles

- Never log or print GitHub tokens.
- Send tokens only to GitHub API requests.
- Do not store repository data or credentials locally.
- Treat new network destinations, persistence, telemetry, or hosted services as security-sensitive changes.

## Reporting a vulnerability

Please report security issues privately by opening a GitHub security advisory or contacting the maintainer.

Do not include active tokens, private repository data, or other secrets in public issues.

## Out of scope

GitMaintainer cannot protect secrets already committed to repositories it analyzes. It only reads public maintenance metadata.
