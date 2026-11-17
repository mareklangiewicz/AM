# Convert AppImage `bb53f3180` instances to declarations

Type: task
Label: implementation:task
Status: open
Blocked by: none

## Outcome

Recipes whose upstream original is an instance of AppImage template
`bb53f3180` become recipe declarations, ticket 31's cheapest gain.

## Step 1, done November 17, 2026: the layout is reviewed

`bb53f3180` ("Remove --no-sandbox nonsense in AppImage's templates (#1717)")
differs from reviewed 3.5 `b7c72a974` by one line: the desktop `sed` gains
`s# --no-sandbox##g` (`git diff b7c72a974 bb53f3180 -- templates/AM-SAMPLE-AppImage`).
That line is what `DESKTOP_STRIP_NO_SANDBOX=true` does in
`modules/appimage.am` (ticket 32), so `tools/recipe-conversion/layouts.json`
lists it with that setting. Conversion and merge suites pass (17 and 16
tests). Effect today: none on the tree; the merge tool may now re-convert
upstream changes of these recipes into declarations.

Three existing declarations match it: `5ire` and `actiona` already set the
flag; `obsidian` is a deliberate hand conversion (release-catalog ticket 109
keeps `--no-sandbox %U` and sets `DESKTOP_EXEC=installed`) and was left.

## Step 2, open: convert the long recipes

Dry run at `main-marek` `d85c3851b`, `upstream/main` `ba061a639`: of the
upstream originals that are exact `bb53f3180` instances, 1,171 long recipes
convert to declarations with the identities from their rows in
`tools/catalog-collector/recipe-url-policies.json` (`convert.policy_identities`);
3 long recipes refuse (2 "unsupported selector pipeline", 1 "no verified
catalog source"), 1 original refuses ("app identity"). Script logic: for each
`upstream/main` recipe that `convert.recognize` matches against this layout
alone, convert to `declaration` with the recipe's current identities.

Still to work out before writing anything:

- How the converted recipes' policy rows leave `recipe-url-policies.json`
  and what regenerates (`recipe_policy_source.generate`, enrollment); the
  merge tool's `derive` may already do it.
- It changes live collection input, so it needs its own push, a repin of
  `CATALOG_SCHEDULE_REVISION` and an observed scheduled run (as ticket 25
  step B).
- Ticket 31 counted 1,236 instances (1,183 long, 50 original) with a looser
  matcher; this dry run found 1,178. Not reconciled.

## Comments
