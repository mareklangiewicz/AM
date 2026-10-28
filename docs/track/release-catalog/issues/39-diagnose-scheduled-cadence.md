# Diagnose sparse scheduled refresh cadence

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Marek explicitly requested diagnosis of wrong scheduled cadence. Capture current
read-only GitHub schedule/run/branch/configuration evidence, replay the observed
cadence symptom and distinguish event delivery, skipped jobs, controller refusal,
runner queuing and downstream collection. Consult primary GitHub documentation
and service status. Do not dispatch, retry, alter cadence/settings, repin source,
extend the pilot, collect upstream releases or change installed apps.

## Answer

[Diagnosis and replayable evidence](../research/scheduled-cadence-diagnosis.md):
ten nominal hourly slots but one scheduled run, confirmed by workflow-specific
and repository-wide queries. No failed/skipped/queued runs. The sole run starts
immediately, job starts two seconds later, child succeeds. Remote cron/default
branch/source pin/window/enabled state and configuration history are correct.
This localizes the observed gap before dispatcher execution. GitHub-side delayed/
dropped scheduling fits documented behavior; exact internal root cause is not
provable with available public telemetry. No overlapping public Actions incident
was found. No speculative code fix or fake passing regression was introduced.

Captured replay run twice gives the same sparse-event assertion failure; it
checks actual history without creating runs. Root-cause boundaries, tested
hypotheses, third-party regression-test limits and operational alternatives are
recorded. Pilot expiry and request budget remain unchanged; no new live work.
