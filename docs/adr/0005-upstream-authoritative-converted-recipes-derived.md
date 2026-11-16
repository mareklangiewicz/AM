# Upstream stays authoritative for recipes; converted forms are derived

`main-marek` keeps taking all of `upstream/main`. Upstream decides which apps
exist and what each original recipe says. A long recipe or recipe declaration
is derived from its original recipe by conversion and is never merged by hand:
when upstream changes an original, the fork takes upstream's text and re-runs
the conversion; when upstream deletes one, the fork deletes it and takes its
source out of collection enrollment; when upstream adds one, it lands as an
untouched original. Fork-owned recipes are the only exception and are named in
an explicit list that a merge never overwrites.

We chose this over a hard fork (stop merging recipes, pick runtime changes by
hand). A hard fork would end the 986-conflict merges for good, but it gives up
upstream's new and corrected recipes, makes the fork the maintainer of every app
upstream drops, and removes the path to proposing the catalog upstream, which is
the stated goal of this work.

Consequences:

- The upstream merge is one real `git merge` commit whose `programs/` tree is
  produced by a repeatable tool that writes a receipt. `am` reads this branch
  live, so history is never rewritten.
- A re-conversion that refuses falls down a fixed ladder: the same form as
  before, else a long recipe, else upstream's original. The fork never keeps a
  converted form built from text upstream has replaced; the recipe's source
  stays enrolled.
- Hand edits to a converted recipe do not survive the next merge unless the
  recipe is made fork-owned.

Decided November 16, 2026, in
[ticket 17](../track/catalog-system/issues/17-plan-upstream-merge-after-recipe-conversion.md#answer--november-16-2026).
This is a target decision; no merge has been performed.
