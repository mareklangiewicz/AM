# Deploy common declarations and maintained recipe refresh

Type: task
Status: resolved
Triage: ready-for-agent

Marek requested pushing 115, continuing, and deployment. Prepare a concrete local
plan for source 14adf6fd1: changed runtime modules plus all 21 installed recipe/
source snapshots, using the maintained refresh operation. Preserve installed paths,
configured AMREPO ownership, binaries, version/download metadata, updaters, removers,
launchers and official Obsidian CLI. Back up all changed metadata and runtime.
Compare old/new selectors on the same local catalog before applying; verify installed
bytes and protected paths afterwards. No app enrollment, workflow dispatch or yadm
changes. Do not turn the unobserved natural schedule into a prerequisite.

## Answer

Pushed main-marek through `14adf6fd11c0c9109a3f62ced92b3be7548964dc` and deployed
that source on myxps. Only `catalog-yaml.am`, `catalog-yaml-policy.am` and all 21
installed recipe/source-snapshot pairs changed (44 files). The maintained refresh
operation preserved installed bindings and configured repository ownership while
pinning standalone recipe defaults to that source. No binary reinstall was needed.

Preflight compared old/new policies on local catalog
`312e8d8bc9a7d800fce5a2907db66ca9806b3fad`: identical selection for 21 apps/24 assets.
The concrete deployment plan records all old/new hashes and 187 protected paths.
Each runtime module and recipe/snapshot pair was backed up. Apply and a subsequent
verification both confirmed all expected deployed hashes and unchanged protected
hashes/modes/link targets, including binaries, updater/version/download/removal
metadata, manager/other modules, launchers and the official Obsidian CLI.

Manager `am -h` exited zero. Read-only live catalog smoke checks selected Neovim
and all four distinct, fresh, same-release EmmyLua assets through the installed
helper at publication `9461e1770bbf67be8552c2d1f84811c24a7d2bdd`. No stale consent,
application binary download, updater execution, GUI launch, workflow dispatch,
publication, enrollment change or yadm pointer change occurred. Ordinary `am -u`
was not run during this metadata-only deployment; the previous successful ordinary
update remains earlier evidence, not a claim about this deployment.

Local plan, scripts, before-images, receipts and logs:
`/home/marek/Documents/Codex/am-yaml-cutover/common-declarations-deployment/`.
Recipe backups are `before-APP/`; runtime backups are `runtime-before/`.
`plan.json`, `applied.json`, `verification.json`, `smoke.json` and `manager-help.log`
record this deployment. Natural daily-trigger observation remains optional.
