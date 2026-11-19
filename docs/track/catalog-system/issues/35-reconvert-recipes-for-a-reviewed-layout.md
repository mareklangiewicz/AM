# Re-convert recipes for a reviewed layout in one command

Type: task
Label: implementation:task
Status: open
Blocked by: none

## Outcome

One tested command re-converts every recipe that a reviewed layout covers,
writes the recipes and the derived files, and reports that each converted
recipe compiles to the same selection as before. Reviewing the next layout
(AppImage-in-archive, 6,009 recipes per ticket 31) is then that command plus a
commit.

## Why

Tickets 32 and 33 each needed a throwaway script (session scratchpad, lost on
reboot; logic recorded only in prose on the tickets):

- ticket 32: re-convert declarations from their `upstream/main` originals;
  write a file only if the result is the old text plus the new setting line;
- ticket 33: long recipes whose original matches one layout become
  declarations, with identities from `convert.policy_identities`; derived files
  from `merge.derive` and `merge.stage`, one `re-converted` row per recipe and
  `untouched` for the rest; then compare `url_policy_rows` before with
  `recipe_rows` after on repository, channel, pattern, URL rules, catalog app
  and fresh-only, in a temporary worktree.

## Scope

- Lives in `tools/upstream-merge` (it reuses `derive`/`stage`) or
  `tools/recipe-conversion`; dry run by default, `--write` to change the tree.
- Tests drive it on pinned fixtures, not the live tree (ticket 28).
- No new layout review in this ticket.

## Comments

November 19, 2026, Marek's answers:

- Command: `python3 tools/upstream-merge/relayout.py --layout COMMIT
  [--write]`, dry run by default; it imports `merge` (`derive`/`stage`).
- Originals come from `merge-base(HEAD, upstream/main)`, the originals the
  fork's recipes were converted from, so unmerged upstream edits never leak
  in.
- Tests: whole-tree replays of the two past runs (on `cf6255fc3` with layout
  `bb53f3180` it must produce `082502f64`'s recipes,
  `recipe-url-policies.json` and `modules/catalog-yaml-policy.am` byte for
  byte, ticket 33; on `d85c3851b^` it must produce `d85c3851b`'s 586
  declarations, ticket 32), plus fast tests on pinned recipes where mutants
  (changed pattern, channel, repository) must be reported by the
  selection-equivalence check.
