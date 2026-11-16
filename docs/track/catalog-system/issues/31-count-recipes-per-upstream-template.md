# Count recipes per upstream template

Type: research
Label: wayfinder:research
Status: open
Blocked by: none

## Outcome

A table: for each of upstream's 15 `templates/AM-SAMPLE-*`, how many recipes
per architecture are instances of it, and how many of those are long recipes
or originals today. Marek uses it to pick the next template to review into a
shared installer.

## Why

Marek, November 16, 2026: "did upstream add more templates? can we use them to
match more recipes as 'standard' and support more of them as short declarative
recipes?" Only the plain AppImage template is reviewed
(`tools/recipe-conversion/layouts.json`, two versions), so recipes built from
the other 14 can be long recipes at best
([ADR 0006](../../../adr/0006-recipe-declaration-is-the-preferred-form.md)).

## Scope

- Match against upstream's originals (`upstream/main`), since long recipes
  keep the install steps but replace the selection.
- A template has had several versions; match each recipe against the
  template's history, as `layouts.json` does for the AppImage one, and report
  near misses (a few edited lines) separately from exact instances.
- Between merge base `7b4f831e6` and `ba061a639` upstream added
  `AM-SAMPLE-AppImage-muliple-variants-from-same-source` and edited three
  multiple-choice templates (`git diff --stat`, November 16, 2026).
- No conversion and no new module in this ticket.

## Comments
