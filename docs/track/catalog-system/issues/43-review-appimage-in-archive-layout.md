# Review AppImage-in-archive `cf50304fc` as a declaration layout

Type: task
Label: implementation:task
Status: claimed
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
