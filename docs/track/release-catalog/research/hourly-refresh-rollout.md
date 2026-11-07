# Hourly metadata refresh rollout

Implementation for [146](../issues/146-roll-out-hourly-metadata-refresh.md),
following Marek's “go on” after [145's assessment](refresh-batch-sizing.md).
The profile is pushed and its first full enrolled-scope manual run is verified.
Actual enrollment remains 224; the ceiling and hourly schedule are now active.

## Prepared profile

- Hourly at minute 17 UTC, up to 500 oldest-attempt-first sources.
- 512 MiB charged response allowance, 900-second cooperative acquisition,
  30-minute workflow timeout. Serial requests, one page of 100 releases/source.
- Numeric primary quota headers and Retry-After diagnostics only; before a
  subsequent request, preserve 100 remaining primary requests until reset.
  HTTP 401/403/429 stops; no automatic retry or sleep. Redirects are refused
  before following them, preventing hidden extra requests/credential forwarding.
- Report requests, bytes, attempts/success/unattempted counts, explicit stop
  reason, acquisition/command time, first/last quota observations and history usage.
- Report source-success ages at 24/36/48 hours and never-successful sources;
  emit a CI warning from 24 hours. These are source diagnostics, not permission
  to refresh retained observations outside page 1 or change client selection.
- Bounded 256 MiB local history allowance and 500-source enrollment ceiling.
  Actual enrollment remains **228 apps / 224 verified sources**. New source
  identities still require verification and cohort-specific capacity evidence.
  The 2 MiB/document and 1,024-file reader limits remain.

## Local evidence

The actual maintained main command with the new request/transport/time/history
profile passes on the exact published 224-source parent
`26d82aa94bb5a8f70449e42500dc78a597583ab3`: 224 successes, zero pending apps,
179,239,534 saved response bytes, 150.28 seconds, 284,912 KiB peak process RSS
under a 1 GiB address-space limit. Offline evidence makes zero HTTP requests and
uses explicit synthetic receipt times, rather than claiming live reobservation.
This run precedes the final diagnostic-only additions; final focused main-command
and live workflow checks cover their final implementation.

Two real exact-parent publications with the measured 500-source tree and
published history present pass the new history guard. Existing object bytes
66,369,871 plus snapshot bytes 74,963,368 total 141,333,239; second publication
141,333,408. Both remain below 268,435,456 bytes, with the exact tree preserved.
This is an offline synthetic capacity test, not real 500-source identity review.
The earlier full 500-source normalization/read/retention evidence remains in 145.

The 256 MiB allowance provides intermediate growth headroom; it is not unbounded
history support. No history is pruned, rewritten or force-reset. Thousands of
source documents still require storage/read design and measured enrollment.

Raw controllers, command logs and receipts are preserved under
`/home/marek/Documents/Codex/am-hourly-profile-20261107/`.

## Validation and operation

Final focused checks pass: 21 transport/publication tests, 13 final batch tests,
11 enrollment/source checks and the updated whole-main 500-ceiling test.
[Portable local validation](hourly-refresh-validation.json) binds source hashes,
receipts and logs. The complete final collector run passes all 159 tests; the superseded
pre-fix run is retained in the raw evidence. Live workflow verification follows
the source push. No recipe migration,
installed file refresh, app update, website rebuild or yadm pointer operation is
part of this rollout. The 48-hour selected-release observation check is unchanged.


## Published operation

Source `09ae7fe81355a06eabe1c2afc141f22e2d3de675` is pushed to `main-marek`.
[Run 42366263140](https://github.com/mareklangiewicz/AM/actions/runs/42366263140)
succeeds in a 226-second job. Its maintained command takes 205.27 seconds,
including 166.55 seconds acquisition/normalization. All **224 sources succeed in
one batch**, zero failures, zero unattempted, 228 app identities, 179,326,726 charged
response bytes. Stop reason is `complete`. Source-success age counts at 24/36/48
hours and never-successful counts are all zero.

Published pin `59b3f3f398bc1013c7b5caf0f37b19a4f3fc9821` is a direct child of
its actual fetched parent `e992cc2ca3b22c01f2e95e61c404121cbcdbf188`, rather than
an old rehearsal pin. Both exact pins pass maintained bounded distributed-reader,
canonical and cross-file validation in an isolated catalog repository. App/source
identities, retained release IDs and effective observations are preserved. Final
YAML totals 33,220,878 bytes, largest 1,159,110. Actual pre-publication history
objects are 55,410,163 bytes; the guard total is 88,631,041 of 268,435,456 bytes.
Post-publication objects total 61,614,225 bytes.
[Portable live receipt](hourly-refresh-publication.json) binds exact parents,
per-source identity/last-success/document hashes, metrics, timings and raw log digest.

### Observed quota versus documented allowance

Live response headers report core `limit=5000`, initially `used=53` /
`remaining=4947`, finally `used=148` / `remaining=4852`. Reset values change
from `1794049288` (11:01:28 UTC) to `1794052889` (12:01:29 UTC) during the run.
Do not subtract endpoint counters to count this run: 224 request attempts and
224 successful release responses are independently recorded; quota windows and
other consumers can affect the shared counters.

The source passes `github.token` as `GH_TOKEN`. Official documentation and its
[first-party source text](https://github.com/github/docs/blob/main/data/reusables/rest-api/primary-rate-limit-github-token-in-actions.md)
still specify 1,000/hour/repository for ordinary `GITHUB_TOKEN` and 15,000 for
the documented Enterprise-resource exception. No official explanation was found
for this run's 5,000 response allowance; do not infer a PAT, cache exemption or
durable entitlement. Keep the conservative **1,000/hour planning baseline**, while
using actual response headers to preserve the 100-request reserve. GitHub notes
that regional processing can affect counters, but that does not explain this
allowance difference.
[Official REST limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).

The workflow is active, on the checked default branch `main-marek`; committed
cron is `17 * * * *`. Its first natural hourly trigger has not been observed;
the accepted operation above is a manual full-scope run. Cron remains best effort.
This does not claim live qualification of 500 unique upstream sources: only 224
are enrolled; the 500 ceiling has local synthetic and history-capacity evidence.
Further identity enrollment and cohort-specific density/capacity gates remain.

The 48-hour selected-release rule and page-scope observations are unchanged.
No recipe migration, installed-host refresh, app install/update, website rebuild
or yadm pointer bump occurs. Broader storage/attribution work remains with 138.
