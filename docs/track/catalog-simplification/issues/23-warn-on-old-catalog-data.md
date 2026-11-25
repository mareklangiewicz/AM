# Warn instead of refusing old catalog data

Type: task
Label: implementation:task
Status: open
Triage: needs-triage
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
