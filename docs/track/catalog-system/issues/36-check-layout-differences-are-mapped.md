# Check that every layout difference is mapped to a setting

Type: task
Label: implementation:task
Status: open
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
