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
without finalization, latest attempt versus last publication, history gaps, retention
and aggregate bounds. Show safe examples for success, budget stop, failed validation,
failed publication and abrupt interruption.
Use the consistency model from the contract ticket; do not invent another schema
or strengthen timestamps. Allowlist sanitized public fields, not environment/header
dumps. Decide the few useful initial charts with Marek, measurement definitions
and drill-down links. Feed these semantics into the educational/browser reviews.
