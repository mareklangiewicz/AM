# Keep scheduled collection running across pushes that do not change it

Type: task
Label: implementation:task
Status: open
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
