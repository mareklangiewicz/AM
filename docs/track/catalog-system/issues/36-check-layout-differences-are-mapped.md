# Check that every layout difference is mapped to a setting

Type: task
Label: implementation:task
Status: resolved
Blocked by: none

## Outcome

`tools/recipe-conversion/test_convert.py` fails when a row in `layouts.json`
has a template line that differs from the base reviewed layout and is not
mapped to a declaration setting or explicitly marked neutral.

## Why

Ticket 32: template 3.6 entered `layouts.json` to reproduce an old bulk
conversion, and nothing asked what its install steps did differently, so 579
declarations lost upstream's `--no-sandbox` strip unnoticed for over a week.
The test added then covers only that one `sed` line. The next candidate,
AppImage-in-archive, differs in its download/extract steps, exactly the kind
of change this would force someone to map.

## Scope

- A table beside `layouts.json` (or in it): for each layout, the differing
  lines against `b7c72a974` and the setting or "neutral" each maps to.
- The test diffs each layout body against the base and requires every
  differing line to be in the table, and every table entry to still differ.
- Replaces the single-line test from ticket 32.

## Comments

## Answer — November 17, 2026

Marek chose, in the session: a third kind, `dropped` (with a ticket), for
lines that are neither a setting nor neutral; and the check lives in
`convert.layouts()`, so conversion can never use an unmapped layout.

- `layouts.json`: rows after the base (`b7c72a974`, first row) carry
  `differences`, one entry per removed or added line (`convert.differences`,
  `difflib` over lines), each with exactly one of `setting`, `neutral` or
  `dropped` + `ticket`. `bb53f3180`: both sed lines map to
  `DESKTOP_STRIP_NO_SANDBOX`. `cf50304fc` (3.6): the version comment is
  neutral, both sed lines map to the strip (the added one also globs every
  launcher, noted), and the 22 multiple-launcher lines are `dropped`, ticket
  37.
- `convert.check_differences` refuses an unmapped line, an entry that no
  longer differs, a `setting` entry for a key the row does not set, a row
  setting no entry maps to, and an entry with zero or two kinds or `dropped`
  without a ticket.
- Tests: `test_convert.LayoutDifferences` (5) drives `layouts()` through a
  patched `LAYOUTS` file; each of the five refusals was mutated away in turn
  and a test failed each time. Ticket 32's single-line test is removed.
  Whole recipe-conversion suite: 21 tests OK, corpus counts unchanged.
- Writing the 3.6 entries surfaced ticket 37: the shared installer's
  `mv ./squashfs-root/*.desktop` fails outright on an AppImage with two
  top-level desktop files.

November 17, 2026: pushed with Marek's approval as `7569c5526` after Long
tests run 44125730308 passed on `ci/layout-differences` (fast, tree, Debian
and Fedora e2e). `CATALOG_SCHEDULE_REVISION` repinned to it; dispatched
catalog run 44128846771 (acquire, publish) and Fast tests 44128842671 passed.
Branches `ci/layout-differences` and `ci/format-3-collection` deleted.
