# Requirements

## MVP Coverage

| Requirement | Status | Notes |
| --- | --- | --- |
| CLI accepts `github.com/user/repo` | Implemented | Also accepts `owner/repo` and HTTPS URLs. |
| Score: Active / Slow / Risky / Abandoned | Implemented | Explainable heuristic in `gitmaintainer.scoring`. |
| Last release | Implemented | Uses latest GitHub release. |
| Median issue response time | Implemented | Uses first non-author issue comment where available. |
| Open PR age | Implemented | Reports oldest open PR age. |
| Bus factor-ish estimate | Partial | Uses contributor count from GitHub contributors endpoint. |
| Badge generator for README | Implemented | Emits shields.io Markdown. |

## Planned Improvements

- Detect default branch and archived/fork status as scoring context.
- Improve bus-factor estimate with recent commit authors.
- Add package manager metadata for dependency-oriented checks.
- Add browser extension or web UI after CLI scoring stabilizes.
