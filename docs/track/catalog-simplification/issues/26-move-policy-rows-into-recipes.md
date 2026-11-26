# Move the policy rows into their recipes

Type: task
Label: implementation:task
Status: claimed
Triage: ready-for-agent
Blocked by: none

## Outcome

As decided in [Derive the collector's inputs](25-collector-inputs-from-catalog-and-recipes.md) (the
correction that replaces item 3): each row of `recipe-url-policies.json`
(1,464) and `appimage-policies.json` (105) becomes `CATALOG_*` assignments in
the recipe it names: repository id and name, channel, URL rules, aliases, and
for AppImage rows the endpoint and release rule. `recipe_policy_source.py` and
`appimage_policy_source.py` read the recipes, and the committed
`modules/catalog-yaml-policy.am` comes out byte-equal, which
`tree_generated_policy` proves. Both JSON files go, with `source_sha256`
(the recipe now holds the facts itself). `tools/upstream-merge` handles a
recipe that carries them. Install bodies don't change.

Before converting: measure how the rule lists fit shell assignments (counts,
characters in patterns, ordering), with a script under `scripts/26/`, and
settle the assignment form with Marek.

## Comments

Was "Generate the policy files in memory, not commit them". The premise was
false: the files are the facts' only home (see ticket 25's correction).
