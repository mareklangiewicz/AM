# Slim the status channel

Type: task
Label: implementation:task
Status: open
Triage: needs-triage
Blocked by: none

## Outcome

As decided in [Show failures and staleness](11-show-failures-and-staleness.md),
on today's status layout (ticket 16 later moves it under `catalog/status/`):
no per-source detail files, `details` map or per-source `reason`; one
`status/runs.yaml` holding the last 64 run summaries (`id`, `attempt`,
`reported_at`, counts `enrolled`/`selected`/`succeeded`/`failed`, the 7 known
metrics as plain integers, an early-stop-only `stop_reason`); statistics with
the five age buckets from `observed_at` (under 24 h, 24–48 h, 48 h–14 days,
over 14 days, never collected) and no daily aggregates. The page shows a
source's state from its repository file, with 11's sentences for each
`failed_with` code, "Never collected" and data older than 14 days. Readers,
schema and tests follow; the old branch's extra files are dropped by the next
run.
