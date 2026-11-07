# Choose truthful health summaries and bounded statistics

Type: grilling
Label: wayfinder:grilling
Status: open
Blocked by: 01, 03, 04

## Question

Which public run-summary fields, measurements and bounded historical aggregates
explain health without misleading users or creating a second operational system?

Define successful/failed/unattempted/deferred counts and denominators, source-age
buckets separately from individual release freshness, attempts/redirect accounting,
charged versus received bytes, acquisition versus command/job duration, configured
limits, quota observations, snapshot/history growth and meaningful remaining work.
Identify unavailable measurements rather than reporting invented zeroes.

Specify run identity, timestamps, stop/failure taxonomy, partial success, aborts
without finalization, last reported run versus last publication, history gaps, retention
and aggregate bounds. Show safe examples for success, budget stop, failed validation,
failed publication and abrupt interruption.
Use the consistency model from the contract ticket; do not invent another schema
or strengthen timestamps. Allowlist sanitized public fields, not environment/header
dumps. Decide the few useful initial charts with Marek, measurement definitions
and drill-down links. Feed these semantics into the educational/browser reviews.

## Accepted update cadence — November 7, 2026

Marek replaced the earlier start/finish plan with final-summary-only reporting.
No public start update. Attempt a final summary for every normal outcome, including
collection, validation and publication failures. Abrupt termination or failure to
publish the summary may leave no report. Preserve the previous report's original
timestamps and label it “last reported run”; do not imply latest-attempt coverage,
current running state or complete run history. If there is no report, say so.

Include the specific GitHub Actions run link and a link to recent collection runs
for investigation. Actions may require GitHub sign-in; the public summary must
remain readable without it. No continuous feed, missing-run detector, public
registration or runner-loss recovery service. Detailed counts, enums, timestamps,
bounded report retention and charts remain this ticket's work. Include acceptance
cases for handled collection/validation/publication failures, abrupt termination,
failed summary publication, and an older report alongside a newer catalog.
