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
| Bounded API pagination | Implemented | Samples multiple pages for commits, issues, and open PRs without unbounded CLI runtime. |
| Rate-limit budget reporting | Implemented | JSON includes the observed GitHub API budget; text output warns when remaining budget is low. |
| GitHub API fixture coverage | Implemented | Metric extraction has deterministic fixture coverage for core repository, activity, response, PR, pagination, and budget signals. |
| Package manifest metadata | Implemented | Detects known root package manifests such as `pyproject.toml`, `package.json`, `go.mod`, and `Cargo.toml`. |
| Dependency count summaries | Partial | Parses counts for `package.json` and `requirements.txt`; other manifests are reported without dependency parsing. |

## Planned Improvements

- Add dependency-file parsing for more package ecosystems.
- Add browser extension or web UI after CLI scoring stabilizes.
