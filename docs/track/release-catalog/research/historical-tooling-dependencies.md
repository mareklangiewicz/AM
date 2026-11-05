# Historical tooling dependency inventory

Source inspected: `7cb32057a0629bbd47ea61c73819078ca2ae2ef5`, November 5, 2026.
Ticket: [117](../issues/117-inventory-historical-tooling-dependencies.md).

## Current roots and import reachability

`.github/workflows/catalog.yml` runs `host_catalog.py`; collection enrollment is
`collection-recipes.txt`. Maintained metadata refresh runs `recipe_refresh.py`;
registry compilation runs `recipe_policy_source.py`. `host_cutover.py` is the
maintenance reinstall tool documented in the operating policy.

Static inventory parsed every `tools/catalog-collector/*.py` with Python `ast`,
collecting local `Import` and `ImportFrom` module names, including imports inside
functions, and taking their transitive closure. These are conservative module
relationships, not proof that every reachable function executes. No imported
code, network request, publication or installed command was executed.

| Root | Local Python closure, including root |
| --- | --- |
| `host_catalog` | `attempt_adapter`, `bounded`, `collector`, `delivery`, `host_catalog`, `manifest`, `publication`, `reader`, `recipe_declarations`, `retention`, `shell_lookup`, `storage`, `supervised_transport`, `workflow_adapter`, `writer`, `yaml_adapter`, `yaml_publication` |
| `host_cutover` | The preceding closure plus `host_cutover`, `installed_recipe` |
| `recipe_refresh` | `installed_recipe`, `recipe_declarations`, `recipe_refresh` |
| `recipe_policy_source` | `recipe_declarations`, `recipe_policy_source` |

Shell/process dependencies need separate treatment: `host_cutover.py` invokes
`modules/catalog-yaml-reader.am` and `modules/catalog-yaml-policy.am` directly;
`yaml_publication.decode_document` invokes `reader.sh`; `recipe_refresh` checks
rendered recipes with `sh -n`. AST imports alone omit these dependencies.

## Why historical-looking files remain connected

- `host_catalog` imports `schema_url` from `yaml_adapter`, whose module imports
  the historical collector/manifest and `attempt_adapter`. This is a small value
  helper pulling in a much larger module interface.
- `host_catalog` and `yaml_publication` use `publication.git` and the local Git
  publisher. `publication` also imports format-1 storage validation, manifest and
  descriptor types for its older functions. Removing it breaks current publication.
- `yaml_publication` imports `delivery.bounded` and `delivery.environment` inside
  its fetching implementation (line 120 at the inspected revision). `delivery`
  imports `workflow_adapter`, which imports `supervised_transport`. This is a real
  dependency in source, despite the retired workflow wiring.
- `reader` and `shell_lookup` still use collector validation/time helpers and
  storage functions. Shared helper reuse does not make all historical operational
  entry points current, but prevents deleting their modules as a single batch.

## Staging, packaging and test callers

| Tool | Direct local Python importers |
| --- | --- |
| `yaml_staging` | `yaml_delivery`, `yaml_workflow`, `test_yaml_delivery`, `test_yaml_publication_delivery`, `test_yaml_staging` |
| `yaml_delivery` | `yaml_workflow`, `test_yaml_delivery`, `test_yaml_publication_delivery` |
| `yaml_installed_migration` | `yaml_cutover_package`, `yaml_legacy_staging`, `test_yaml_host_rehearsal`, `test_yaml_installed_migration` |
| `yaml_cutover_package` | `legacy_updater_audit`, `test_legacy_updater_audit`, `test_yaml_cutover_package`, `test_yaml_host_rehearsal` |

Cross-directory text searches additionally found `yaml_staging` imports in
`tools/catalog-yaml-prototype/capacity.py`, `host_capacity.py` and
`sunshine_growth.py`. These prototype callers are outside the collector-only graph.
The current maintenance root `host_cutover` no longer imports
`yaml_installed_migration`, consistent with ticket 115; historical packaging still
does. The tests therefore span maintained behavior and historical experiments.
Do not remove test files merely because their names or subjects look old.

## Bounded next proposal

First isolate the local Git publication/fetch implementation reused by current
YAML publication from format-1 validation and historical workflow delivery.
Preserve environment isolation, output/time/history bounds, remote-free local
publication, exact-parent refusal and atomic ref advancement. Existing historical
callers should reuse the extracted implementation until explicitly retired.
Keep this behind a small publication interface; do not add a second publisher or
new configuration framework. Before implementation, claim a separate task with
exact moved functions and focused current/historical caller checks.

A smaller independent opportunity is moving `schema_url` to a format/schema module
shared by `host_catalog` and `yaml_adapter`; this alone does not disconnect the
historical closure through publication/fetching and should not be described as
retiring the old collector.

## Limits

This is a first dependency inventory and follow-up proposal, not a validated
removal list or full conversion design. Dynamic imports, shell command construction,
external/local recovery scripts and every historical CLI caller have not been
exhaustively classified. The static graph over-approximates conditional imports.
No test suite was run for this documentation-only result. The 472 transitional
format-2 recipes and their selector policies remain outside this cleanup scope.
