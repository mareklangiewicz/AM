# Implement and check the supervised adapter offline

Type: task
Status: resolved
Triage: ready-for-agent
Blocked by: 13

## Goal

Implement the supervised-worker adapter proposed in
[transport-enrollment-review.md](../design/transport-enrollment-review.md), using
fake sockets and pipes for verification. Refine the design if implementation
reveals a simpler equivalent boundary, preserving its guarantees and recording why.

## Scope

Add the transport module behind the existing collector interface, without a live
CLI, active workflow change, source enrollment or dispatch. The public test/replay
entry point remains offline. No outbound API or loopback HTTP requests, actual
credentials, package installation or installed-app changes.

## Acceptance

- Operational preflight requires numeric-ID fetch URLs and trusted own repository
  ID; names remain aliases. Missing IDs or unapproved revisions prevent worker
  creation. Preserve exact descriptors/new IDs; do not inherit validators across
  URL changes or silently change the six-source manifest.
- Parent enforces connect/request/batch absolute deadlines while child can block;
  kill/reap/cancellation and cleanup are checked with fake worker processes/pipes.
  Simulated trickle traffic never extends the overall deadline. Connected reflects
  completed handshake, not first response header.
- Bound status/header/body/IPC input before allocation and report only actual
  conditional values sent. Demonstrate framing/length/truncation/overflow cases.
  Any version-sensitive HTTP parser integration requires focused compatibility
  checks; do not rely on Python 3.15-only features.
- Credentials travel only through protected runtime IPC, never argv, dumped config,
  inherited broad identity or saved output. Poison ambient proxy/auth/config inputs
  and secret-bearing fake exceptions; fixed diagnostics must remain safe.
- Run existing collector/churn checks and focused offline adapter tests. Record
  real integration limitations and exact next review prerequisites in the tracker.

No live enrollment or six-release run follows automatically. Review the implemented
adapter and exact code/manifest/workflow revision before asking for separate live
validation. The one missing-ID metadata request remains unperformed.


## Answer — 2026-10-27

Implemented tools/catalog-collector/supervised_transport.py behind the existing
collector API. It enforces numeric fetches, approved revision checks, one worker
per planned descriptor, protected bootstrap IPC, actual conditional evidence,
bounded pre-parser input and parent-enforced absolute process deadlines.

[Findings](../research/supervised-adapter-findings.md) and
[checks](../research/supervised-adapter-checks.json) record 44 passing offline tests:
19 adapter, 17 collector and eight churn. Tests use fake sockets and real local
processes/pipes, with no outbound or loopback HTTP and no actual token. Cleanup,
trickle traffic, handshake/header timing, strict chunk framing and parser close
compatibility were exercised. No active workflow or live CLI was added.

Real TLS/GitHub behavior, trusted workflow provenance and missing source enrollment
remain unverified. [15](15-review-adapter-and-stage-manifest.md) reviews the concrete
implementation and stages the real manifest prerequisites before any separately
authorized identity read or six-release baseline. Neither run is authorized here.
