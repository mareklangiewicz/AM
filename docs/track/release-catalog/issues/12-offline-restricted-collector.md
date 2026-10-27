# Implement the bounded collector contract offline

Type: task
Status: resolved
Triage: ready-for-agent
Blocked by: 11

## Goal

Implement the pure planner and bounded collection loop specified in
[restricted-collector-v1.md](../design/restricted-collector-v1.md), with injected
transport and clock. Follow its offline implementation acceptance section.

## Scope

Add a narrowly scoped module and fixture-replay entry point beside tools/catalog-probe.
Leave the historical churn collector, existing workflow, installers and updaters
unchanged. No real network transport or live CLI is added in this ticket. No HTTP,
workflow dispatch, remote publication, schedule or live identity enrollment.

## Acceptance

- Reviewed exact descriptors and immutable repository identities determine a plan;
  own-repository aliases, missing IDs and conflicts refuse before any fake call.
- Credential remains opaque, has no fallback source and cannot enter emitted
  metadata, diagnostics or exception reports.
- Injected transport/clock exercise six serial attempts, connect/request/batch
  deadlines, truncation/size/header bounds, quota and consecutive-error stopping.
- Preserve exact bytes and separate measured start/completion/attempt-finish times;
  genuine conditional validation requires matching prior state.
- Explicitly record not-attempted sources and incomplete outcomes; no implicit
  redirects, retries, metadata reads, pagination or network retry on publication.
- Run focused offline contract checks including slow-stream overall deadline and
  zero-call preflight refusals. Retain findings and remaining integration limits
  in this tracker. Do not infer public visibility or production capacity from fakes.

## Next boundary

After resolution, review real manifest identity evidence and the proposed workflow
adapter before requesting a separately authorized bounded live experiment. No day
sample is required. Remote delivery stays deferred.


## Answer — 2026-10-27

Implemented the planner and injected collection loop in tools/catalog-collector,
with a synthetic replay entry point and 17 passing focused offline tests. The
existing eight churn tests also pass. [Findings](../research/collector-offline-findings.md)
and [replay](../research/collector-offline-replay.json) record byte/timing semantics,
identity/credential checks, conditional evidence, deadlines, bounds and stopping.

No real transport, live CLI, workflow wiring or source enrollment was added.
Arbitrary blocking transport cannot be preempted by event checks: a future adapter
must enforce absolute IO deadlines itself. Current identity/token provenance and
real reviewed repository IDs also require concrete adapter/manifest review.
[13](13-prepare-adapter-and-enrollment-review.md) is the next preparation frontier.
