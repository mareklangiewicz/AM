# Single-user YAML catalog operation

The local source collection list now contains 23 recipe identities in
`tools/catalog-collector/collection-recipes.txt` (21 numeric repository identities),
including 20x and 2fac. The deployed baseline remains 21 recipes / 19 repositories
until the pending source commits are pushed and a publication succeeds.
Collection enrollment is independent of recipe declaration support. Recipe headers
marked `# AM-RECIPE-DECLARATION 1` own customization and selection settings;
adding a declaration does not enroll it for collection. The older 50-source design
manifest and
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

Edit recipe declarations directly. `recipe_policy_source.py` compiles their
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

`DESKTOP_STRIP_NO_SANDBOX` defaults to `false`. An explicit `true` removes
space-delimited literal `--no-sandbox` flags from `Exec=` lines of newly generated
desktop files, preserving other keys, other arguments and field codes. This is a
narrow textual compatibility transformation, not a general desktop argument
parser; quoted/escaped argument forms require separate review. Other values are
refused before acquisition and by declaration compilation. Existing desktop files
remain preserved. 20x opts in to retain its original fork recipe behavior;
2fac and all other recipes keep the default argument-preservation behavior.

20x/2fac have source declarations and local collection enrollment (tickets 130/131).
Neither local change supplies production catalog coverage or changes installed
recipes. Pushing would make the next scheduled/manual publication collect the
two additional sources; push, publication observation and deployment remain
separate. Do not assume source enrollment proves a successful live collection.

Obsidian declares `EXTRA_APP_LAUNCHERS=obsidian-gui` and `DESKTOP_EXEC=installed`.
The shared lifecycle contains no Obsidian identity checks. Official CLI registration
at `~/.local/bin/obsidian` remains independent. Existing installed recipes are not
rewritten by module sync; these declarations arrive through the current source
recipe on install/reinstall. Existing user GUI aliases/desktop overrides need no
migration.

## Recipe archive and selection settings

Each declared recipe owns its repository identity (`CATALOG_REPOSITORY_ID`,
`CATALOG_REPOSITORY`), channel (`CATALOG_CHANNEL`) and asset pattern
(`CATALOG_ASSET_PATTERN`), alongside its launcher, refresh and version settings.
Keep the declaration header literal: one shell assignment per line, with shell
quoting for spaces and patterns. `recipe_declarations.py` reads it without executing shell.
The collector and maintenance cutover resolve the explicit collection list through
these same declarations. Run
`python3 tools/catalog-collector/recipe_policy_source.py` after selection changes,
and commit the regenerated `modules/catalog-yaml-policy.am` with the recipe.
The generator emits registry data only; eligibility, ordering and freshness remain
maintained selector code. The generated registry serves direct catalog clients; it
is not another source to edit. No JSON host manifest or app-named archive adapter registry remains.

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


