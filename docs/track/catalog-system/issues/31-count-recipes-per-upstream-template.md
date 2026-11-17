# Count recipes per upstream template

Type: research
Label: wayfinder:research
Status: resolved
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

## Answer — November 17, 2026

Full table, definitions, scripts and unverified points:
[template-instances-31.md](../template-instances-31.md). Measured at
`upstream/main` `ba061a639`, `main-marek` `36c087049`. Of 11,782 upstream
recipes, 11,178 are exact instances of some template version, 317 are near
misses (1 to 5 edited lines) and 287 match nothing.

Exact instances that are not declarations in our tree, top three:

1. AppImage-in-archive: 6,009 (5,346 long, 663 original); 5,980 match one
   version, `cf50304fc`, which differs from reviewed AppImage 3.6 only in
   the download step.
2. AppImage (already reviewed): 3,918; 1,233 match unreviewed `bb53f3180`,
   one line from reviewed 3.5 (desktop `sed` strips `--no-sandbox`).
3. Archive: 230, plus 85 near misses.

No multiple-choice template, including the new
`AM-SAMPLE-AppImage-muliple-variants-from-same-source`, has an exact
instance; choice recipes each write their own list. 986 originals already
match a reviewed layout, mostly recipes upstream added since the merge
base; 106 "other converted" (fifth-form) recipes remain, 104 of them exact
reviewed-layout instances upstream. Recount: 1,029 declarations and 8,767
long recipes (README: 984 and 8,770); spot-checked with `merge.form()`.

