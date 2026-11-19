# Re-convert recipes for a reviewed layout in one command

Type: task
Label: implementation:task
Status: resolved
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

November 19, 2026, two more answers from Marek, after the first replay runs
found recipes the tickets 32/33 scripts never covered: a recipe whose
re-conversion would select differently is refused and left as it is (the run
goes on), and `--from declaration|long` narrows a run to one form.

## Answer — November 19, 2026

`tools/upstream-merge/relayout.py --layout COMMIT [--from FORM] [--write]`
(usage in `tools/upstream-merge/README.md`). It re-converts each covered
recipe as a declaration, refuses any whose selection rows (`url_policy_rows`,
`recipe_rows`: repository id and name, channel, asset pattern, URL rules,
catalog app, fresh-only) would change, then derives the files with
`merge.derive`/`merge.stage`. A final check also requires every policy row
of the recipes it did not touch to be unchanged. The dry run is the default.

Tests:

- `test_relayout.py` (fast, 3): pinned `x86_64/zulip` before
  (`cf6255fc3`, long) and after (`082502f64`, declaration) selects the
  same. Mutants of repository id, repository, channel, asset pattern, URL
  rules, catalog app and fresh-only are each named, and so is a recipe that
  stops selecting.
- `tree_relayout.py` (replays, ~45 s on myxps, in Long tests): ticket 33
  reproduced byte for byte (1,171 recipes, registry, compiled module; the
  same 3 refusals). Ticket 32 reproduced (579 declarations; 586 is the
  pinned corpus count). Both replays were red before the refusal rule and
  `--from` were added.
- Run for real: `--write` in a scratch worktree (`--layout cf50304fc --from
  long`) wrote 784 recipes and 2 derived files; a fresh `generate()` gave
  the same module; a second `--write` refused (paths modified).

Findings on HEAD `6292edaae` (dry runs, originals at `ba061a639`):

| Layout | Long → declaration, same selection | Refused: selection would change | Other refusals |
|---|---|---|---|
| `b7c72a974` (3.5) | 791 | 3: neovide, neovide-nightly, sunshine | 3 |
| `bb53f3180` | 0 | 3: 5ire, actiona, obsidian | 3 |
| `cf50304fc` (3.6) | 784 | 6: 0x808, 0xsynth, 3mf-katalog-manager, aeroftp, ag-repatch, agent-buddy | 0 |

- 1,575 long recipes can become declarations with unchanged selection. 732
  of the 784 at 3.6 were already instances at the bulk-conversion base
  `7b4f831e6`; why the bulk run made them long is not checked (a guess:
  conversion rules widened since). Not converted here: that is a separate
  decision.
- The 12 refused declarations were written by hand in the v3 migration
  (`80122f46e`): their own asset patterns, and some settings conversion
  does not produce (`EXTRA_APP_LAUNCHERS`, `DESKTOP_EXEC`). The 9 from
  `bb53f3180` and 3.6 do not set `DESKTOP_STRIP_NO_SANDBOX=true`, though
  their layout does; not decided whether they should.

November 19, 2026: shipped with Marek's approval. Long tests 44509415534
green on `ci/relayout` (the new "Relayout replays" step: 2 tests, 12 s);
`release.py ship --ci relayout --watch 30` pushed `077b463f5`, Fast tests
44510586158 green. Collection inputs unchanged, so `CATALOG_SCHEDULE_REVISION`
stays `a506f3dd5` and nothing was dispatched. `ci/relayout` deleted.

November 19, 2026: two-axis review of `a506f3dd5..a63693032` (tickets 35,
39-43). Fixed in `c668d9948`: relayout writes derived files as UTF-8; both
replays check the exact set of derived files; `release.py watch` continues
with the minutes it was given; `convert.py` reads `template.settings`.
Not fixed: a declaration that is not UTF-8 still crashes `relayout`, as it
crashes `merge.py` (108, 163, 236); declarations are generated as UTF-8.
Left over (the ticket 43 guard was fixed in `fd9a4c343`, see ticket 43;
the other findings are resolved below):
- `incremental.py` format-2 branches are still reached from
  `rehearse_pipeline.py`: leave them to ticket 25.

Shipped with Marek's approval: Long tests 44564074865 green on
`ci/review-fixes`; `release.py ship` pushed `e019f7ce1`, Fast tests
44566930800 green. Collection inputs unchanged, so `CATALOG_SCHEDULE_REVISION`
stays `4a0efa530`. `ci/review-fixes` deleted.

`modules/appimage.am` copy check: kept. Template 3.6 (`cf50304fc`, line 82)
compares sorted lines against the main launcher the same way, and a 3.6
declaration must install what its long recipe does. The counters are renamed
`staged_main` and `launchers`, and the comment says why the compare is 3.6's.

579, not 586: the 586 in this ticket's Comments is the pinned corpus's count;
the tree at `d85c3851b^` has 579 declarations from template 3.6, and ticket
32 counts 579 (its line 27). The replay's 579 is the number to keep.
`scripts/31` fixed (see ticket 31's how-to): `run.sh` runs all seven steps
with `layouts.json` as of `539ccac8d`, `report.py` writes `table.json` beside
its inputs, `origins.py` finds layout versions by body hash; a rerun matches
the published numbers and the old `origins.py` output byte for byte.

`FIELDS` now holds every compiled selection field (`03523af78`). It left out
`selection`, `tag_pattern`, `tag_exclude`, `git_ref`, `git_file`, `tools` and
`tool_asset_suffix`; conversion carries only repository identities, so a
re-converted recipe could have dropped them unnoticed. 32 long recipes have
such policy rows; dry runs of all four layouts re-convert none of them, and
none of the shipped conversions (`082502f64`, `a2fad9fc8`, `db00f2544`,
`4a0efa530`) had one. `selections()` still compiles only the changed recipes:
no compiled row has needed another recipe, so the whole-tree compile is not
worth its cost. Ticket 40's first-refusal question: see ticket 40.
