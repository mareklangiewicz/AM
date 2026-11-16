# Repair the offline e2e suite after the v3 cutover

Type: task
Label: implementation:task
Status: open
Blocked by: none

## Outcome

`./test/e2e/run` passes on `main-marek`, so it can serve as the whole-command
check before a push that ticket 18 assumed it was.

## Why

On November 16, 2026 the suite failed 27 tests with 1 error on both debian and
fedora, with the same failing tests on `cf9b5cc9b` (before the upstream merge)
and on the merge commit `8f3bd0cf3`. Installs stop at:

    Unexpected offline request: https://api.github.com/repos/e2e-selected/AM/commits/heads/release-catalog-v3
    AM YAML catalog: catalog transfer refused

The offline fixture does not answer the client's request for the
`release-catalog-v3` branch tip. The last commit under `test/e2e/` is
`eedd89328`. Whether every failure has this one cause is not established: the
error (`test_interrupted_appman_install_and_update_retry`) is a 45-second
timeout.

## Scope

- Make the fixture serve what the v3 client asks for, or change the scenarios
  to the v3 flow.
- Find when it last passed (`git bisect` with `./test/e2e/run`, about one
  minute per run) if the cause is not clear from the fixture.
- Nothing runs this suite automatically; decide with Marek whether something
  should.

## Comments

November 16, 2026: opened from the first upstream merge (ticket 18).
