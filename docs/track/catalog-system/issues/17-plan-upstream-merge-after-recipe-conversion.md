# Plan the upstream merge after the recipe conversion

Type: research
Label: wayfinder:research
Status: open
Triage: needs-triage
Blocked by: none

## Question

How does `main-marek` take `upstream/main` now that most recipes under
`programs/` are short v3 declarations? Produce a merge strategy that can be
repeated on every later sync, and say what it costs.

## Why now

The routine sync (`myapps` skill, `procedures/sync-fork.md`: `git merge
upstream/main`, resolve the two `programs/<arch>-apps` list conflicts) no longer
applies. Measured November 16, 2026, with upstream as fetched November 15
(`6f0b7389d`), `main-marek` at `6277377ae`:

- `main-marek` is 403 commits behind and 446 ahead; merge base `7b4f831e6`
  (October 19, 2026).
- Since the base the fork modified 10,435 files under `programs/` and added 8;
  upstream changed about 2,500 files there.
- A trial merge (`git merge-tree --write-tree --name-only main-marek
  upstream/main`, no checkout touched) reports 986 conflicts: 586 content, 400
  modify/delete (the fork modified a recipe that upstream deleted).
- 983 of them are under `programs/` (772 `x86_64`, 209 `aarch64`, 1 `i686`,
  `aarch64-apps`). The other three are `APP-MANAGER`, `modules/install.am` and
  `README.md`.

The gap grows by roughly 400 upstream commits a month.

## Scope

- Decide what is authoritative for a converted recipe when upstream changes or
  deletes its original: re-derive the declaration from upstream's new text, keep
  ours, or refuse and review.
- Decide whether `tools/recipe-reconstruction` (release-catalog
  [120](../../release-catalog/issues/120-prototype-upstream-recipe-reconstruction.md)
  to [123](../../release-catalog/issues/123-generalize-upstream-template-recognition.md))
  can drive the merge: classify upstream's changed recipes at the new revision,
  convert the recognized ones, list the rest. Its pinned template revisions
  predate current upstream (the map already notes upstream's 3.6 template needs
  its own review).
- Account for the 400 upstream deletions: which are renames, which are removed
  apps, and what happens to their catalog identities and enrolled sources.
- Treat the three runtime files separately. The fork patches in `APP-MANAGER`
  and `modules/install.am` must survive: `AMREPO` on the fork's `main-marek`,
  `ALT_GH="https://api.github.com"`, and every `MAREK-FORK` mark.
- Say whether upstream's runtime changes (manager, modules, templates,
  translations) can land ahead of the recipes without recording a merge that
  hides the recipe work still owed.
- Keep `git merge`, never rebase: `am` reads this branch live.

Out of scope: performing the merge, pushing, or changing any installed host.

## Evidence to keep

Record the commands and counts used, so the next sync can compare.

## Comments

November 16, 2026: opened from a home-directory session after `gndx home sync`
kept reporting the clone 403 behind upstream. Measurements above are from that
session; nothing in the checkout or on any branch was changed.
