# The recipe declaration is the fork's preferred recipe form

A recipe declaration has no install steps of its own: it names the app, its
catalog source and its packaging, and a shared installer module the fork has
reviewed does the rest. A reader can therefore trust it without reading shell.
That is one of the main advantages of this fork, so the declaration is the form
every recipe should reach. The browser shows which apps lack one, as a signal
to read the recipe carefully before installing.

A long recipe is the fallback: what a recipe is until a reviewed template
covers it. No work goes into improving long recipes as such, only into moving
them to declarations by reviewing further upstream templates. The refusal
ladder of [ADR 0005](0005-upstream-authoritative-converted-recipes-derived.md)
is unchanged: declaration, else long recipe, else upstream's original.

We considered retiring the declaration to leave fewer forms (original, long,
fork-owned). It would have simplified the upstream merge and given up the
property the fork exists to offer.

Consequences:

- Only the plain AppImage template is reviewed today (two versions in
  `tools/recipe-conversion/layouts.json`), out of 15 upstream templates. Each
  further template needs its own shared installer module and review; which one
  comes next is decided by a count of the recipes that match it.
- The "Shared installer" label of
  [ticket 06](../track/catalog-system/issues/06-choose-evidence-bound-recipe-classification-and-provenance.md)
  is what the browser shows for a declaration.

Decided November 16, 2026, in
[ticket 24](../track/catalog-system/issues/24-simplify-and-unify-catalog-process.md#answer--november-16-2026).
