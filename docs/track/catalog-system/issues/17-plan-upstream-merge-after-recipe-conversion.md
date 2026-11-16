# Plan the upstream merge after the recipe conversion

Type: research
Label: wayfinder:research
Status: resolved
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

## Answer — November 16, 2026

Decided with Marek in a grilling session; recorded as
[ADR 0005](../../../adr/0005-upstream-authoritative-converted-recipes-derived.md).
Terms are in `GLOSSARY.md` under Recipes.

Facts found during the session (upstream as fetched November 15):

- Upstream's changes under `programs/` since the merge base: about 1,476
  added, 529 modified, 401 deleted, and 108 that Git pairs as renames but look
  like unrelated add/delete pairs.
- All 400 modify/delete conflicts are recipes upstream deleted and the fork
  converted.
- Of 400 sampled upstream-modified `x86_64` recipes, 277 carry template version
  3.5 and 122 carry 3.6.
- `x86_64` today: 294 original recipes, 7,814 long recipes, 791 recipe
  declarations. The installer handles all three.
- 300 sampled declarations were all plain original recipes at the merge base.
- Upstream has 47 commits touching `APP-MANAGER`, modules or templates.

Decisions:

1. The fork keeps following upstream; upstream is authoritative for which apps
   exist and for original recipes. Converted forms are derived and never
   hand-merged.
2. Upstream changed an original: take upstream's text and re-run the conversion.
   On refusal fall down the ladder: same form, else long recipe, else upstream's
   original. The source stays enrolled; the fallback is listed in the receipt.
   Template 3.6 support is therefore not a prerequisite for the first merge.
3. Upstream deleted a recipe: delete it and take its source out of collection
   enrollment; published catalog history stays. Deleted apps installed on one
   of Marek's machines are reported for a decision.
4. Upstream added a recipe: it lands as an untouched original. Conversion and
   enrollment are a separate later batch.
5. Fork-owned recipes come from an explicit list and are never overwritten;
   upstream changes or name collisions on them are reported.
6. One real `git merge` commit with `upstream/main` as second parent.
   `programs/` is produced by a repeatable tool that writes a receipt;
   `APP-MANAGER`, `modules/install.am` and `README.md` are merged by hand.
   Runtime changes land in the same merge as the recipes, not earlier.
7. The merge is pushable only when: the receipt accounts for every recipe path
   in both parents as exactly one of taken from upstream, re-converted, fell
   back, deleted, fork-owned kept; every converted recipe upstream did not touch
   is byte-identical to before; `AMREPO`, `ALT_GH` and every `MAREK-FORK` mark
   survive; the existing tool tests and `regress/` pass. The installed-host
   check stays a separate authorized step after the push.
8. The first merge runs after ticket 16's conversion is committed and
   published. After that, sync at least monthly, with a dry run reported first.

Left for [ticket 18](18-build-upstream-merge-tool-and-run-first-merge.md): no
single tool was found that converts an original recipe straight to a recipe
declaration (declarations came through an intermediate wrapper form), so "same
form" on the ladder may need one built, or fall to a long recipe at first.

November 16, 2026, later: Marek decided that tool must exist and be solid;
ticket 18's scope now requires the direct original-to-declaration conversion.
