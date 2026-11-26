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

### November 26, 2026: measurement (`scripts/26/measure.py` on `dda1aab36`)

- URL policies: 1,464 rows from 1,391 recipes, the same 1,391 scripts that
  call `catalog-yaml.am` across all architectures. 72 recipes have more than
  one row (up to 3), keyed `<recipe>.select-N`, and the script picks one with a
  `case` on the requested repository (`aarch64/86box`). Each row has 1–4
  rules; a rule's fields are only `pattern`, `ignore_case` and `exclude`. No
  pattern holds a single quote, newline, tab or non-ASCII character, and the
  longest rule list is 274 characters as compact JSON. Channels: `any` 1,384,
  `stable` 79, `nightly` 1. 78 rows have a `catalog_app` that isn't the
  recipe's app. 58 have an alias besides the repository and its lowercase
  form. A few rows use the optional fields `selection` (40), `tag_pattern`
  (10), `tag_exclude` (1), `git_ref` (3) and `git_file` (3).
- AppImage policies: 105 rows, no recipe overlapping with the URL policies.
  Each row has the same three rule fields, an `endpoint` (`list` 96,
  `latest` 9), a `release_rule` (`published_desc` 98,
  `stable_published_desc` 7), and `selector`, the original pipeline text kept
  as evidence.
- Precedent: 8,351 recipes already declare `CATALOG_URL_RULES='[…]'` as
  single-quoted compact JSON, read by `recipe_declarations.recipe_rows`.
