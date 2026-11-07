# Hourly metadata refresh rollout

Implementation for [146](../issues/146-roll-out-hourly-metadata-refresh.md),
following Marek's “go on” after [145's assessment](refresh-batch-sizing.md).
The profile is prepared locally; the operational receipt is appended after the
source push and exact-pin workflow verification.

## Prepared profile

- Hourly at minute 17 UTC, up to 500 oldest-attempt-first sources.
- 512 MiB charged response allowance, 900-second cooperative acquisition,
  30-minute workflow timeout. Serial requests, one page of 100 releases/source.
- Numeric primary quota headers and Retry-After diagnostics only; before a
  subsequent request, preserve 100 remaining primary requests until reset.
  HTTP 401/403/429 stops; no automatic retry or sleep. Redirects are refused
  before following them, preventing hidden extra requests/credential forwarding.
- Report requests, bytes, attempts/success/unattempted counts, explicit stop
  reason, acquisition/command time, quota endpoints and history consumption.
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
