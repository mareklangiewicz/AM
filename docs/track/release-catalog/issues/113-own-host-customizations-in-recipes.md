# Make host recipes the source of truth for app customization

Type: task
Status: resolved
Triage: ready-for-agent

Marek requests full locality after 112: this is a single-user fork with only 21
host apps, so do not carry a compatibility registry to preserve older recipes.
Each host recipe should own its selection, archive, toolset, launcher and freshness
settings. Shared machinery may compile/read those declarations, but no separately
maintained host manifest or named archive adapter registry should own them.
Remove obsolete layout/legacy-launcher compatibility. Preserve actual current
host layouts, custom launchers, EmmyLua same-release/fresh-only constraints, and
selection/acquisition separation. Test inert manager installs/standalone updates
and compiler behavior. Source work only; no live deployment or push authorized.

## Answer

All 21 marked host recipes are authoritative for app-specific selection,
repository identity, archive roots, required executable paths, tool membership,
launchers, freshness, refresh and version behavior. The collector and maintenance
cutover read literal recipe headers without shell execution. The policy compiler
reads those same headers and updates only the generated selection registry; it
never rewrites recipes. The separately maintained JSON host manifest and generated
archive adapter module are deleted.

Shared staging consumes recipe declarations for raw/tar/zip/toolset shapes.
EmmyLua's one tool list drives staging, launchers and generated selection.
Fresh-only refusal remains before HTTP; same-release checks remain shared.
Legacy launcher-target inference and old app-named layout aliases are removed.
Unrecognized old layouts fail before acquisition with a recipe-refresh message.

Validation: 16 host groups pass, including all 21 actual-manager inert
installs/standalone updates, custom wrapper preservation, same-release and
per-tool freshness refusal, archive failures and obsolete-layout refusal.
Eleven manager integration tests and two compiler/parser tests pass. Compiler
repeatability and recipe-edit propagation are checked; malformed/nonliteral
headers refuse. Shared shell syntax and diff whitespace checks pass.
Independent Standards and Spec reviews report zero actionable findings.

No push or live deployment. When deploying, refresh the four installed recipes
that previously used named layouts (btop, Kitty, rclone and EmmyLua) together with
the shared module; ordinary module sync alone intentionally does not upgrade
those recipe declarations. This supersedes 112's compatibility commitment by
Marek's explicit request, without adding a migration framework.


## Deployment follow-up — November 5, 2026

Marek explicitly authorized the four-commit push, then the coordinated live
refresh. Source e4c84b154 was pushed to main-marek. Three changed modules,
four installed recipes and their four source snapshots were deployed together.
All installed source modules and manager byte-match that revision. Four real
standalone updates report no update needed; eight binary version probes pass.
Post-update hashes confirm existing binaries, updater/version/remover metadata,
launcher targets and Obsidian CLI/desktop override were preserved. Plans,
before-images and receipts: `/home/marek/Documents/Codex/am-yaml-cutover/recipe-locality-deployment/`.
No GUI check or natural-cycle observation is claimed; November 6 publication and
ordinary `am -u` remain pending. No workflow dispatch or yadm operation occurred.


Manual publication follow-up: Marek requested running publication now after a
quota check. [Run 42097574409](https://github.com/mareklangiewicz/AM/actions/runs/42097574409)
succeeded, publishing 9461e1770bbf67be8552c2d1f84811c24a7d2bdd. Ordinary `am -u`
exited zero for all 21 apps (two verified nightly refreshes, 19 unchanged).
Seventeen source-recipe notices remain for apps outside today's required refresh;
these were recorded, not treated as failed updates or automatic reinstall consent.
The natural schedule remains unobserved. Local logs and receipt:
`recipe-locality-deployment/manual-publication*` under the existing evidence root.


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
