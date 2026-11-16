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

November 16, 2026: suite timed at `479574930` with
`python3 -B -m unittest discover -s tools/catalog-collector -p 'test_*.py' --durations 0`:
226 tests, 1,045 s, all pass.

| Seconds | Where |
| --- | --- |
| 415 | `test_yaml_appimages` `test_actual_manager_all_saved_matches_and_generated_updaters`: runs the real manager for every recipe in the live AppImage policy table |
| 205 | `test_host_cutover` `test_all_host_recipes_manager_install_and_standalone_update` |
| 58 | `test_yaml_appimages` `test_adversarial_url_rules_on_three_awk_tools` |
| 526 | `test_yaml_appimages`, whole file |
| 240 | `test_host_cutover`, whole file |
| 80 | `test_yaml_manager_integration`, whole file |
| 199 | the other 30 or so files together |

Two tests are 59% of the run and three files are 81%. The two slowest are
also whole-tree checks over live recipes, which
[ticket 28](28-unpin-tests-from-live-recipes.md) wants out of the unit suite.

Proposal, not yet agreed: name the tier by file. Whole-tree and
real-manager-over-every-recipe checks move to `tree_*.py` files, run with
`-p 'tree_*.py'` before an upstream merge and on demand; `test_*.py` stays the
fast tier (about 3 to 7 minutes depending on how much of the manager
integration stays) and is what CI runs. No skip flags, so nothing is silently
off.
