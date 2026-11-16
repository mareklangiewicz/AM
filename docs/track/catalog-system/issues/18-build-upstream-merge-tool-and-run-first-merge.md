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
- Find out whether an original recipe can be converted straight to a recipe
  declaration; if not, say what the ladder's first rung costs to build.
- Hand-merge `APP-MANAGER`, `modules/install.am` and `README.md`.
- The four-part gate from ticket 17, decision 7.

Pushing the merge and any installed-host action need Marek's specific
authorization. Merge, never rebase.

## Comments

November 16, 2026: opened from ticket 17's answer. Unassigned.
