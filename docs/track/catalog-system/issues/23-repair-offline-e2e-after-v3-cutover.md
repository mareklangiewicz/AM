# Repair the offline e2e suite after the v3 cutover

Type: task
Label: implementation:task
Status: resolved
Assignee: claude
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

## Answer — November 16, 2026

Fixed in the commit "Repair the offline e2e suite for the format-3 catalog
client". `./test/e2e/run` passes on the merged tree: debian 21, fedora 21,
`./test/e2e/run termux` 14.

The suite had not followed the v3 cutover. Four causes, all on the test side:

- the fixture published a format-2 tree; the client reads format 3;
- the adapter answered the `release-catalog` ref, the client asks for
  `release-catalog-v3` (the cause named when this ticket was opened; the
  45-second timeout was the same refusal);
- scenarios that corrupt a source document wrote
  `repositories/<id>.yaml`, a path the format-3 tree does not have;
- the module check expected every file under `modules/` to survive a sync,
  but a real sync deletes what `APP-MANAGER` does not name.

No manager or module code changed. The images now need PyYAML (`python3-yaml`,
`python3-pyyaml`, `pip install pyyaml` on Termux), so they rebuild once.

Left open, for [ticket 24](24-simplify-and-unify-catalog-process.md):

- `modules/catalog-yaml-reader.am` and `modules/catalog-yaml-parser.am` are
  format-2 modules the manager deletes on sync; only collector tests still use
  them.
- Nothing runs this suite automatically.
