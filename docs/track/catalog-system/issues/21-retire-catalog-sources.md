# Retire catalog sources no recipe selects from

Type: task
Label: implementation:task
Status: claimed
Blocked by: none

## Outcome

A source can be taken out of collection enrollment. Its documents leave the
next published snapshot, earlier snapshots keep them, and its source name is
never reused. The sources the first upstream merge lists are retired this way.

## Why

[ADR 0005](../../../adr/0005-upstream-authoritative-converted-recipes-derived.md)
says a recipe upstream deletes takes its source out of collection enrollment.
Today that cannot be done: `host_catalog.collect` refuses a batch when the
published catalog retains a source the enrollment no longer has ("batch would
discard retained sources"), and nothing moves a name from `active` to `retired`
in `tools/catalog-collector/source-names.json`. The upstream merge therefore
leaves such sources enrolled and only names them, under `sources_to_retire` in
its receipt.

## Scope

- An explicit retirement step: remove the enrollment row, move the source name
  to `retired`, and let collection drop exactly those retained documents. A
  source missing from enrollment without that step still refuses.
- Retire the merge receipt's `sources_to_retire`, and the am-utils source
  (repository 1225768109) once no recipe uses it: upstream moved the am-utils
  recipes to "am-extras" (`0a221879c`), and the receipt cannot see that source
  because those recipes carry no policy rows.
- Remove the then-unused am-utils policy (`am_utils_recipe` in
  `modules/catalog-yaml-policy.am`) and its reference data.

Pushing, the schedule pin and delivering the changed policy module to an
installed host need Marek's authorization.

## Comments

November 16, 2026: opened from tickets 16 and 18.

November 22, 2026: claimed; "Blocked by: 18" was stale (18 is resolved).
Built and run locally, not pushed:

- `collection_interface.collect` drops a retained source whose name is in
  `retired` and that is no longer active: its `repositories/` and
  `provenance/` documents leave the candidate (`Candidate(removed=...)`), a
  schema transition does not rebind it, and batch mode no longer sees it as
  discarded. A retained source that is neither active nor retired refuses
  ("retained source NAME is neither active nor retired"; before, a
  `TypeError`). Tests: `test_source_retirement.py`, red first on that
  `TypeError`.
- `retire_sources.py RID ... [--write]` is the explicit step: rows leave
  `collection-apps.json`, names move to `retired`. It refuses a source a
  declaration, a URL policy, an AppImage policy or any recipe's GitHub URL
  still names. Tests: `test_retire_sources.py`; each refusal checked by
  removing it (red).
- The list was recomputed on today's tree, not taken from the November 16
  receipt. Of the receipt's 34 plus am-utils, `dabri` (970408916) is selected
  again (its AppImage policy, `x86_64/dabri`) and 9 are still named by an
  upstream recipe under a new app name (ticket 46). The other 25 are retired:
  202 catalog-only rows, 178 of them am-utils (source name `7z`). 21 of the 25
  have documents in the live catalog (`c269faf5d`); 4 never did.
- `am_utils_recipe` is gone from `modules/catalog-yaml-policy.am`, with
  `AM_UTILS` in `reference_policies.py` and its only input,
  `test-data/consumer-inventory.json`. No am-utils app is installed on myxps
  (checked `/opt/NAME/remove` for all 178 names). `APP-MANAGER`'s runtime
  download of am-utils static binaries is separate and unchanged.

Rehearsed on `2bd635d70`'s tree (a throwaway worktree), offline:
`host_catalog.py collect --parent c269faf5d --batch-size 1` with empty saved
evidence, 761 s. The candidate validates and differs from the live catalog
by exactly 42 removed paths, the 21 retired sources' `repositories/` and
`provenance/` documents; nothing added, no app points at a retired source.

Left for Marek: pushing (the `policy` and `source` inputs change, so the
schedule pin moves) and delivering the changed policy module to installed
hosts. Resolve once a catalog run under it drops the 21 documents.
