# Twenty-recipe enrollment, publication and live policy refresh

Ticket [134](../issues/134-enroll-and-publish-twenty-recipe-batch.md), November 6, 2026.
Marek's “Go ahead” authorized the remaining enrollment, source push, manual
publication and scoped live follow-through after ticket 133's twenty conversions.

Source `743dbf1394aa3433c21814145bf09f86dcb1921d` is pushed and its remote tip
was verified. [Manual run 42156336747](https://github.com/mareklangiewicz/AM/actions/runs/42156336747)
succeeded, publishing `daf47edb2b382bc6b7df832b00c43fae12bb73d2` as the exact
child of `a547f48289475ed474de10a6389ce69c12c62060`. The exact-pin app map is
**43 recipes / 41 numeric repositories**; all former 23/21 entries remain.
All 41 source documents have matching numeric/name/schema identities, successful
collection statuses and 100-release page scope. Total YAML is 8,466,205 bytes;
largest document is 1,142,139 bytes, below the unchanged 2 MiB per-file limit.
The new aeroftp source has 100 retained releases and incomplete history; each
other new source reached the end under the maintained collector's page rule.
This is one observation, not future growth/capacity or transactional completeness.

[Portable publication/deployment receipt](large-batch-publication-deployment.json)
contains exact source/run/catalog/parent pins, all 41 source sizes/hashes/counts,
selected-key sets and deployment verification. Earlier
[full-scope API evidence/replay](large-batch-enrollment-replay.json) preserves
49,703,951 response bytes acquired in 51.56 seconds, normalized/validated in
31.93 seconds. Both observed full-scope snapshots have the same YAML byte total.
The 52-source / 16 MiB response / 96 MiB total / 300-second collection and 2 MiB
per-repository budgets remain unchanged. No workflow scheduling or runtime logic
was modified.

## Live result

Only `/opt/am/modules/catalog-yaml-policy.am` was backed up and atomically
replaced, preserving its native mode/UID/GID. Its before-image matched reviewed
source `fa36ebb7e`; the after-image matches `743dbf139`. All installed source
modules and manager now byte-match that target. Native ownership was captured
at preflight; no sandbox ownership plan was reused or mistaken for real drift.

The installed helper successfully selected all 46 asset choices at the exact
published pin. All **26 prior choices are identical** before and after: 24
choices for the 21 installed apps (including four coherent EmmyLua tools), plus
the uninstalled 20x/2fac pilot selections. All **twenty newly enrolled choices**
match the statically inspected asset IDs and URLs from 133. Selection validation
uses the distributed reader and installed helper, not application execution.

All **296 protected paths** retain native hashes/modes/ownership or symlink
targets after deployment and smoke checks, including existing recipes/snapshots,
binaries, commands/desktops and twelve Obsidian-related paths including the
official CLI. Manager help passes. All twenty newly enrolled apps remain absent
from `/opt`; the host still has 21 installed apps. The earlier pilot remains
uninstalled as well. No ordinary app update, installed recipe refresh, GUI launch
or yadm pointer change occurred.

Native plan, before-image, exact-pin command-session cache, before/after selection
receipts, manager help and final verification are preserved locally under
`/home/marek/Documents/Codex/am-yaml-cutover/large-batch-deployment-20261106/`.
All earlier recovery directories are preserved. The operation has an atomic
single-module replacement and rollback-on-verification-failure; it does not
claim binary rollback or installed-app migration.

## Verification scope

The enrollment source passed **28 focused tests**: six publication groups, one
new saved-page full-batch enrollment group, three declaration groups, two compiler
groups and sixteen host manager/lifecycle/cutover groups covering all 43 enrolled
recipes with inert assets. The batch enrollment check verifies an exact former
23/21 parent, maintained collector normalization, distributed reader, sixty
three-awk selections, historical-pin preservation and malformed-source refusal.
Ticket 133 separately records 43 focused conversion tests and static evidence.
No new complete catalog/container suite or real app launch is claimed. The manual
workflow is verified; the natural scheduled trigger remains unobserved.
