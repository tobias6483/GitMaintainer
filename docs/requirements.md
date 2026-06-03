# Requirements

## MVP Coverage

| Requirement | Status | Notes |
| --- | --- | --- |
| CLI accepts `github.com/user/repo` | Implemented | Also accepts `owner/repo` and HTTPS URLs. |
| Score: Active / Slow / Risky / Abandoned | Implemented | Explainable heuristic in `gitmaintainer.scoring`. |
| Last release | Implemented | Uses latest GitHub release. |
| Median issue response time | Implemented | Uses first non-author issue comment where available. |
| Open PR age | Implemented | Reports oldest open PR age. |
| Bus factor-ish estimate | Partial | Estimates how many recent commit authors account for 80% of sampled commits. |
| Badge generator for README | Implemented | Emits shields.io Markdown. |
| Default branch and archived/fork context | Implemented | Included in output and scoring. |
| Actionable API errors | Implemented | Rate-limit, auth, forbidden, and 404 errors are summarized. |

## Planned Improvements

- Add package manager metadata for dependency-oriented checks.
- Add pagination and rate-limit budget reporting for larger repositories.
- Add browser extension or web UI after CLI scoring stabilizes.
