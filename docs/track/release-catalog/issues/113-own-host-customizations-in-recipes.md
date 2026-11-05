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
