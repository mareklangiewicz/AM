# Keep scheduled collection running across pushes that do not change it

Type: task
Label: implementation:task
Status: resolved
Blocked by: none

## Outcome

A push to `main-marek` that changes nothing the collection reads does not
pause scheduled collection.

## Why

`.github/workflows/catalog.yml` runs a scheduled collection only when
`vars.CATALOG_SCHEDULE_REVISION == github.sha`. The variable is a review gate
for collector, policy and recipe changes, but it compares whole commits, so any
push pauses collection until someone repins the variable by hand. On November
16, 2026 three documentation commits (`e8cecf50c`, `0b568f16d`, `ae2c2d2c5`)
were pushed at 13:56 UTC without a repin; the pin stayed at `6277377ae` until
Marek approved a repin at 15:27 UTC. `gh run list` shows no scheduled run,
skipped or otherwise, in between, so none was lost that time.

## Scope

- Decide what the gate should compare: the reviewed revision of the paths
  collection reads (the workflow, `tools/catalog-collector/`,
  `tools/catalog-contract/`, `modules/`, `programs/`), or the whole commit as
  now with the repin made part of every push.
- Whichever is chosen, a skipped scheduled run must be visible in the status
  branch, not only as a skipped job in Actions.
- Until this is done, every push to `main-marek` is followed by
  `gh variable set CATALOG_SCHEDULE_REVISION` to the new tip, after checking
  the diff from the old pin.

## Comments

November 16, 2026: opened from the ticket 16 review.

November 17, 2026: the hourly cron fires far less often than hourly. Scheduled
runs on November 15 to 17 started at 22:51Z, 02:45Z, 11:26Z, 22:07Z and
04:30Z (`gh run list --workflow catalog.yml`), so "wait for one scheduled
run" can cost hours. A dispatched run (`gh workflow run catalog.yml --ref
main-marek`) runs the same acquire and publish jobs; only the schedule's pin
check is skipped. It served as the observed run for ticket 33 (run
44069990694, acquire and publish green). Proposed convention: a dispatched run
on the pinned commit counts as the observed run. Two manual repins today
(`34290b8c4`, `082502f64`); the step B push will need a third.

November 17, 2026 (retro of the ticket 36/37 session): the silent skip was
the most severe retro item; Marek chose the path-scoped gate.

## Answer — November 17, 2026

Marek chose to compare the collection inputs, not the whole commit. A new
`gate` job in `.github/workflows/catalog.yml` runs on scheduled runs only:
it checks out the commit `CATALOG_SCHEDULE_REVISION` names, fetches the pushed
commit, and runs that pinned commit's `host_catalog.py schedule-gate --pin
--head`. The command diffs the two over `collection_interface.INPUT_SCOPES`
(the scopes collection already verifies its pins against, hoisted out of
`verify_checkout_inputs` so there is one list) plus the workflow and
`.github/actions/catalog-collect`. No difference: acquire and publish run as
before. Any difference: the job fails listing the changed paths and the
commit to repin to, acquire and publish are skipped, the run is red.

- A skipped scheduled run is now a failed run in Actions, which GitHub reports
  to the workflow's owner; it is not written to the status branch (no run
  reaches publication), which this answer takes as covering "visible".
- Reviewed code judges the new commit: the gate runs from the pinned commit.
  Consequence: the first scheduled run after this push fails until the pin
  names a commit that has `schedule-gate` (this push changes collector code,
  so it needs a repin anyway).
- Dispatched runs stay ungated, as before.
- Tests: `tools/catalog-collector/test_schedule_gate.py` (fast tier), on a
  throwaway Git repository; a gate that returns nothing, and one without the
  workflow paths, both fail it.

November 17, 2026: Long tests 44179435023 green on `ci/schedule-gate`
(`02c7495d4`); pushed to `main-marek` with Marek's approval and repinned
`CATALOG_SCHEDULE_REVISION` to `02c7495d4` (21:36Z). Fast tests 44181646939
green. Dispatched catalog run 44181653553: `gate` skipped, acquire and publish
green, so dispatch stays ungated. Not yet observed: a scheduled run through
the gate, either passing (inputs equal) or failing red (inputs changed).

November 17, 2026: the gate ignores `README.md` files under its paths (ticket
38 comment); other Markdown such as `docs/catalog-format-v3.md` still counts.
