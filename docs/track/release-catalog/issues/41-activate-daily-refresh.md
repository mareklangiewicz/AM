# Switch from the finished hourly pilot to daily operation

Type: task
Status: open
Triage: ready-for-agent
Blocked by: 37

## Authorization

Marek explicitly accepted daily final collection with 48-hour freshness in ticket
40. This switch is already authorized; do not ask again. Wait for the existing
pilot's exclusive expiry 2026-10-29T00:12:16Z and close/assess it in ticket 37.
No external timer, new source enrollment, extra test dispatch or app operation.

## Activation

1. Confirm elapsed pilot window, preserve scheduled/child evidence, disable old
   catalog-schedule.yml and check for in-flight collector runs before switching.
2. Recheck main-marek default branch and unrelated workflows remain disabled.
   Compare local reviewed daily workflow/controller to the ticket-40 change;
   include the queued evidence and SQLite recipe commits in ordinary source push.
3. Push reviewed daily changes to origin/main-marek. Record full source SHA.
   Confirm remote source/YAML are exact. Set CATALOG_SCHEDULE_REVISION to that
   pushed SHA; remove obsolete CATALOG_SCHEDULE_START/UNTIL variables after their
   values are recorded. Enable catalog-schedule.yml for `17 3 * * *` daily UTC.
   No synthetic/manual collection merely to test the schedule. No implicit future
   source repin: review later source changes before updating approved revision.
4. Observe natural daily executions when available; preserve timestamps, six
   conditional outcomes, child publication parent/tree and actual freshness.
   Final daily operation has no pilot expiry; nominal six release requests/day,
   no retries/expansion; job/body/time limits and separate publisher unchanged.
5. Read-only verify installed /opt/am/modules/catalog.am hash against current
   48-hour helper. If still the old 24-hour version, give Marek this command per
   his preference for running privileged host commands himself:

   `sudo install -m 644 /home/marek/code/shell/AM/modules/catalog.am /opt/am/modules/catalog.am`

   This changes the metadata age policy only, with no installer/updater/app run.
   Verify afterward and record actual delivered hash. Do not claim all installed
   consumers gained 48-hour freshness until that delivery is observed.

## Limits

Daily cron is best-effort: a full missed day plus delays can still exceed 48 hours.
Readers then refuse unless exact stale consent is given. Failed observations do
not get new validation timestamps. The 48-hour policy is implemented in both shell
and Python reference readers; historical expiration evidence keeps its original
24-hour meaning. No rollback of installed apps or publication history is needed.
