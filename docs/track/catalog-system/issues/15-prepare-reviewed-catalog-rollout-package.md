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
Status: claimed
Assignee: codex
Blocked by: current-scope migration checks in 14; expanded dual-output qualification deferred

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
