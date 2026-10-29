# Close and assess the bounded hourly pilot

Type: task
Status: resolved
Triage: ready-for-human

## Scope

At/after 2026-10-29T00:12:16Z, disable catalog-schedule.yml (already authorized by
ticket 36), verify no new child dispatch after expiry, and assess actual run count,
release requests/statuses/bytes, freshness and full remote history object growth.
Retain exact artifacts/logs/publication relationships before seven-day expiry.
Do not extend window, repin source or enable ongoing scheduling automatically.

The controller refuses further submission after expiry even if disabling is
late. Existing queued child may complete. Emergency stop is disable workflow and
clear CATALOG_SCHEDULE_REVISION; independently cancel in-flight child if required.
Do not rewrite/delete release-catalog or alter installed apps as cleanup.

Use `gh workflow disable catalog-schedule.yml --repo mareklangiewicz/AM` for
closing the trigger, then verify remote workflow state. This task requires elapsed
pilot time, not another approval for the already approved shutdown.

## Interim observation 2026-10-28T08:56Z

[First scheduled run verified](../research/hourly-pilot-first-run-findings.md),
but only one event listed in approximately nine pilot hours. Actual source and
variables unchanged; no failed controller job to explain absent ticks. Assess
scheduler delivery separately from successful six-source collection/publication.
No automatic extension or replacement dispatch is authorized.

## Accepted follow-on daily operation

Marek subsequently accepted ticket 40's once-daily final cadence and 48-hour
freshness policy. Complete the existing expiry/shutdown/assessment without
extending the hourly pilot, then [41](41-activate-daily-refresh.md) may perform the
already authorized daily switch. No repeat approval is required for that scope.

## Answer — 2026-10-29

Closed and assessed; [retained verification](../research/hourly-pilot-closure.md).
Four successful children, 24 conditional HTTP 200 responses, exact artifact/tree/parent
verification, full history growth measured. Post-expiry dispatcher refused and
created no child. Workflow disabled; no in-flight collector. Ticket 41 unblocked.
