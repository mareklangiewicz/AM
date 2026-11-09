# Verify scale, compatibility and rollback

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
Blocked by: 11, 12, 13

## Outcome

A compact reproducible evidence package shows which accepted capacity,
compatibility, browser and recovery targets are met and which need correction.
Do not turn synthetic processing success into verified enrollment/live capacity.

## Accepted inputs

[Storage rehearsal](05-choose-scalable-snapshot-and-history-storage.md#answer--november-8-2026),
[cutover](09-choose-compatibility-transition-and-recovery.md),
[system targets](10-agree-system-acceptance-and-implementation-roadmap.md#answer--november-8-2026),
[browser acceptance](../../catalog-pages/issues/04-agree-delivery-and-acceptance.md).

## Work and acceptance

- Reuse ticket 12's isolated saved 500-source seed-plus-three receipt, or run it
  once if not yet available. Never mutate the preserved evidence repository.
  Label original observations versus deterministic simulated changes.
- Exercise 5,000 app identities/up to 5,000 distinct sources as a reference workload,
  with representative retained release/asset variation and largest supported
  documents, separate app/source counts, incremental and full-validation fallback,
  catalog/status retention and temporary dual-format resource cost. Synthetic
  scale validates its stated local workload only. No automatic enrollment increase.
- Measure wall time, peak RSS/scope, transfer charges versus received bytes,
  current tree/document/file counts, changed/reused blobs, local/fetched objects
  and consistently packed reachable history. Set ordinary safeguards with at least
  25% unused allowance at measured peak, honoring real host/service constraints;
  do not solve normal overflow by dropping supported data or hiding failed scope.
- Test quota-aware hourly oldest-first scope progression against the ordinary
  allowance/reserve and actual requests/source; establish the 12-hour healthy-source
  objective with explicit evidence limits. Offline scheduling/transport simulation
  does not establish live quotas, schedule reliability or acquisition throughput.
  Define any required live check in the rollout package for separate authorization.
- Project 12 months of catalog/status history at hourly cadence using stated real
  and synthetic churn inputs, including shared-observation timestamps and dual
  output. Report scenarios and review points before normal work consumes headroom;
  do not call an annual projection a measured year or remote storage measurement.
- Check v2/v3 common-fact round trips, actual maintained selection fixtures and
  intentional retention/tag differences, old numeric pins/readers, renamed labels,
  unknown/new schemas and recipe/source-policy divergence. Inventory maintained
  consumers. Marek confirmed November 9 that there are no unknown external
  readers/consumers; do not add an external-consumer discovery or waiting gate.
- Rehearse disposable exact-parent conflicts, ambiguous writes, rerun after loss,
  partial dual-format publication, failed final status, explicit old-pin reader
  recovery, retained site-artifact restore and corrective direct-child publication.
  Preserve observations/history; no forced rewind, installed binary rollback claim
  or new recovery service. Consume ticket 13's real-browser/educational results.

## Decision and boundary

Fix scoped failures, then rerun affected checks only. If actual host/quota/history
limits defeat accepted normal coverage/refresh/headroom, bring the concrete tradeoff
for review; do not mark capacity accepted or silently change guarantees. Record
known gaps for ticket 15. No live collection, remote mutation, enrollment, workflow
execution, deployment, history rewrite or installed-host change is authorized here.

## Preparatory findings — November 8, 2026

While 13 remains claimed, an independent [root/scheduling/consumer preflight](../preflight-14.md)
exposes a blocking ordinary-workload provenance-root overflow, records the concrete
layout proposal pending Marek's decision, inventories current v2 source consumers,
and checks synthetic oldest-first scheduling plus corrective old-pin recovery.
This ticket remains open and unclaimed; no full scale/history acceptance is implied.

The [schema-transition follow-up](../preflight-14.md#collectorschema-revision-transition--november-8-2026)
reproduces the handoff's suspected retained-source schema mismatch, aligns collector
and trusted publisher defaults with the exact parent's schema pin, and adds
cross-validator/publication refusal checks. This is preparatory compatibility
evidence; ticket 13's remaining gates and this ticket's workload/history/selection
requirements remain open.

## Qualification started — November 8, 2026

Claimed after Marek accepted ticket 13's explicit device/comprehension deferrals
and retained timing misses. Continue from the preserved preflight/rehearsal;
exercise a complete synthetic 5,000-source tree, then measure affected resource,
history, maintained-selection and recovery checks. No live capacity claim or
remote operation follows from this claim.

## Qualification checkpoint — November 9, 2026

The [qualification package](../qualification-14.md) records completed 5,000-source,
incremental, dual-output, status-retention, maintained-selection and exact retained
site-restore checks. Marek accepted the synthetic 2 MiB timing exception; ordinary
timing targets and recorded misses remain. Annual dual-output capacity and the
conflicting published source remain explicit unresolved gates. Status stays claimed;
no activation or remote mutation is implied.

## Capacity recommendation ready for review — November 9, 2026

The [concrete operating-profile recommendation](../qualification-14.md#capacity-recommendation-for-review--november-9-2026)
adds only a hash-bound v2 Git-storage probe to the completed evidence. Its one-step
hourly dual-output extrapolation is 92.012 GB/year including synthetic seeds and
optimistic status, before new-release payloads or existing remote history. This
is a scenario, not a stationary rate or measured year. Sensitivities explicitly
price temporary compatibility, variable status and new releases. The prepared
30-minute acquisition timeout and complete hourly headroom remain unqualified.

Recommendation: hold current coverage while correcting history/throughput;
preserve the 5,000-source / 12-hour destination. A proposed 4 GB aggregate history
envelope (3 GB maximum planned usage) is unaccepted and presently unqualified.
Consumer-gated v2 retirement is an alternative, not implied authorization.
The recommendation names narrow affected checks and review triggers without
repeating completed suites. Source 1245849062 remains an independent coverage gate.
Status stays claimed pending material operating decisions and qualification;
ticket 15 remains unclaimed. No deployment, push or settings change occurred.
