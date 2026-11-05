# Retire historical catalog tooling

Type: task
Status: resolved
Triage: ready-for-agent

Marek authorized completing retirement after inventory 117. Disconnect current
YAML publication from historical collector/delivery imports, retaining isolated
Git execution, bounded reads, history limits, remote-free publication and exact
parent checks. Remove retired collection/workflow/staging/migration commands and
their experiment-only tests and prototype callers. Promote fixtures and contract
tests still needed for current publication, reader, selector, installer and refresh.
Retire format-1-only container scenarios and keep a usable current offline container
runner. Leave tracked historical evidence and local deployment recovery untouched.
Preserve all runtime recipes, transitional selector policies and collection scope.
Validate the complete remaining offline suite and commit. No push/deployment.

## Implementation and validation

Retired 172 historical tracked paths (about 25,000 net lines): format-1
collector/storage/consumer, credentialed transport/workflow and shard/artifact
delivery, staging/enrollment/migration/acceptance/replay commands, quota/churn
probe workflow and the runnable YAML prototype tree. Removed the completed
format-1 bootstrap option. Historical source/results remain at `007ea4871`.
[Retirement report](../research/historical-tooling-retirement.md) records the keep
surface and links the exact retired path list.

Promoted the shared Git publication/bounded-reader implementation, isolated schema
URL construction and direct distributed-reader validation. Current collection's
local import closure is seven modules, down from eighteen. No current root imports
retired modules. Kept transitional recipe policy data/compiler and current
selection/installer coverage. All recipe bytes, generated selector registry and
collection enrollment remain unchanged. Native Termux parser compilation was
fixed separately in 119 (`1c1b4e7e4`); no runtime deployment accompanied it.

Promoted reader, normalization, retention and shared-observation contract tests
and only the saved-response fixture loaders needed by current tests. Whole-command
container fixtures now use current YAML facts. Historical migration-only scenarios
were removed; general install/update, AppMan, remove/reinstall, source ownership,
mixed-batch, failed/partial/interrupted transfer and retry cases remain.

Completed verification:

- Broad maintained-suite discovery ran 129 tests in 886.991 seconds: 128 passed,
  including the 115-policy lifecycle group (matching installs/updaters and
  no-match refusal paths). The sole error
  was an obsolete historical comparison calling the already-removed
  `am_appimage_select_asset` shell function. Removed that oracle and its fixture
  helper; retained direct adversarial selection checks against the independent
  reference and mawk/GNU awk/BusyBox awk. The corrected standalone test class
  passed in 23.649 seconds. Complete declarations use their own compiler/lifecycle coverage instead
  of the transitional registry's historical oracle.
- Five current publication tests pass on the final helper source, exercising
  offline all-enrolled collection, failed-collection preservation, pinned reads,
  exact-parent and remote refusal, history/byte/time limits and Git environment
  isolation.
- Eleven e2e helper/reader tests pass. The reader portability regression also
  passes separately with mawk, GNU awk, BusyBox awk and native Termux GNU awk.
- Whole installed command matrix: Debian 21/21, Fedora 21/21, native Termux 14/14,
  with networking disabled and source mounted read-only. Final receipts/logs are
  under `/tmp/am-retirement-e2e-{debian,fedora,termux}-final/` locally.
- Retained Python sources parse; shell runner syntax, staged whitespace checks
  and static imports against the retired path list pass.

The expensive full discovery was not repeated after deleting the obsolete test
oracle; the corrected direct selector class was rerun instead. Early extraction
and fixture migration failures were corrected before the final targeted/container
runs. No independent agent review is claimed. No push, installed metadata change,
module synchronization, publication/dispatch, enrollment or yadm operation.
