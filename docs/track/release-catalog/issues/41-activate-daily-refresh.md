# Switch from the finished hourly pilot to daily operation

Type: task
Status: resolved
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

## Offline readiness review — 2026-10-28

[59](59-daily-switch-offline-review.md) verifies the queued daily workflow/controller
still match ticket 40 and the operational collector/manifest remain six-source.
It records cached-ref hashes, private-path/ancestry checks and five focused tests.
This does not replace live checks or 37's closure; use the final reviewed pushed
SHA, not the earlier offline review HEAD, for activation.

## Activation preflight — 2026-10-29

37 closed; live default branch main-marek, six unrelated workflows disabled,
no in-flight collector. Daily workflow/controller still equal ticket 40; operational
manifest remains six-source and collector workflow is unchanged from remote.
Full three-target matrix passes 38 scenarios at 6fd050bda; logs at
`test/e2e/out/20261029T091354Z-1117351`. One extracted-test harness omitted the new
encoder definition; ticket 63 repairs that test only.

Installed catalog.am hash `b827f9febc90a45012f540926674f8f4210e3e1f3626cb30050b4422092be6fc`
exactly matches the old pilot helper. Current 48-hour helper hash is
`5c1ca600e478ef26ec7ff3c70ef4bd61f49f6e86ff66696e722a9e9b90255618`.
Host delivery remains user-run and has not occurred.

## Answer — activated 2026-10-29T09:21Z

Pushed and pinned `da0bb8b9768856e69db1b9f6c0b5e77c73f27fd5`. Remote branch,
workflow/controller/manifest bytes verified exact before activation. Recorded old
window variables in 37's archive, removed START/UNTIL and verified only REVISION
remains. Daily workflow enabled and confirmed active; collector active, six
unrelated workflows disabled. No synthetic dispatch or source enrollment.

[Activation checks](../research/daily-activation-checks.json) and
[final source review](../research/daily-activation-source-review.json).
198 catalog tests, 10 support specs, 38 container scenarios passed.

Natural daily observation and user-run host helper delivery remain explicitly
open under [64](64-observe-daily-refresh-and-helper.md). This resolution records
configuration activation, not an observed daily execution or host delivery.
Do not push later documentation commits without reviewing and deliberately
updating the source pin: the dispatcher requires default-branch HEAD to equal it.
