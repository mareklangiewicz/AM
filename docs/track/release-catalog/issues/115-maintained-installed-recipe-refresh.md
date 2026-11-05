# Maintain installed recipe binding and metadata refresh

Type: task
Status: resolved
Triage: ready-for-agent

After 114, Marek requested push and continuation. Implement the deferred small
source-only maintenance slice: shared Python recipe binding/updater primitives
and a metadata-only refresh command for an explicitly selected installed recipe.
Reuse these primitives from cutover helpers; remove the live helper's dependency
on the historical migration module. Keep the shell-only installer independent of
Python and verify its updater output agrees with the maintained primitive.

Preview before writing. On explicit apply, back up recipe and source snapshot,
preserve installed paths and configured source owner, require reviewed old hashes,
and verify the managed updater instead of replacing arbitrary custom updaters.
Do not execute recipes, download/reinstall binaries, sync runtime, change launchers,
introduce a generic migration/rollback framework or perform live deployment.
Test disposable installations, drift refusal, custom updater refusal, and quoted
paths. Historical scripts under Documents remain recovery evidence, untouched.

## Answer

Added maintained `installed_recipe.py` for compact recipe binding, installed path
reading and exact managed updater rendering. Cutover packaging and the historical
migration helper reuse it; live `host_cutover.py` no longer imports the historical
migration module. Cutover selection/source lookup now uses the declaration's
recipe identity instead of rebuilding an x86_64 identity.

Added `recipe_refresh.py`: preview one explicitly selected installation against a
full local source commit; explicit apply requires reviewed old recipe/snapshot
hashes and a fresh external backup directory. It validates complete declarations,
installed identity and module/helper consistency, preserves configured repository
ownership and paths, refuses custom updaters/symlink metadata/drift, and replaces
only recipe and source snapshot while preserving modes/ownership. No installed
scripts are executed. Pair replacement is not atomic; exclusive maintenance and
manual recovery limits are documented. No generic migration framework or runtime
synchronizer was added.

Validation: four new refresh tests, nine cutover-package tests and all 16 installed
app/cutover groups pass (29 distinct tests). The all-21 actual installer/standalone
update case was additionally rerun after adding exact shell/Python updater byte
comparison and passes. Checks include quoted paths/arguments, configured custom
source ownership, backups, preview without mutation, drift/custom updater refusal,
and preservation of other app metadata. Python compilation and diff whitespace
checks pass. One initial targeted test invocation used the wrong module directory;
it was corrected and rerun successfully. No independent agent review is claimed.

The earlier source through 01241d2d3 was pushed as explicitly requested. This new
maintenance slice is committed separately; no live refresh, runtime synchronization,
publication, workflow dispatch or yadm changes were performed.

## Deployment follow-up

Marek requested push and deployment. Source 14adf6fd1 was pushed; deployment 116
used the maintained refresh operation for all 21 installed recipe/snapshot pairs,
coordinated with the two changed runtime modules. See
[116](116-deploy-common-recipe-declarations.md) for verification and backups.
