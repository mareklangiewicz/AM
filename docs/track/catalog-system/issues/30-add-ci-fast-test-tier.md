# Add a CI fast test tier

Type: task
Label: implementation:task
Status: open
Blocked by: 28

## Outcome

Every push to `main-marek` runs a fast tier of tests in GitHub Actions within
a few minutes. A failure shows as a failed run and blocks nothing. The full
collector suite and e2e stay on demand, and the merge README says to run them
before each upstream merge.

## Why

Nothing runs any suite automatically; the e2e suite stayed broken from the v3
cutover until [ticket 23](23-repair-offline-e2e-after-v3-cutover.md). `am`
reads the branch live, so CI cannot gate a push, and the repo uses no Git
hooks. Decided in
[ticket 24](24-simplify-and-unify-catalog-process.md#answer--november-16-2026).

## Scope

- First measure where the collector suite's time goes (226 tests in 1,053 s
  on November 16, 2026; 18 to 47 minutes across runs) and report the slowest
  tests. Not measured yet.
- Fast tier candidates: recipe-conversion (15 tests), recipe-reconstruction
  (44), upstream-merge (15), e2e helper units (11), plus whatever part of the
  collector suite is fast. The corpus tests need Git objects `7b4f831e6` and
  `6277377ae` in the CI checkout.
- Check whether the offline e2e suite (containers) can run in Actions on
  demand.

## Comments
