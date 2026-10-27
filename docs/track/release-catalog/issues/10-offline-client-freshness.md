# Prototype commit-pinned freshness and refusal offline

Type: prototype
Status: resolved
Triage: ready-for-agent
Blocked by: 09

## Question

Can a selective client explain observation age and explicit stale acceptance
without mixing publication generations or serving unavailable sources?

## Scope

Pure offline lookup/state prototype using saved or synthetic publication fixtures.
Reuse the captured storage experiment where useful. No HTTP, remote Git, Actions,
installer/updater integration or installed-app changes. Capture throwaway code on
a separate local branch and findings in this tracker. No day sample required.

## Acceptance

- Resolve a publication fixture once to a full commit. Index and selected body
  always come from that commit; branch movement never changes an ongoing read.
- Verify supported schema, exact descriptor/alias identity, body path, digest and
  byte count before exposing data. Missing pinned bytes refuse without fallback.
- At a fixed injected UTC time, show ages of 0, 86,399, 86,400 and 86,401 seconds.
  Working proposal: <=86,400 is fresh; greater age requires explicit acceptance.
  Refuse missing/unparseable timestamps and future validation times. No hidden
  clock correction or tolerance; record if evidence suggests revising this rule.
- Receipt and validation times remain visible and separate. A valid 304 advances
  validation but never receipt. Production-like lookup refuses fixture-only
  round-completion timing; demonstrate it separately as historical evidence.
- Temporary failure may serve an available observation subject to its unchanged
  validation age. New unknown, unavailable, retired and removed-alias states
  refuse, even when an older body exists or a stale acceptance is present.
- Bind acceptance to publication commit, descriptor identity and body digest.
  Acceptance for A cannot authorize B, another source or a changed body. It never
  rewrites timestamps or authorizes unavailable data. No persistent acceptance
  store or installer UX is required for this experiment.
- Demonstrate explicit alias tombstones independent of descriptor retirement;
  re-enrollment does not reuse validators or current availability automatically.
- Exercise the proposed six-source/body/index/tree caps atomically; previous
  publication remains intact on refusal. Pack-history cap can use an injected
  measured-size fixture; do not generate 128 MB just to cross a boundary.
- Provide a shareable state walkthrough plus a concise verdict and remaining
  choices. No live public-visibility or hosting guarantees may be inferred.

## Inputs

[Storage findings](../research/storage-prototype-findings.md), captured source
commit bff0d5bf2 on proto/offline-storage-v1, and the
[review refinements](../design/storage-publication-v1.md#2026-10-27-offline-review-refinements).


## Answer — 2026-10-27

Completed the bounded offline prototype. The runner recorded 54 outcomes (53
successful checks/expected refusals and one historical timing demonstration).
A shared pure core drives both the single-file walkthrough and local Git replay.
See [findings](../research/freshness-prototype-findings.md) and
[machine report](../research/freshness-prototype-report.json).

Primary source: `694613538`, branch `proto/offline-freshness-v1`,
`tools/proto-freshness/`. Main keeps findings only. Exact age/consent boundaries,
separate timing provenance, alias removal/re-enrollment, pinned reads and caps
behave as specified within the synthetic-fixture limits. Browser visual QA and
production hardening are not claimed. [11](11-review-client-and-collection-boundaries.md)
records remaining policy and operating-design choices. No live experiment ran.
