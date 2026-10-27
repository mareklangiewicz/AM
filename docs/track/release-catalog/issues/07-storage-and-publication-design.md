# Design observation storage and publication

Type: task
Status: resolved
Triage: ready-for-agent
Blocked by: 06

## Scope

Marek accepted moving ahead provisionally with exact REST snapshots and making the day sample optional, then authorized storage/publication design. Describe the stored representation, request identity/provenance, freshness/error state, publication consistency and retention limits. Preserve client release/asset selection. No live collection, publication, installer integration or schedule in this ticket.

## Acceptance

Produce a concrete reviewable format and processing rules, name unresolved operational choices, and identify the smallest offline prototype. Use measured churn as short-window evidence, not fleet capacity proof.

## Answer

2026-10-27: [v1 proposal](../design/storage-publication-v1.md) specifies stable request-ID body paths, exact bytes with index digests, explicit aliases/source descriptors, separate validation/attempt times, temporary-failure/absence/redirect transitions, and atomic publication with commit-pinned selective reads. Includes an illustrative one-entry index drawn from hour evidence. Retention/fleet budgets and hosting remain open. No production schema, collector or publisher was implemented or enabled. [08](08-offline-storage-prototype.md) defines the next offline verification.
