# Build the upstream merge tool and run the first merge

Type: task
Label: implementation:task
Status: resolved
Assignee: claude
Blocked by: 16

## Outcome

`main-marek` contains `upstream/main` through one real merge commit produced as
decided in [ticket 17](17-plan-upstream-merge-after-recipe-conversion.md#answer--november-16-2026)
and [ADR 0005](../../../adr/0005-upstream-authoritative-converted-recipes-derived.md),
and the same tool can repeat it at the next sync.

## Scope

- A maintained tool under `tools/` that, given `main-marek` and an upstream
  revision, produces the merged `programs/` tree and a receipt: per recipe path
  exactly one of taken from upstream, re-converted, fell back, deleted,
  fork-owned kept.
- Re-conversion reuses the existing conversion tools and the recipe receipt's
  before hashes to find what upstream changed. Refusals follow the ladder: same
  form, else long recipe, else upstream's original.
- An explicit fork-owned recipe list, including the fork-only entries and every
  recipe with a `MAREK-FORK` mark; the `programs/<arch>-apps` lists keep their
  lines.
- A dry run that reports conflicts, fallbacks, deletions, installed apps among
  the deletions, and collisions with fork-owned recipes, without changing
  anything.
- A solid maintained conversion tool is part of this work, not an optional
  extra: one entry point that converts an original recipe to a long recipe or
  to a recipe declaration, with the direct original-to-declaration path built
  (today declarations only come through an intermediate wrapper form). It
  refuses what it cannot account for, has its own tests, and is what the merge
  tool calls for every rung of the ladder.
- Hand-merge `APP-MANAGER`, `modules/install.am` and `README.md`.
- The four-part gate from ticket 17, decision 7.

Pushing the merge and any installed-host action need Marek's specific
authorization. Merge, never rebase.

## Comments

November 16, 2026: opened from ticket 17's answer. Unassigned.

November 16, 2026: Marek decided the conversion tool must be solid, especially
original recipe to recipe declaration. The earlier "find out whether" item is
replaced by that requirement in Scope.

November 16, 2026, takeover session: Marek asked Claude to take over ticket 16
and continue here. The tools were built ahead of the merge itself, which still
waits for ticket 16:

- `tools/recipe-conversion/` ([README](../../../../tools/recipe-conversion/README.md)):
  one entry point, `convert.py`, for both forms, with the direct
  original-to-declaration path. Its corpus tests rebuild the published bulk
  conversion from the merge-base originals byte for byte: 984 recipe
  declarations and 8,770 long recipes with their policies.
- `tools/upstream-merge/` ([README](../../../../tools/upstream-merge/README.md)):
  `merge.py plan | apply | gate` and `fork-owned.txt` (the eight fork-only
  recipes and `aarch64/appimageupdatetool`, the one recipe with a `MAREK-FORK`
  mark).
- Receipt outcomes: the five from ticket 17 plus `untouched`, for a recipe
  upstream did not change. A re-conversion that lands in a lower form (long
  instead of declaration) counts as `fell back`.

Found while building, each changing the scope written above:

- Un-enrolling a deleted recipe's source is not a file edit. The collector
  refuses a batch that would drop a source the published catalog retains
  (`host_catalog.collect`: "batch would discard retained sources"). The merge
  leaves those sources enrolled and lists them in the receipt under
  `sources_to_retire`; retiring them is collector work in
  [ticket 21](21-retire-catalog-sources.md).
- The wrapper translator kept a selector's shell expansions as pattern text.
  `x86_64/odicto` and `x86_64/pdf4qt` were published with
  `https.*$APP.*...mage$`, which matches nothing. Fixed in both recipes and in
  the translator (commit `0ae2468fe`): a literal `$APP` is written out, any
  other expansion refuses.
- A long recipe that picks its repository at run time (`"$RELEASE"`) was
  converted with policies for the given identities only, so a variant upstream
  adds later would refuse at install time. The conversion now refuses unless
  every offered `SITEn` has an identity (`appimagetool` hits this).
- `regress/` installs real apps from the network through the pushed `AMREPO`
  branch, so it cannot test an unpushed merge. The fork's offline container
  suite `test/e2e/run` is the whole-command check before the push; `regress/`
  can only follow it.
- Upstream deleted whole families the tool tests are pinned to: the am-utils
  recipes (moved to "am-extras", upstream `0a221879c`) and all 49 recipes in
  `unavailable-github-recipes.json`. Their tests have to be retired or
  re-pinned in the merge commit.

## Answer — November 16, 2026

`main-marek` holds `upstream/main` `ba061a639` through merge commit
`8f3bd0cf3` (parents `cf9b5cc9b`, `ba061a639`), made with
`tools/upstream-merge/merge.py apply`. Not pushed; the push, the
`CATALOG_SCHEDULE_REVISION` repin and delivering the recompiled
`modules/catalog-yaml-policy.am` to `/opt/am/modules` wait for Marek.

Receipt: [upstream-merge-20261116.json](../upstream-merge-20261116.json).
1,591 taken from upstream, 486 re-converted, 30 fell back, 512 deleted, 9
fork-owned kept, 9,674 untouched; 34 sources to retire
([ticket 21](21-retire-catalog-sources.md)).

Decided by Marek for this merge: nothing was added to `fork-owned.txt`. The
three recipes installed on myxps that fell back (`x86_64/appimagetool`,
`x86_64/appimageupdatetool`, `x86_64/satty`) are upstream's originals again.
Consequence for `x86_64/appimageupdatetool`: a fresh install or reinstall asks
for the source again and offers the pkgforge build first; the installed copy
and its updater are not changed by the merge.

Hand-merged files were taken from the rehearsal branch; upstream did not touch
them between `448123c0a` and `ba061a639`.

Tests changed in the merge commit: `test_yaml_am_utils.py` and
`fixture_am_utils.py` removed; the `mercury` and `obs-studio.select-2`
consumer tests removed; AppImage policy count 115 to 105; unavailable recipes
49 to 0; the two enrollment replays leave the three fallen-back recipes out of
their former scope.

Checked on the merged tree: merge gate; collector suite 226 of 226;
recipe-conversion 15, recipe-reconstruction 44, upstream-merge 15.

Not passing, and not caused by the merge: `./test/e2e/run` fails 27 tests with
1 error on debian and fedora, identically on `cf9b5cc9b` and on the merged
tree ([ticket 23](23-repair-offline-e2e-after-v3-cutover.md)). `regress/` was
not run; it needs the pushed branch.
