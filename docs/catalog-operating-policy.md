# Single-user YAML catalog operation

Marek's fork now uses the YAML catalog for the 21 installed applications named in
`tools/catalog-collector/host-apps.json` (19 numeric repository identities). This
is the production enrollment manifest. The older 50-source design manifest and
format-1 collector experiments are historical evidence, not active publication.
The source cap remains 52; per-repository YAML remains capped at 2 MiB.

`.github/workflows/catalog.yml` collects one page of 100 releases per source daily
at 03:17 UTC or on manual dispatch, retains previously observed releases and
publishes validated YAML to `release-catalog`. Failed collection leaves the
previous publication in place. The first cutover explicitly replaces the old
format-1 tree with a child commit; old commits remain available. The old collector,
sharded dispatcher and schedule workflows are removed. There is one catalog
publication format and no format-1 fallback. The retired `catalog.am` is an error
message for old installed recipes, not a format-1 consumer.

Clients choose by publication time descending, then numeric release ID; eligible
assets sort by bytewise name then numeric ID. Stable channels exclude prereleases
and the nightly tag; nightly channels require exactly that tag. App-specific
patterns and x86_64 platform exclusions are compiled from the manifest. These are
explicit client policies, not GitHub's latest designation. Neovim/Neovide nightlies
refresh on each update, matching their reused URLs. Logseq DB nightly uses its
release publication timestamp as its version and retains the actual download URL
separately. Other apps compare selected URLs. Changed bytes behind an unchanged
URL otherwise require an explicit reinstall (or checksum-repair flag).

The selected release observation must be no older than 48 hours, independent of
publication time. The helper prints an exact `--commit`/`--accept-stale-release`
retry tuple when a single asset is stale. EmmyLua is deliberately fresh-only:
all four musl tools must be fresh, distinct catalog assets of the same release
and publication. Refresh the catalog instead of coordinating stale consents.

Every acquisition is an ordinary download of the catalog-selected URL. Embedded
AppImage updaters no longer choose a different target. The old AppImageUpdate
actual-URL patch is preserved in
`track/release-catalog/research/appimageupdatetool-before-yaml.sh.txt`. This does
not claim that URL identity verifies a binary digest or publisher authenticity.

## Maintenance-window reinstall

`tools/catalog-collector/host_cutover.py prepare` stages every selected asset in
a private directory and exercises the delivered archive extraction code. `apply`
saves the previous manager/modules, installed recipe/updater/version/remover and
launcher metadata, then overlays program files. It never executes an old remove
script, deletes an app directory or edits home configuration. Existing desktop
entries and custom executable launchers are preserved. Existing app data stays
in place. Program files are replaced by rename so a running executable is not
truncated. Multi-file replacement is not atomic.

Local source, downloaded assets, staged payloads, selections, smoke output and
catalog Git objects are under `/home/marek/Documents/Codex/am-yaml-cutover/`.
The persistent development worktree is `source/`; `prepared/` contains the app
payloads. `before/` inside the chosen prepared directory is created only on live
application. This directory is local and is not shipped with source pushes.

Recovery is to rerun the prepared apply or reinstall the affected app after fixing
the cause. Restore `before/APP-MANAGER` and `before/modules/` if the manager itself
needs reverting. Old updater/recipe/version metadata and launcher targets are
also saved, but that does not restore old binaries. The previous format-1 catalog
commit is retained in history and in `catalog-report.json` if an old managed
recipe needs an explicitly pinned old catalog. No durable binary transaction,
power-loss guarantee or automatic rollback service is provided.

## Checks

The actual manager installation path and standalone updaters were exercised for
all 21 recipes with inert assets. Additional checks cover failed downloads,
failed archive extraction, custom launchers/data retention, explicit format-1
refusal and fresh-only EmmyLua. Existing manager mixed-batch, source-binding and
AppMan-path checks passed. All 21 real staged payloads passed `--version` or
`--appimage-version` probes; the latter checks the AppImage runtime, not the GUI.
GUI startup and a natural daily catalog cycle remain post-cutover observations.


Live cutover completed November 5, 2026, at source 88ca89f30. All 21 apps now
have installed YAML recipes and managed updaters. The first
[YAML publication run](https://github.com/mareklangiewicz/AM/actions/runs/42007220573)
succeeded. Seven actual manager update cases passed, including a real nightly
AppImage refresh; original desktop entries, removers and executable-link targets
were verified preserved. Before-images are in `prepared/before/` under the local
cutover directory. Logseq's generic checksum UI still treats its version timestamp
as a missing URL; the selected URL remains in download-url and updates succeed.

## Recipe launcher settings

The host manifest compiles recipe settings through `host_policy_source.py`.
`EXTRA_APP_LAUNCHERS` is an optional space-separated list of additional command
names pointing to the installed root executable `$APPS_DIR/$APP/$APP`. Names
must be simple basenames; dot-prefixed names and the main app name are refused.
The shared installer creates these links, preserves existing custom launchers,
and generates removal commands that delete aliases only while they still point
to that executable. This setting does not describe executables inside archives.

`DESKTOP_EXEC` defaults to `command`, preserving existing desktop behavior.
`installed` uses the quoted absolute root executable in newly generated desktop
entries, keeping their arguments and field codes. Existing desktop entries remain
preserved. Other values are refused before downloading or installing anything.

Obsidian declares `EXTRA_APP_LAUNCHERS=obsidian-gui` and `DESKTOP_EXEC=installed`.
The shared lifecycle contains no Obsidian identity checks. Official CLI registration
at `~/.local/bin/obsidian` remains independent. Existing installed recipes are not
rewritten by module sync; these declarations arrive through the current source
recipe on install/reinstall. Existing user GUI aliases/desktop overrides need no
migration. [Archive adapter follow-up](track/release-catalog/issues/112-separate-host-archive-adapters.md)
records the remaining app-specific archive/layout knowledge in shared code.

### Host archive adapters

`tools/catalog-collector/host-apps.json` owns the reviewed host archive roots,
required executable paths and launcher mappings. `host_policy_source.py` compiles
these into `modules/archive-policy.am`; edit the manifest and regenerate, rather
than editing the generated module. `raw` and flat `tar` retain shared defaults.
Existing `PACKAGE_LAYOUT` values select these app-owned adapters, so module sync
can update machinery without rewriting installed recipes. The manager's module
list includes the adapter module, including first delivery to older installations.

The shared installer performs downloads, archive checks, staging, replacement and
launcher ownership handling. The manifest's EmmyLua tool list drives both archive
staging/launchers and catalog asset selection; `fresh_only` rejects stale consent
in the trusted policy before acquisition. All selected tools must match the first
selection's repository and release at its pinned publication. The maintenance
cutover helper uses the same manifest mappings. This source change requires no
reinstall; deployment is an ordinary separately chosen module synchronization.
