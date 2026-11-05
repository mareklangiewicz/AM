# Historical catalog tooling retirement

Ticket [118](../issues/118-retire-historical-catalog-tooling.md) implements the
[117 inventory](historical-tooling-dependencies.md). Previous runnable historical
source is available at `007ea4871`; no archive copy is kept in the maintained tree.
The [retired path list](retired-tooling-files.txt) enumerates 172 tracked paths.

## Maintained surface

- Publication: `host_catalog.py`, `yaml_publication.py`, `publication.py`,
  `bounded.py`, `retention.py`, `writer.py`, `recipe_declarations.py`.
- Maintenance: `host_cutover.py`, `recipe_refresh.py`, `installed_recipe.py`.
- Registry compilation: `recipe_policy_source.py` plus the transitional
  `appimage_policy_source.py` and its retained policy data.
- Tests: current declaration, selector, reader, normalization/retention,
  collection/publication, installer/update and metadata-refresh checks. Explicit
  `fixture_*.py` and `reference_*.py` support them; these have no historical CLI.

The current collector's local Python import closure shrank from 18 modules to 7:
`host_catalog`, `bounded`, `publication`, `recipe_declarations`, `retention`,
`writer`, `yaml_publication`. Cutover adds only `host_cutover` and
`installed_recipe`. Metadata refresh still needs only `recipe_refresh`,
`installed_recipe` and `recipe_declarations`. No current root imports fixtures,
reference policies or retired collector/delivery/transport modules.

`publication.py` now contains only the reused local Git writer and bounded read
implementation. `yaml_publication.schema_url` no longer imports the historical
collection bridge. Snapshot validation directly invokes the distributed reader;
compatibility reader wrappers were removed. Read Git environments carry no token.
Output/time/history limits, Git environment isolation, remote refusal, exact-parent
checks and atomic ref update remain exercised by current publication tests.

## Retired surface

Removed the old format-1 collector, storage/reader/consumer model, credentialed
transport/workflow adapter, artifact delivery, shard dispatcher, enrollment,
staging, migration, acceptance/audit/replay commands and operation-only tests.
The manual quota/churn probe workflow and its tooling were removed. All runnable
YAML prototype commands and prototype-local results were removed from the working
tree; their source/results remain in Git history. The one-time format-1 bootstrap
option was removed from current publication and its workflow.

Fixtures still needed by current selector/installer tests were promoted as small
loaders over hash-checked saved responses. Reader, normalization, retention and
shared-observation contract tests were promoted from experiments into normal
unittest discovery. The remaining 472 recipes' transitional selection behavior,
generated runtime registry, all recipe bytes and collection enrollment are unchanged.

Whole-command Debian/Fedora and native Termux tests now author current YAML facts
without importing historical storage/migration code. General install/update,
removal/reinstall, source ownership, mixed-batch, failed/partial/interrupted transfer
and retry checks remain. Migration-only utility/Brave/container batches were
retired; portable transitional selector/installer coverage remains in the main
suite. Fixtures now follow the delivered staging cleanup and malformed-catalog
batch refusal contracts. The native Termux migration exposed an existing awk
compilation bug, fixed separately in [119](../issues/119-fix-native-termux-yaml-parser.md).

## Retained evidence and operation

Historical specs, manifests and saved upstream/deployment evidence under
`docs/track/` remain. References in those historical records describe their source
revision; consult Git history for retired executable paths. Ignored local logs,
installed application data and `/home/marek/Documents/Codex/am-yaml-cutover/`
recovery evidence were not removed. No live installation, module sync, workflow
dispatch, catalog publication, enrollment change, push or yadm operation occurred.

Validation results and limits are recorded in ticket 118: the broad run passed
128 cases; the one obsolete historical oracle was retired and its retained direct
selector replacement passes separately. All 56 whole-command container cases,
11 helper/reader cases and five final publication cases pass. No full-discovery
rerun is claimed after the test-only oracle cleanup.
