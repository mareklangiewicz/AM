# Warn instead of refusing old catalog data

Type: task
Label: implementation:task
Status: claimed
Triage: ready-for-agent
Blocked by: none

## Outcome

As decided in [Show failures and staleness](11-show-failures-and-staleness.md):
when the selected release (or Git selection) was last seen more than 14 days
ago, AM prints one warning naming the age and continues, instead of refusing.
`--accept-stale-release`/`--accept-stale` (`APP-MANAGER`), `AM_YAML_ACCEPT`, the
stale tuple and the `fresh_non_asset_observation` refusal in
`modules/catalog-yaml-policy.am` go; `docs/catalog-operating-policy.md` states
the warning. Tests show a 15-day-old selection installing with the warning and a
13-day-old one without it.

## Implementation

Decided with Marek before the tests (November 25): `CATALOG_FRESH_ONLY` goes
too, since nothing refuses old data any more; the removed options are errors,
not ignored; one warning per app per command; the Python reference model
follows the host.

- `modules/catalog-yaml-policy.am`: the 7-day refusal, the stale tuple
  (`token`), `fresh_non_asset_observation_required` and the fresh-only refusal
  go. Past 14 days (1209600 s) the policy writes `DAYS<TAB>OBSERVED` to the file
  named by `AM_YAML_WARNING`; only `catalog-yaml.am`'s final pass sets it.
- `modules/catalog-yaml.am` prints `AM YAML catalog: warning: APP catalog data
  last seen N days ago (TIME); using it anyway` and marks `warned-APP` in the
  command cache, so a toolset's per-tool calls (`appimage.am`) and a batch warn
  once per app. `--accept-stale-release` and `AM_YAML_ACCEPT` go; the option is
  now "unsupported option".
- `APP-MANAGER` update: `--accept-stale`/`--accept-stale-release` fall to
  "Unsupported update option". `modules/install.am` refuses both by name:
  install passes unknown words on as app names, so it would otherwise install
  the rest.
- `CATALOG_FRESH_ONLY`: off `programs/x86_64/emmylua`, the generator
  (`recipes_fresh_only`, 9,869 table rows), reconstruction's setting list and
  relayout's fields. `recipe_declarations.py` ignores it, so the relayout
  replays of tickets 32/33 still compile historical trees;
  `tree_host_policy_source` refuses it in the live `programs/` tree.
- `reference_selection.py`: `stale` means over 14 days and never raises;
  `StaleSelection` and `accept_stale` go. `qualify_usable_selections.py` loses
  its `stale` outcome.
- Docs: `catalog-operating-policy.md`, `catalog-format-v3.md`, the collector
  and e2e READMEs.

Tests: an old Git and asset selection warn once and select, 13 days do not
(`test_git_consumers`, `test_custom_consumers`); one command session warns
once per app; an install on 15-day data warns once and the old option fails
before installing; a batch warns once per app and each app rechecks the clock
(`test_yaml_manager_integration`); the model at the exact 14-day boundary; the
EmmyLua toolset selects old data and reports its age; no live recipe sets
`CATALOG_FRESH_ONLY` (whole-tree tier). Long e2e: the exact 14-day CLI boundary, the
warning beside interrupted work, and the removed option.
