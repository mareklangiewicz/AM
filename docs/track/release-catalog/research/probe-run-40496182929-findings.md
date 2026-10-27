# First manual workflow-token probe

[Successful run](https://github.com/mareklangiewicz/AM/actions/runs/40496182929), manually dispatched once on 2026-10-27 from main-marek commit 4a2083e2a4ca921addfcfae2bacec59349f55b1c. Job 122162100581 completed successfully in 12 seconds. The job used github.token as GH_TOKEN with Contents read and Metadata read permissions; no personal access token was supplied.

## Measurements

| Request | HTTP status | Body bytes | Relevant measurement |
| --- | ---: | ---: | --- |
| Initial /rate_limit | 200 | 1,232 | core and GraphQL limits reported as 5,000; both used=0 |
| Obsidian release list | 200 | 450,991 | core used=1, remaining=4,999; ETag returned |
| Same list with If-None-Match | 304 | 0 | same ETag, core used=1 and remaining=4,999 |
| GraphQL batch for Obsidian and Neovim | 200 | 26,054 | cost=1, GraphQL used=1, remaining=4,999 |
| Final /rate_limit | 200 | 1,232 | core used=1; GraphQL unexpectedly reported used=0 |

Public upstream reads worked with the real workflow token. The conditional repeat was a genuine 304 with no increase in the reported core usage. GraphQL returned five releases from each repository with no errors. Both release connections reported hasNextPage=true; no returned release had a truncated fifty-asset connection.

## Interpretation and limits

This run reported 5,000/hour for each primary budget, above the 1,000/hour conservative planning baseline from documentation. Preserve this as a measured fact for this token/run, not a universal promise or an explanation of how GitHub assigns limits. A collector should use response headers and handle rate limits rather than hard-code this observation.

The final /rate_limit response's GraphQL usage disagreed with the GraphQL response's own headers and rateLimit object; their reset timestamps differed too. The direct GraphQL response consistently reported cost=1 and remaining=4,999. Do not infer zero GraphQL cost from the subsequent /rate_limit result. The cause was not investigated by additional requests.

The much smaller GraphQL body is not a like-for-like compression result: it requests fewer releases, selected fields, and different ordering semantics than the full REST response. This probe does not establish long-term ETag hit rate, compatibility of GraphQL with existing filters, full-catalog volume, polling capacity, or Git history growth. Those remain separate experiments.

Exactly one manual dispatch was submitted. All five unrelated workflows remain disabled; no automatic trigger or schedule was added. No catalog was published, no installation script ran, and no installed app was changed.

## Preserved evidence

The downloaded seventeen-file artifact includes public response bodies, status files, response headers, and the fixed GraphQL query; no request Authorization header is saved. GitHub artifact 12730930167 has seven-day retention. A local evidence archive and summary with body SHA-256 values are retained alongside this report, so the findings do not depend on that expiry.

Files: probe-run-40496182929-summary.json and probe-run-40496182929-evidence.tar.gz. The local archive is repackaged from extracted artifact files; it is not byte-identical to GitHub's uploaded ZIP.

Next useful step: compare storage/response churn for a small reviewed set under manually controlled repeat observations. The static inventory's approximately 348 requests/hour for one daily sweep remains a conservative arithmetic estimate; this single run does not prove production feasibility.
