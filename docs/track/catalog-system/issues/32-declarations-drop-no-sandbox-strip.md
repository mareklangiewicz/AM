# Declarations from template 3.6 drop the `--no-sandbox` strip

Type: grilling
Label: wayfinder:grilling
Status: open
Blocked by: none

## Outcome

Marek decides whether a declaration converted from a template version that
strips `--no-sandbox` must set `DESKTOP_STRIP_NO_SANDBOX=true`. That
decision covers the 579 existing declarations and any further review of
AppImage `bb53f3180` (ticket 31's second-ranked template).

## Evidence (November 17, 2026, `main-marek` `36c087049`)

- Upstream `bb53f3180` ("Remove --no-sandbox nonsense in AppImage's
  templates (#1717)") added `s# --no-sandbox##g` to the desktop `sed` of
  `templates/AM-SAMPLE-AppImage`. Reviewed layout 3.6 (`cf50304fc` in
  `tools/recipe-conversion/layouts.json`) carries that line; reviewed 3.5
  (`b7c72a974`) does not.
- `convert.to_declaration` passes only `APP` and `CATALOG_ALIAS` to
  `bulk_recipes.declare`; nothing maps the template's strip to
  `DESKTOP_STRIP_NO_SANDBOX`. `modules/appimage.am` strips only when that
  setting is `true` (default `false`), so the declared install keeps
  `--no-sandbox` in `Exec=` where the AppImage's own desktop file has it.
- Of 1,029 declarations: 579 match `cf50304fc` both at merge base
  `7b4f831e6` and on `upstream/main` `ba061a639` and do not set the flag;
  398 match 3.5 (no strip upstream either, correct); 6 match 3.6 and set the
  flag; the rest are hand conversions. Counted with `convert.recognize` over
  `merge.recipes` and `merge.form` (script in this session; logic: for each
  declaration, recognize its upstream original against `convert.layouts()`
  plus `bb53f3180`, group by template and by presence of
  `DESKTOP_STRIP_NO_SANDBOX=true`).
- `docs/catalog-operating-policy.md` describes the opt-in as retaining the
  "original fork recipe behavior" (20x and tickets 133/135). The bulk
  conversion at `6277377ae` did not apply that rule to 3.6 instances. The
  release-catalog map still says "upstream's 3.6 template requires a
  separate revision review"; `layouts.json` lists 3.6 because ticket 18
  reproduced the bulk conversion byte for byte, not after such a review
  (inference from commit `e23779424`'s message).

## Not verified

- How many of the 579 AppImages actually ship `--no-sandbox` in their
  desktop file (needs payloads; not fetched).
- The rest of the 3.5 → 3.6 diff (multiple launchers, `./*-AM.desktop`)
  against `modules/appimage.am`.
- The shared installer's strip is narrower than the template's
  (`Exec=` lines, space-delimited); treated as equivalent by the policy doc.

## Options

1. Map the strip: `convert.py` sets `DESKTOP_STRIP_NO_SANDBOX=true` for
   layouts containing the line; re-convert the 579; the corpus tests pin
   them as deliberate differences from `6277377ae`. Then `bb53f3180` can
   join `layouts.json` with the same mapping (1,233 more instances).
2. Accept the drop as policy and document it (keeps `--no-sandbox`, which
   upstream removed on purpose).

Recommendation: option 1. ADR 0005 makes converted forms derived from
upstream, and the policy doc's own rule is to keep the original's behavior.

## Comments