Later November 5, Marek requested a manual publication. Run
[42097574409](https://github.com/mareklangiewicz/AM/actions/runs/42097574409)
succeeded at source 264e5264d in an 80-second job, publishing catalog
`9461e1770bbf67be8552c2d1f84811c24a7d2bdd`. Collection uses 19 release-list
requests with the workflow token. Ordinary unpinned `am -u` then exited zero:
Neovide nightly and Neovim nightly refreshed with checksum verification; the other
19 apps were unchanged. AM reported source-recipe changes for the 17 installed
recipes outside the coordinated four-recipe refresh; no reinstall was performed
in response. Official Obsidian CLI and desktop override hashes remain unchanged.
Manual publication/update receipts are beside the deployment before-images.
This manual run does not establish that the November 6 schedule fired.


November 5 completion: Marek authorized the remaining 17-recipe refresh. Their
installed declarations and `.am-installer` source snapshots were backed up and
refreshed from e4c84b154; host path bindings were retained and standalone source
defaults pinned to that revision. All 21 installed recipe bodies (excluding host
bindings) and source snapshots match source. Ordinary `am -u` exited zero:
two nightlies refreshed with checksum verification, 19 apps unchanged, and zero
source-recipe change/reinstall notices. All 189 recorded protected paths retained
their hashes/modes or link targets after the refresh and update. Plans, before-images
and logs: `/home/marek/Documents/Codex/am-yaml-cutover/remaining-recipe-refresh/`.
This closes the installed-recipe refresh; the natural November 6 scheduled trigger
remains unobserved. No additional workflow dispatch or GUI check occurred.


Marek subsequently accepted closing the rollout without waiting for the natural
scheduled trigger. Manual publication plus ordinary updates establish the completed
publication/consumer path. The scheduled trigger itself remains unobserved and is
routine monitoring, not a blocker. Historical tracker tickets 47/49 are closed as
superseded broad scope; design ticket 71 is resolved by the delivered implementation.


## Common declarations — source change, ticket 114

The declaration reader accepts `x86_64`, `aarch64`, `i686` and `armv7l` recipe
paths without a host category. Architecture policy excludes other operating
systems; x86_64 retains its prior exclusions, while the other architectures require
an explicit matching architecture name and exclude conflicting ones. App-specific
patterns still apply. Direct catalog clients and the shared installer use the same
trusted recipe-identity registry; selection settings are not accepted from ambient
client environment variables. Configured AMREPO still determines catalog ownership.

The remaining 472 format-2 recipes retain the existing am-utils, AppImage and
Neovim selector policies. These are a transition pending reviewed equivalent
recipe declarations, not a second final declaration format. Remove those branches
only after all their supported identities have reviewed replacements and matching
behavior checks. This slice does not convert unused recipes or widen collection.

Source `14adf6fd11c0c9109a3f62ced92b3be7548964dc` was pushed and deployed on
November 5 after Marek requested deployment. All 21 installed recipes and source
snapshots now use the generic declaration marker; selection fields and behavior
for those identities are unchanged.


## Maintained metadata-only recipe refresh

Use `tools/catalog-collector/recipe_refresh.py` for one explicitly selected
installation. This maintainer command requires Python; installed AM clients and
standalone updaters remain shell-only. Preview reads a recipe from a full local
source commit and prints old/new recipe and `.am-installer` snapshot hashes:

```sh
python3 tools/catalog-collector/recipe_refresh.py \
  --source /path/to/AM --commit FULL_SOURCE_SHA \
  --recipe x86_64/APP --installation /path/to/apps/APP
```

After reviewing that source and preview, append `--apply --backup /new/backup/dir`
and `--expect-recipe OLD_RECIPE_SHA256 --expect-snapshot OLD_SNAPSHOT_SHA256`.
The backup directory must not exist and must be outside the installation. Apply
checks both hashes and the exact managed updater before writing. It preserves
installed app/bin/desktop/module paths, keeps configured AMREPO repository ownership,
and advances only its source ref to the selected commit. Recipes and source
snapshots retain file modes and ownership. Custom updaters, symlink metadata,
identity mismatches and unsupported installed bindings refuse.

Only `recipe.am` and `.am-installer/APP` are replaced. Binaries, version/download
metadata, removers, updaters, desktop files and launcher links remain untouched.
Runtime synchronization is separate: coordinate any required runtime changes
before relying on new declarations. Run under exclusive maintenance; this command
does not lock ordinary AM operations. Each file replaces by rename, but the pair
is not transactional. If interrupted, inspect the backup and restore its two
metadata files or rerun with reviewed current hashes and a fresh backup directory.
It provides no automated rollback or binary migration framework.

The shared Python `installed_recipe.py` owns compact recipe binding and managed
updater rendering for maintenance/cutover tooling. The production shell installer
remains independent of Python; integration tests compare its actual updater bytes
with the maintained renderer. No live refresh accompanied this source addition.


November 5 common-declaration deployment: two runtime modules and all 21
recipe/snapshot pairs were refreshed from `14adf6fd1`, with per-app backups.
Old/new selection matched for 21 apps/24 assets on the same local catalog;
all deployed hashes and 187 protected path hashes/modes/link targets matched after
apply and again during verification. Manager help and installed-helper live
selection for Neovim and the four same-release EmmyLua tools passed at publication
`9461e1770bbf67be8552c2d1f84811c24a7d2bdd`. No binary updates, ordinary `am -u`,
GUI launch, workflow dispatch or publication occurred during this deployment.
Plans, before-images and receipts are in
`/home/marek/Documents/Codex/am-yaml-cutover/common-declarations-deployment/`.


## Historical tooling retirement

Ticket 118 retires the historical collector, staging/migration commands, manual
quota/churn probe workflow and runnable YAML prototype tree from source. Current
publication uses only maintained YAML normalization/retention, validation and
isolated local Git helpers. The one-time format-1 bootstrap option is removed;
publication now requires an existing valid YAML parent. Historical commands and
prototype results remain in Git history at `007ea4871`, while tracked research
evidence and local recovery backups remain in place.

See `tools/catalog-collector/README.md` for maintained entry points and offline
verification. Transitional recipe selectors and their policy compiler remain until
reviewed complete declarations replace them; collection enrollment is unchanged.
The retirement itself performs no publication, installed metadata refresh or module
synchronization. Ticket 119 separately fixes native Termux awk compilation of the
reader's forbidden-character expression; that source change is not deployed.

November 5 retirement deployment: after explicit push/deploy authorization,
`eedd89328` was pushed to origin/main-marek. The sole runtime delta since
`14adf6fd1`, `catalog-yaml-parser.am`, was backed up and deployed on myxps.
All source modules and the manager match installed bytes; 230 protected paths
(including installed recipes/snapshots and earlier protected application paths)
retained their hashes, modes and link targets. The installed reader Unicode /
forbidden-codepoint regression and manager help passed. Read-only live selection
passed for Neovim and all four distinct same-release EmmyLua tools at publication
`9461e1770bbf67be8552c2d1f84811c24a7d2bdd`. The first sandboxed smoke attempt
failed DNS; a fresh network-enabled session passed. No binary update or recipe
refresh was needed. Evidence and parser before-image:
`/home/marek/Documents/Codex/am-yaml-cutover/retirement-deployment/`.
