# Restricted-token collector — bounded implementation design

2026-10-27. Marek accepted ticket 11's two recommendations: retain the demonstrated
freshness contract, and design the restricted-token collector before remote
delivery. This document specifies the next implementation boundary. It does not
authorize collection, workflow dispatch, a schedule or catalog publication.

## Accepted client contract

Validation age <=86,400 seconds is fresh. Older available observations require
explicit acceptance bound to full publication commit, descriptor ID and exact body
SHA-256. Unknown/unavailable/retired sources, removed aliases, missing files,
unmeasured timing, future observation/publication times and failed integrity checks
refuse regardless of stale acceptance. No clock-skew tolerance or negative-age
clamping is introduced. A new publication requires new stale acceptance, including
when bytes match. Receipt and validation times and their provenance remain separate.
This is the accepted initial contract; persistence and installer presentation remain
outside scope. Experimental schema 2 is not thereby adopted as production format.

## Interfaces

Implement a new module beside the existing probe, leaving the historical churn
collector and its workflow unchanged:

`plan(manifest, workflow_identity, previous_state) -> ordered_request_plan`

`collect(plan, transport, clock, credential) -> attempt_batch + run_report`

`transport.execute(request, credential, limits) -> inert_response`

Planning and state checks are pure. The clock and transport are injected for
offline verification. A credential is an opaque runtime value used only by the
transport, never a field in request plans, attempts, exceptions or reports. A plan
contains request descriptor/ID, reviewed repository ID, identity evidence pointer,
aliases, timeout/body limits and optional matching conditional validator values.
It cannot select a release/asset, enroll an unknown source, change descriptors,
resolve a redirect or publish Git objects.

The collect entry point accepts only a plan validated against the current workflow
identity; it checks again before transport. The six-request counter includes every
attempt begun, including timeouts/errors; retries and redirects consume no hidden
requests because neither is implemented. A failed preflight starts zero attempts.

## Reviewed identity and credential boundary

Manifest entries require a positive immutable GitHub repository ID, exact reviewed
HTTPS release descriptor and an auditable identity-evidence reference. All aliases
must resolve through that entry. The workflow repository's ID comes from the
trusted workflow event/context, not an artifact or request URL. Reject a source
with that same ID even when its spelling, owner/name or numeric URL differs.
Missing IDs, conflicting alias identities and numeric-URL/recorded-ID disagreement
fail the entire plan before transport. Owner/name URLs require reviewed identity
mapping; a redirect never updates that mapping automatically. No authenticated
request is made to discover a missing ID during this six-request run.

The existing six-source sample has not acquired a complete reviewed immutable-ID
manifest under this design. Keep incomplete real entries unrunnable; use explicitly
synthetic IDs offline. Obtaining missing public identity evidence is a separate,
bounded, explicitly authorized future operation, with its own request budget.
Do not quietly expand the release job to fetch repository metadata.

An eventual workflow adapter supplies only its built-in GITHUB_TOKEN to collection
with contents:read. Do not accept generic GH_TOKEN/PAT fallback or inspect gh login,
SSH helpers, local credential stores, netrc or curl configuration. Workflow checking
must establish token provenance; token text or an environment variable name cannot
prove it. Before any live wiring, review the exact workflow and credential path.
A transport executable receives the credential through a protected channel, never
command-line arguments or saved request headers; diagnostics redact by design.
Disable implicit proxy/auth/config discovery or explicitly review any needed proxy.
No redirect, arbitrary host or cross-host authorization forwarding is supported.

GitHub documents workflow-token repository isolation and public-release visibility;
using it for unrelated repositories is an inferred public-only permission boundary.
It is not a completed live credential or visibility test. If that boundary cannot
be established in the actual adapter, fail closed rather than fall back to a broader
credential. Draft detection remains an additional content check, not proof of scope.

## Attempt and timing shape

