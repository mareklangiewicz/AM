# Build the upstream merge tool and run the first merge

Type: task
Label: implementation:task
Status: open
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
