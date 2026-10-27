# First REST churn baseline — incomplete

Exactly one authorized manual dispatch: [run 40499617203](https://github.com/mareklangiewicz/AM/actions/runs/40499617203), source 6f9648bb2800c57e8455c22542075851a0fecc27. Created 2026-10-27 11:54:13 UTC (12:54:13 Europe/Warsaw); observation began 11:54:22.610811 UTC. The job failed after 12 seconds. No retry or subsequent observation was dispatched.

Before dispatch, repository Actions was enabled; Catalog quota probe was the only active workflow, the five unrelated workflows were disabled, and queued/in-progress/waiting run counts were zero.

## Observations

| Endpoint | Status | Saved body bytes | Releases | Assets |
| --- | ---: | ---: | ---: | ---: |
| Obsidian list | 200 | 450,991 | 30 | 269 |
| Obsidian latest | 200 | 13,889 | 1 | 8 |
| Neovim list | 200 | 822,241 | 30 | 376 |
| Neovim latest | 200 | 24,510 | 1 | 12 |
| WezTerm list?per_page=100 | 301 | not saved | — | — |
| sqlitebrowser list?per_page=100 | not attempted | — | — | — |

The fifth request returned HTTP 301. The no-redirect policy stopped the round as intended, leaving complete=false. Its 220-byte response was counted but not saved by the current failure path; Location is not in the current response-header allowlist. Thus the destination and reason for the redirect are not established by this artifact. Do not infer a particular renamed owner/repository or retry with a guessed URL.

All four saved body SHA-256 values match their observation manifest. Quota headers reported limit=5,000 and ample remaining requests, but counters/reset timestamps differed across responses; this is not a consistent baseline for attributing total quota usage. No GraphQL, extra page, binary, or installer requests were made.

The comparison step did not run because collection failed. No storage/churn or annual-growth conclusion follows. This partial run must not be used as previous_run for churn-hour. Record any changed endpoint/redirect policy explicitly, preserve the failure evidence, and obtain separate authorization for a replacement baseline. A useful preparation improvement is retaining a bounded public error body and Location header while keeping redirect following disabled.

## Persistent evidence

Artifact 12732440434, uploaded as catalog-quota-probe-40499617203, has seven-day retention and reported digest sha256:c6a224b22eabbe1b74889fdde528cd87d605f808305b44c4edbc8836d0951c8b.

Local repackaged archive: churn-baseline-40499617203-evidence.tar.gz, 93,622 bytes, SHA-256 ca1198d99353b54a4cfa766aa23b3b87f1314ad84a47e3f53a5d29c4ea3c003d. This is not byte-identical to GitHub's artifact ZIP. The adjacent summary JSON includes the complete observation manifest and artifact identifiers. No request authorization header is saved.