Each inert result contains request ID, exact descriptor, reviewed repository ID,
request_started_at, optional response_completed_at, HTTP status (or null), selected
public headers, bounded response bytes, actual conditional values sent, and a
bounded transport outcome. Use UTC wall-clock times for provenance and monotonic
elapsed time for deadlines. Reject missing/future/out-of-order completion claims;
never substitute server Date, run start or publication time for receipt.

A complete valid 200 supplies exact bytes and measured receipt/validation completion.
A genuine conditional 304 supplies no new body and advances validation only after
storage confirms matching descriptor, validator and prior bytes. Separate receipt
and validation timing bases remain intact. A timeout, truncation or oversized body
is not a complete response; it never advances observation freshness. Record an
attempt finish time separately for diagnostic outcomes with no completed response.

The storage apply operation owns body hashes, public shape validation, availability
transitions and candidate-tree validation. The collector never writes a successful
body path itself or upgrades an HTTP result into usable client data. This keeps
transport results inert and leaves app selection outside both modules.

## Bounds and stopping rules

- Exactly the reviewed sample, at most six descriptors and six serial release GET
  attempts. No automatic pagination, retries, metadata reads, quota reads or fallback.
- Proposed connect deadline 10 seconds, whole request including body 30 seconds;
  batch deadline five minutes. Implement deadline enforcement, not merely a socket
  inactivity timeout that a slow stream can keep resetting.
- Maximum body 8,000,000 bytes. Bound headers to 64,000 bytes total and each retained
  value to 8,192 bytes. A bounded read may consume one overflow sentinel byte to
  detect rejection, but never store it as an accepted observation.
- Index <=2,000,000 bytes, complete candidate tree <=50,000,000 bytes and six-source
  cap are checked by storage before candidate acceptance. Existing proposed local
  history cap is a publication concern, not collection transport behavior.
- Stop on a quota exhaustion response, Retry-After, remaining<=100, a non-rate-limit
  401/403, or a descriptor/identity/provenance violation. Rate-limit 403 needs explicit
  response evidence; do not treat every 403 as transient.
- Stop after two consecutive transport/5xx failures. A complete HTTP response outside
  that class resets this streak. Other individual refusals, including 404/410/3xx
  or invalid JSON, remain reported and may leave the remaining bounded plan to run.
- Missing/malformed quota headers stop further attempts conservatively, rather than
  implying unlimited capacity. An otherwise usable completed response can still
  be supplied to storage; stopping later attempts does not invalidate its bytes.
- Reports distinguish attempted, completed and not-attempted sources, stop reason,
  total bytes and deadline consumption. Retain partial evidence explicitly; never
  label an incomplete run as a complete baseline or retry it on publication failure.

The existing quota probe reported 5,000/hour in one run; documented normal
GITHUB_TOKEN planning is 1,000/hour. Respect actual response evidence without
promising either as an operating capacity. These initial limits do not establish
a fleet scheduler, daily coverage or production cost.

## Offline implementation acceptance

Implement the pure planner, injected collection loop and inert result validation
first. The only shipped runnable entry point in this step is fixture replay; no
real network transport, workflow changes or live CLI is added. Use a fake transport
that counts calls and a fake wall/monotonic clock that exposes deadline behavior.

Verify own-repository exclusion across name/numeric aliases; missing/conflicting
identities; no credential material in output/errors; at most six attempts; no
implicit follow-up on redirect/304/missing metadata; exact byte/validator forwarding;
304 with no prior state refusal; measured timing versus partial/timeout/truncation;
slow-stream overall deadline; response/byte bounds; header redaction and limits;
quota stop, missing-header stop and consecutive-error stop; not-attempted entries;
no token source fallback. Check zero fake calls on preflight refusal and no mutation
of previous state on malformed batches. Use focused contract checks where needed;
this is implementation work rather than another throwaway state-demo requirement.

After offline checks pass, review the real identity manifest and a proposed workflow
adapter separately. Remote delivery remains deferred. No live run is implied by
resolving the offline implementation ticket.

Primary factual references and the credential-boundary inference are recorded in
[the review proposal](client-collection-review.md). Existing workflow/probe files
are evidence, not automatically production-ready adapters for this contract.
