# Prepare the reviewed catalog rollout package

## Direct v3 cutover — accepted November 9, 2026

Marek explicitly superseded the temporary dual-output migration plan: he is the
only user, there are no external consumers, and only myxps uses these changes.
Mylenovo and mypi have not pulled them. Complete maintained v3 readers/consumers
and remove active v2 production from the intended operating path. Git history
and manual recovery suffice; preserve historical snapshots/commits without new
rollback machinery or continued v2 publication for recovery. Prioritize the
current enrolled scope before coverage expansion; expanded dual-output
qualification is stopped. Reuse completed evidence and check actual migration
changes only. Prepare a concrete myxps cutover and commit locally; only final
specific push/deployment or installed-host actions need separate authorization.
Earlier dual-publication, consumer waiting/date and extra rollback requirements
are superseded wherever they conflict.

Type: task
Label: implementation:task
Status: resolved
Assignee: codex
Blocked by: 14

## Outcome

One concrete package identifies exactly what can be pushed/activated, the evidence
supporting it, required live checks, stop conditions and tested recovery commands.
Preparing the package does not authorize executing it.

## Accepted inputs

[Cutover/ownership](09-choose-compatibility-transition-and-recovery.md),
[final roadmap](10-agree-system-acceptance-and-implementation-roadmap.md#answer--november-8-2026),
[rehearsal evidence](14-verify-scale-compatibility-and-rollback.md).

## Package and acceptance

- Record exact source/schema/policy/recipe revisions, candidate/catalog/status pins,
  content hashes, dependency/workflow versions, measured operating settings and
  history margins. Link focused test/browser/scale/comprehension receipts and
  explicitly list unmeasured/live-only facts and blockers.
- Inventory maintained format-2 consumers and their delivery plan. List reviewed
  changes to collector/Action/jobs, hourly/manual orchestration, v2/v3/status refs,
  main-owned Pages artifact and disabling prototype auto-deployment. New channel
  creation and activation require exact expected parents/bootstrap preconditions.
- State ordered v2 → v3 → final-status writes and actual partial/ambiguous/conflict
  behavior. Prepare last-good pin/artifact/before-image records and exact rollback/
  correction commands, without ref rewinds, source-observation freshening or
  binary rollback promises. Do not couple valid catalog recovery to failed status.
- Identify separately authorized live acquisition and exact-publication/readback
  checks needed for real capacity/operation claims. Include actual anonymous browser
  fetch/CORS/deployed allowlist checks; local simulation is insufficient. No repeated
  arbitrary run count; each check must resolve a concrete remaining risk.
- Present source push and remote activation/publication/Pages actions together for
  approval, with exact scope and stop/rollback ownership. After approval, record
  real receipts rather than claiming advance success. Fresh enrollment still needs
  explicit identity/capacity scope; no automatic 5,000-source enrollment.
- Keep installed-host recipe/module/config delivery and any yadm pointer operation
  outside this package. Format-2 retirement waits for migrated maintained consumers,
  rehearsed rollback and Marek's agreed date; preserve old refs/history/evidence.

## Completion boundary

Preparation is complete when the package is reviewable, evidence/limitations are
clear and every remote action has an exact authorization point. Runtime acceptance
requires its actual authorized checks. No push, workflow dispatch, public ref/Pages
change, history rewrite, installed-host operation or yadm change before that point.

## Answer — November 9, 2026

The [direct v3 myxps package](../myxps-cutover-15.md) is prepared with exact source,
schema, seed and observed remote pins, a 50-file installed metadata/runtime
manifest, unchanged updater guards, staged Pages allowlist, focused evidence and
ordered final operations. The source cap stays at the existing 500 sources; no
expanded dual-output qualification or new rollback machinery is included.

Preparation is complete. Push, new v3/status publication, one bounded current-scope
live collection, installed metadata delivery, Pages deployment and resuming the
reviewed hourly schedule await final specific authorization. No binaries, other
hosts or yadm pointers are in that action scope. Record actual live results here
after authorization; no production success is claimed in advance.

## Executed — November 9, 2026

Marek authorized execution with “migrate without any unnecessary steps.”
[Actual receipt](../myxps-cutover-result-15.json): pushed main at `f05e85926`,
created the reviewed v3 seed, and completed
[the first native v3 run](https://github.com/mareklangiewicz/AM/actions/runs/42541004615).
It attempted all 500 sources: 498 succeeded, agent-console failed source validation,
and Axe-OS-Multitool had a transport failure with its old source preserved.
V3 `3b779ba31e70f470fd83889069e3e8e0cb0a889d` and status
`cbacd32922c8da8fdcd9706e4a12c966453ef9e7` are confirmed. V2 remains frozen at
`f98e2285e9348541cd00df74eb9ab570aa96b11e`; no v2 write was attempted.

Delivered all 50 named myxps files; 21 installed declarations are v3 and all 21
updaters are unchanged. Hashes passed. All 21 installed recipes / 24 tool
selections passed ordinary wall-clock freshness with the delivered runtime
against the new live catalog, without stale waivers or app payload execution.
Application binaries, versions, launchers/data, other hosts and yadm were untouched.

[Main-owned browser deployment](https://github.com/mareklangiewicz/AM/actions/runs/42541108432)
succeeded. A native anonymous Chromium journey opened Obsidian with nine assets,
no browser errors and successful pinned catalog/map/source/provenance fetches.
Resumed the existing hourly scope by setting the schedule revision to the exact
pushed main tip. Prototype deployment remains disabled. No extra rollback system
or expanded dual-output qualification was introduced. The remaining two source
failures are normal reported deferred work, not a reason to resume v2 production.
