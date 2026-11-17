# Convert AppImage `bb53f3180` instances to declarations

Type: task
Label: implementation:task
Status: resolved
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

## Step 2, done November 17, 2026: convert the long recipes

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
  matcher; this dry run found 1,178. Reconciled below (comment of November 17).

## Comments

November 17, 2026 (review): the 1,236 vs 1,178 gap reconciled. Both counts use
the same matcher, `originals.Template.match` after `convert.QUOTING`; the 1,236
are all its `bb53f3180` matches on `upstream/main` `ba061a639` (1,233 of them
not yet declarations, the figure in ticket 31's answer and the map). The 1,178
are the ones `convert.recognize` also accepts. Forms at `d85c3851b` (the same
as at ticket 31's `36c087049`):

| Form | Instances | `recognize` accepts | Refused by `recognize` |
| --- | ---: | ---: | --- |
| long | 1,183 | 1,174 | 9: installer and updater disagree (aarch64 `cartridges`, `extension-manager`, `gearlever`, `varia`; x86_64 `dbgate`, `dbgate-premium`, `gale`), SITE not a literal repository (x86_64 `leapp`, `owncloud`) |
| original | 50 | 1 (`x86_64/container-desktop`) | 49 |
| declaration | 3 | 3 (`5ire`, `actiona`, `obsidian`) | 0 |
| total | 1,236 | 1,178 | 58 |

Of the 1,174 long recipes, 1,171 converted and 3 refused later in
`convert.convert` (the two `python` ones and `deadbeef-nightly`, as in the
answer); the one original is the "app identity" refusal of the dry run. At
`082502f64`: 1,174 declarations (1,171 plus the 3 earlier), 12 long, 50
originals. The script (session scratchpad, not kept) ran `merge.form` on each
tree blob and `convert.recognize` against the `bb53f3180` body alone.

## Answer — November 17, 2026

1,171 long recipes became declarations, converted from their `upstream/main`
originals with the identities of their own policy rows
(`convert.policy_identities`). Three refuse and stay long: `aarch64/python`
and `x86_64/python` (unsupported selector pipeline), `x86_64/deadbeef-nightly`
(app identity: upstream's `APP` differs from the file name).

The derived files come from the merge tool itself: one row per recipe
(`re-converted` for the 1,171, `untouched` for the rest) passed to
`merge.derive` and `merge.stage`, exactly as a merge would. Result:
`recipe-url-policies.json` loses the 1,171 recipes' rows and
`modules/catalog-yaml-policy.am` is recompiled (4,661,192 to 4,539,232
bytes); collection enrollment (`collection-apps.json`,
`collection-recipes.txt`), `unavailable-github-recipes.json` and the AppImage
test policies are unchanged; no source to retire. A fresh
`recipe_policy_source.generate()` on the written tree gives the same module.

Equivalence: for every converted recipe, the compiled selection row before
(`url_policy_rows`) and after (`recipe_rows`) agrees on repository id and
name, channel, asset pattern, URL rules, catalog app and fresh-only; every
other policy row is unchanged (checked in a temporary worktree of the
written state). Install steps move from the template text to
`modules/appimage.am` with `DESKTOP_STRIP_NO_SANDBOX=true`, per step 1.

Script (session scratchpad, not kept): for each `long` recipe at HEAD whose
`upstream/main` original `convert.recognize`s against the `bb53f3180` layout
alone, `convert.convert(original, recipe, 'declaration', identities, [layout])`;
then `files=merge.derive(ROOT,'HEAD',rows)`,
`files[POLICY]=merge.stage(ROOT,'HEAD',rows,files)`, write recipes and files.

November 17, 2026: pushed as `082502f64` with Marek's approval;
`CATALOG_SCHEDULE_REVISION` repinned (09:53Z). Fast tests 44059702917 passed.
No scheduled run came within an hour, so a dispatched catalog run served as the
observed run: 44069990694, acquire and publish both green. Locally before the
push: tool suites, fast tier (221), whole-tree tier (5), Debian and Fedora e2e
(21 each) all passed.
