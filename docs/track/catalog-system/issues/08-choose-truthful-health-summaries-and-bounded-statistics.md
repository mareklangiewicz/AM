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

## Accepted update cadence — November 7, 2026

Marek accepted public health updates at run start and finish only. A start with
no recorded finish means “started, no completion recorded”; do not infer failure,
success or partial-source counts. Missing/unavailable records remain gaps. No
continuous progress feed or runner-loss recovery service is required. This
cadence is settled; detailed summary semantics and bounds remain this ticket's work.
