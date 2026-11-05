# Single-user YAML catalog operation

Marek's fork uses the YAML catalog for the 21 host recipes marked
`# AM-HOST-RECIPE 1` under `programs/x86_64` (19 numeric repository identities).
Those recipes are the production enrollment and customization source of truth. The older 50-source design manifest and
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
patterns are compiled from the recipes; x86_64 platform exclusions stay shared. These are
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

Edit host recipe declarations directly. `host_policy_source.py` compiles their
selection settings into the trusted policy registry and never rewrites recipes.
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
migration.

## Recipe archive and selection settings

Each marked host recipe owns its repository identity (`CATALOG_REPOSITORY_ID`,
`CATALOG_REPOSITORY`), channel (`CATALOG_CHANNEL`) and asset pattern
(`CATALOG_ASSET_PATTERN`), alongside its launcher, refresh and version settings.
Keep the declaration header literal: one shell assignment per line, with shell
quoting for spaces and patterns. `host_recipes.py` reads it without executing shell.
The collector and maintenance cutover read these same recipes. Run
`python3 tools/catalog-collector/host_policy_source.py` after selection changes,
and commit the regenerated `modules/catalog-yaml-policy.am` with the recipe.
The generated registry serves direct catalog clients; it is not another source to
edit. No JSON host manifest or app-named archive adapter registry remains.

`PACKAGE_LAYOUT` is one of `raw` (default), `tar`, `zip`, or `toolset`.
`PACKAGE_KIND` distinguishes an AppImage from an executable package.
`ARCHIVE_ROOT` defaults to `.` and may be a glob matching exactly one extracted
directory. `PACKAGE_EXECUTABLES` lists required executable paths relative to that
root; the default is the app name. `PACKAGE_LAUNCHERS` is a space-separated list
of `command:relative/path` mappings, defaulting to the app name and root executable.
Kitty declares both `bin/kitty` and `bin/kitten` here; shared code knows neither name.

For `toolset`, `PACKAGE_TOOLS` lists tools in selection order, with the primary
asset first. Each selected tar archive must contain its tool at the root.
Executables and launcher mappings are derived from that one list. Asset selection
uses `CATALOG_TOOL_ASSET_SUFFIX`; `CATALOG_FRESH_ONLY=true` refuses stale consent
before HTTP. All selections must have the same repository/release at the pinned
publication, and each selected observation must be fresh. EmmyLua declares these
settings locally. No arbitrary installation hooks are introduced.

### Installed recipe refresh

This source revision deliberately drops old app-named layout aliases and legacy
launcher-target inference. Custom launchers remain preserved unless they already
point to the exact declared target. Recipes installed before this change still
contain old declarations: a module sync alone does not convert them. Refresh
installed archive recipes together with the shared module when deploying; the
old named layouts fail before catalog/download work with an explicit recipe
refresh message. Do not claim deployment complete from module sync alone.
The source refactor itself performed no live installation or module synchronization.


November 5, 2026 deployment: after explicit push and deployment authorization,
source `e4c84b154803a2ac3e3ac432ba3d0aa9409c2d95` was pushed and deployed on myxps.
The three changed runtime modules and the installed btop, Kitty, rclone and EmmyLua
recipes were refreshed together; their `.am-installer` source snapshots were also
refreshed. The manager and all source modules match installed bytes. Each of the
four real standalone updaters succeeded with “Update not needed”; all eight
executable version probes passed. Binaries, version/download metadata, removers,
updaters, launcher targets and the official Obsidian CLI remained unchanged.
Local plans, before-images and verification receipts are in
`/home/marek/Documents/Codex/am-yaml-cutover/recipe-locality-deployment/`.
No GUI startup was exercised. The November 6 natural scheduled publication and
subsequent ordinary `am -u` remain unobserved; no workflow was dispatched.
