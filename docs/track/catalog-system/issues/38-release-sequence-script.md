# One tested command for the main-marek release sequence

Type: task
Label: implementation:task
Status: resolved
Blocked by: none

## Outcome

Moving `main-marek` is one command that refuses an untested commit and does
the rest of the sequence itself, instead of five hand-typed `git`/`gh` steps
per push (four times on November 17, 2026).

## Why

Retro of the ticket 36/37 session, second item: the sequence (push
`ci/<name>`, wait for Long tests, push `main-marek`, repin
`CATALOG_SCHEDULE_REVISION`, dispatch `catalog.yml`, find and watch the run
ids) was retyped each time, with `-R mareklangiewicz/AM` on every `gh` call.
Ticket 22 changed which pushes need a repin, so the rule now has two cases.

## Scope

`tools/release/release.py ship [--ci NAME] [--watch MINUTES]`, from a
`main-marek` checkout:

1. Refuse unless HEAD is a fast-forward of `origin/main-marek`.
2. Refuse unless one of: `origin/ci/NAME` is HEAD and its latest Long tests run
   on HEAD succeeded; or every path changed since `origin/main-marek` is under
   `docs/` (no `--ci` needed).
3. Push HEAD to `main-marek` (never forced).
4. Repin and dispatch only when the collection inputs differ from the pin
   (`collection_interface.schedule_gate_paths`, the gate's own list).
5. Print the Fast tests run id and, when dispatched, the catalog run id.
6. `--watch`: poll those runs until completed or the deadline; exit non-zero
   unless all succeeded.

Not in scope: pushing `ci/NAME` (still asked each time), deleting it.

## Comments

## Answer — November 17, 2026

`tools/release/release.py ship [--ci NAME] [--watch MINUTES]` does the scope
above. Refusals happen before any push, variable or dispatch call. The repin
check diffs pin..HEAD over `collection_interface.schedule_gate_paths()`, the
list the scheduled gate itself uses. Run ids are found with `gh run list
--commit HEAD`; the dispatched run is the one not listed before the dispatch.
Every `gh` call carries `-R mareklangiewicz/AM`.

Tests: `tools/release/test_release.py` (13), against scripted `git`/`gh`
replies that also fail on any unexpected call; added to the tool suites of
`tests.yml` and `long-tests.yml`. Mutants that skip the Long tests
conclusion, always repin, ignore a failed watched run, or let code through
without `--ci` each fail them. Run for real: refuses "nothing to ship" on a
pushed HEAD.

November 17, 2026: first real use shipped this ticket itself. `release.py ship
--ci release-script --watch 30` after Long tests 44188801014: pushed
`9f9cfc17f`, repinned from `02c7495d4` (one input changed:
`tools/catalog-collector/README.md`), dispatched catalog run 44191285057;
Fast tests 44191275884 and the catalog run both green, exit 0. Two findings:

- Its output is block-buffered when stdout is not a terminal, so a
  backgrounded run shows nothing until it exits; `print(..., flush=True)`
  (or `python3 -u`) would fix it.
- A README edit under `tools/catalog-collector` counts as a collection input
  (the `source` scope is the whole directory), so it costs a repin and
  dispatch. Excluding `*.md` from the gate's paths would avoid that; not
  decided.
