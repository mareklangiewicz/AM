# Review candidate changes and refresh live shared modules

Type: task
Status: resolved
Triage: ready-for-agent

Marek's November 6 “go ahead” accepts the proposed scoped review of the five
pushed commits, followed by live shared-module refresh after checks pass.
Review fixed range a2119bd9f313fb0368fe896f05c26029423a673d through
fa36ebb7edfe3eb47702a8537802f6b95a4b833b on separate Standards and Spec axes.
Address actionable findings before deployment. Keep 20x and 2fac uninstalled.

Refresh only changed shared modules from the reviewed source; back up old bytes,
check installed drift and preserve existing recipes/snapshots, binaries, metadata,
commands/desktops and official Obsidian CLI. Verify deployed hashes and read-only
catalog selections, including both new source identities. No ordinary app update,
recipe refresh, real app launch, further workflow/publication, push or yadm change
is part of this step. Preserve earlier recovery directories.

## Answer

[Independent two-axis review](../research/two-candidate-source-review.md) of the
fixed five-commit range reports zero Standards and zero Spec findings. The Spec
reviewer independently reran the seven inert runtime and three declaration/
selection tests; all ten pass. No corrective source changes were required.

Marek's requested catalog run had already succeeded before this refresh:
[42150558139](https://github.com/mareklangiewicz/AM/actions/runs/42150558139),
publication `a547f48289475ed474de10a6389ce69c12c62060`. Read-only installed-helper
checks at that exact pin established 24 asset selections for the 21 installed
apps before deployment, including four distinct same-release EmmyLua tools.

Only `/opt/am/modules/appimage.am` and `catalog-yaml-policy.am` differed from
reviewed source. Both installed before-images matched the exact review base
`a2119bd9f`; the manager and other source modules already matched. Backed up both
and atomically replaced each from target `fa36ebb7edfe3eb47702a8537802f6b95a4b833b`,
preserving mode and native UID/GID. All source modules and manager now byte-match
that target. This deploys 127's architecture filter and 130's explicit desktop
flag option/compiled source declarations, without changing installed recipes.

The first preflight stopped before writes because sandbox namespace ownership
IDs differed from native IDs. A native read-only comparison verified all contents,
modes and link targets unchanged; all 85 differences were strictly sandbox
65534-to-native-root UID/GID mappings. Retained the original sandbox plan and
recorded a verified native plan before retrying. The apply and post-smoke checks
then verified all 235 protected paths, including existing installed recipes,
source snapshots, binaries, metadata, command/desktop links and 12 Obsidian paths
(including the official CLI), retained content/modes/ownership/link targets.

Post-deployment checks: manager help exits zero; all 24 existing asset selections
are identical to pre-deployment results at the same catalog pin; 20x and 2fac
resolve to verified IDs/assets 688278008 and 594778867. Both candidate apps and
their installation/launcher paths remain absent. No real payload executes in
these checks. Source tests are scoped, not a new full catalog/container run or
GUI/ordinary-update test.

Local plan, before-images, original sandbox plan, ownership-view evidence,
before/after selection receipts, manager help and final verification are under
`/home/marek/Documents/Codex/am-yaml-cutover/candidate-pair-deployment-20261106/`.
Earlier recovery directories remain untouched. No ordinary app update, installed
recipe refresh, app launch, additional publication/dispatch, push or yadm change
occurred in this task. Review/deployment documentation is committed locally.
