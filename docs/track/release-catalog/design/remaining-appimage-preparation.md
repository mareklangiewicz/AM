# Remaining AppImage batch: offline review package

Prepared November 2, 2026 for [47](../issues/47-enroll-scoped-migration-sources.md).
Status: offline preparation; no additional requests or operations authorized.

## Frozen scope

[Machine payload](../research/remaining-appimage-preparation-20261102.json) binds
source `cc2ba588d5446df5a9fdb5366ad689e672986a2a`, the frozen inventory and current
queue hashes, and all 118 recipe fingerprints. It preserves queue order and all
49 exact named endpoints, with both original selectors per recipe. The accepted
Brave row is excluded. The remaining endpoints require 48 distinct name-to-ID
checks: SuperTuxKart list/latest share identity, but retain separate descriptors.
No unknown ID is inferred. Historical queue status strings are not current
operational truth; the accepted eight-source state is recorded in the handoff
and [Brave acceptance](../research/brave-live-20261102.md).

All 118 recipes passed `bash -n`; all 236 original selectors contain their exact
queued alias. Inventory SHA256 matches the frozen queue. These checks establish
scope and syntax only, not release availability or selector compatibility.

## Proposed substantial evidence stage

Review the entire payload together, rather than requesting approval per endpoint.
A future identity-only authorization can cover at most the 48 exact, deduplicated
GET URLs in `identity_requests`, each once, sequentially, with no retries,
redirects, pagination, credentials or fallback. Preserve the existing supervised
identity contract: direct verified HTTPS, clean environment, pinned API/Accept
headers, identity encoding, 10-second connect / 30-second absolute request limit,
64,000-byte body/header caps and 8,192-byte public header-value limit. Stop the
batch on the first failed or invalid identity, retaining completed evidence.
Require HTTP 200, exact expected full_name ignoring case, positive repository ID,
private=false and visibility=public. Refuse collector-own-repository identity.
Maximum request time is 1,440 seconds plus bounded local bookkeeping; a concrete
supervised batch runner and total deadline must be reviewed before execution.
This document and JSON are a request inventory, not that executable runner.

After reviewing real identity evidence, derive each numeric URL by preserving
its original suffix/query and compute each descriptor ID through the existing
collector implementation. Then prepare one separate review of at most 49 exact
numeric release GETs, each once, with no validators, retries or pagination.
Use unchanged 8,000,000-byte body / 64,000-byte header caps and supervised
30-second per-request limit. At most 1,470 seconds of request time and
392,000,000 body bytes could be retained across that separate evidence stage;
this is an evidence-directory bound, not a permissible catalog tree size.
Bind the executable payload to reviewed identity evidence and fresh output paths.
Stop on failed transport/shape/identity checks; do not substitute latest/list.

Run every original selector against the exact retained response bytes and compare
with actual asset URLs. Report zero/multiple selections and description-only
matches; do not silently repair filters. Preserve per-response hashes, timing,
status and headers. Release GET approval does not approve enrollment or migration.

## Activation boundary and capacity decision

The accepted catalog has eight sources. All remaining endpoints would produce
57 sources: 57 × 30 seconds = 1,710 seconds of nominal request time, exceeding
the unchanged 300-second collector deadline. Even nine sources leave only
30 seconds of nominal overhead. Therefore full-batch activation is not ready,
and increasing only a count guard would not satisfy the contract.

Use actual saved body sizes and selector results to prepare a capacity proposal:
retain all eight accepted descriptors, aliases and observations; preserve 8 MB
body, 2 MB index and 50 MB tree caps; measure complete tree, ZIP and Git growth.
Choose bounded operational subsets or separately review a scheduling/collection
contract change. Evidence gathering can cover all remaining endpoints while
operational adoption proceeds in measured subsets. No new scheduling policy is
accepted by this document.

A subsequent concrete activation review must include candidate source/manifest
hashes, exact source push, one explicitly bounded collection, expected parent,
all-source success and recomputed tree, both pinned readers and unchanged original
selectors, then daily repin only after acceptance. Recheck live state immediately
before operations. No activation patch or source SHA is claimed here because IDs,
response sizes and a feasible collection plan are still missing.

Rollback must be bound to that future preflight's actual prior source pin and
publication parent. Retain the known-good eight-source state while preparing;
never retire existing observations by loading a replacement-only manifest. Failed
validation blocks publication/repin. If a candidate has already published, inspect
its exact tree and pause further expansion before proposing the bounded restore;
do not fabricate a rollback commit or blindly reset the publication branch.

47 and 49 remain partial. No source push, metadata request, collection, repin,
recipe change, host helper delivery or installed-updater operation occurred.

## Identity runner ready for review

[Runner](../../../../tools/catalog-collector/identity_batch.py) SHA256:
`54347a669b4b9bc36fddf1e3b7ea2fd9bd64525aeaab295d2819885abb874cc8`.
It binds payload SHA256
`5538f32fd32d3e3b5f6d545d6f72e9d5af77bc76a021e6b633c518571a2d7066`,
rechecks all recipe fingerprints before execution, and defaults to an offline
plan. It creates the output directory exclusively, so interrupted or completed
batches cannot be rerun in place. Each attempt retains exact body/header bytes
(up to cap plus one overflow-detection byte), hashes, UTC timing, transport exit,
termination and validation; atomic batch summaries preserve progress and refusal.
The runner stops on the first refusal and never automatically resumes/retries.

The 1,500-second monotonic batch budget bounds request execution and is checked
before each request; each child gets at most the smaller of 30 seconds and the
remaining batch budget. Local evidence writes and process cleanup occur afterward;
this is not a separate hard wall-clock watchdog for disk I/O. The inherited
supervisor kills/reaps stalled children and limits both streams while reading.
The own-repository exclusion ID is **1291019762**, recovered offline from
`run.json.repository` in the accepted Brave live-evidence archive (run 41429379232),
not inferred or fetched anew. CLI rejects an override with a different ID.

Reviewable execution command, **only after identity-batch authorization**:

```sh
python3 tools/catalog-collector/identity_batch.py \
  --execute-approved-identity-batch \
  --output docs/track/release-catalog/research/remaining-identities-20261102
```

Exactly the 48 frozen identity URLs, at most once each, are in scope. No release
GET, source push, enrollment, collection/publication, daily repin or host delivery
is included. API quota/status failures stop the batch without retries. If an
attempt fails, review its retained evidence before proposing any remaining scope.

Verification: 15 offline tests pass, covering frozen scope/fingerprints, tamper
refusal, exact evidence, wrong/private/self IDs, redirects, duplicate JSON and
ambiguous framing, both stream caps, oversized header values, nonzero exit,
stalled-child interruption, spawn failure, batch deadline, stop-on-first-failure,
exclusive repeat refusal and a synthetic complete 48-request batch. Default plan
execution and `git diff --check` pass. No network requests were made.
