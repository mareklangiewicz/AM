# Review AppImage-in-archive `cf50304fc` as a declaration layout

Type: task
Label: implementation:task
Status: resolved
Blocked by: none

## Outcome

`AM-SAMPLE-AppImage-in-archive` at `cf50304fc` is a reviewed layout, and
its long recipes whose selection names a direct AppImage become
declarations: 4,630 on `f893d8e03`. Those whose selector takes any asset
(659 long recipes; 661 originals) stay as they are.

## Why

Ticket 31's top row (6,009 instances that are not declarations). The body
differs from reviewed 3.6 only in its download step: it unpacks a `7z`,
`tar.*` or `zip` download and lifts a single top directory, else moves the
file. With one downloaded file whose name ends in `mage`, none of that
applies and the step is 3.6's `mv ./tmp/*mage`.

November 19, 2026, Marek's answer: a conditional layout (declarations only
when the selection names a direct AppImage), not archive support in
`modules/appimage.am`.

## Scope

- The condition is the one every declaration already meets:
  `bulk_recipes.url_rules` refuses a selector without an include rule ending
  in `mage$` ("selector does not establish a direct AppImage suffix"). The
  layout row maps the download-step lines as `neutral` on that ground.
- Tests in `tools/recipe-conversion/test_convert.py`: the layout loads with
  every line mapped; an anchored instance converts to the same declaration
  as the 3.6 instance with the same parameters; an unanchored one refuses.
- Then `relayout.py --layout cf50304fc --from long` writes the conversion;
  Long tests and a dispatched catalog run before it counts as done.

## Comments

## Answer — November 19, 2026

- `bbcd035d4`: `layouts.json` gains `cf50304fc:templates/AM-SAMPLE-AppImage-in-archive`
  (setting `DESKTOP_STRIP_NO_SANDBOX=true`). Its lines shared with 3.6 keep
  3.6's mappings; its 14 other lines (4 comments, 10 download-step lines in
  installer and updater) are `neutral`, on the ground in Scope.
  `relayout.py --layout` takes `COMMIT:PATH`, since `cf50304fc` now has two
  reviewed templates.
- Tests (`test_convert.py` `InArchive`): an anchored instance
  (`aarch64/2ship2harkinian` at `ba061a639`) gives exactly the declaration of
  the same parameters rendered into 3.6; an unanchored one
  (`aarch64/6502-emulator`) refuses with "direct AppImage suffix". The
  existing "declaration refuses, long converts" test moved from
  `x86_64/1devtool` (now a legitimate declaration) to
  `x86_64/actone-screenplay`. `test_relayout.py` `Layout`: a shared commit
  needs the path.
- `4a0efa530`: `relayout.py --from long --write` converted 4,630 recipes,
  all with unchanged selection; 659 refuse ("selector does not establish a
  direct AppImage suffix") and stay long. A fresh `generate()` gave the
  written module.

Shipped with Marek's approval: Long tests 44534741934 green on
`ci/in-archive` (fast, tree, Debian and Fedora e2e); `release.py ship`
pushed `4a0efa530` and repinned `CATALOG_SCHEDULE_REVISION` from
`db00f2544` (4,631 inputs); Fast tests 44536081144 and dispatched catalog run
44536085052 green. `ci/in-archive` deleted.
