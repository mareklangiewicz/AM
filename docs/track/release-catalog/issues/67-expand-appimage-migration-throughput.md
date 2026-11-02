# Expand AppImage migration beyond the original 124-recipe slice

Type: task
Status: claimed
Triage: ready-for-agent

## Scope

User requires faster, substantial migration throughput. Stop using completion of
the original 124-path queue as the overall migration boundary. Freeze at least
1,000 remaining recipes from the two already understood no-unpack source frames,
preserve exact selectors/aliases and source fingerprints, and prepare compact
candidate replacements in one batch. Keep exceptions out of its critical path.

Static replacements are candidates, not accepted migrations. Verify actual
metadata/assets before operational delivery. Do not blindly raise the 52-source
collector cap or existing time/storage caps to fit the wider queue. Establish a
bounded enrollment/publication design that can process substantial slices while
retaining previously accepted observations, provenance and pinned readers.
New publication and installed rollout remain distinct operations.

## Current result

[Exact frozen payload](../research/appimage-next-large-batch-20261102/payload.json)
and [1,000 candidate replacements](../research/appimage-next-large-batch-20261102/recipes.patch)
cover 732 exact endpoints / 730 distinct identity requests, chosen by most shared
callers first. Wider compatible lexical pool: 2,549 recipes / 2,281 endpoints.
Source hashes and original install/update selector text are frozen; candidate
filters preserve the exact pipeline tail. All 1,000 shell syntax checks and clean
patch application pass. Static recipe reduction: 67,776 lines. No new metadata,
actual-asset validation, operational migration or publication is claimed.

Next work is a bounded collection/publication capacity design for substantial
slices, rather than treating the eight redirect leftovers as the main frontier.
Keep existing guards until measured replacement capacity is specified and tested.

## Capacity audit and evidence queue — 2026-11-02 continuation

Implemented an offline [queue/capacity module](../../../../tools/catalog-collector/throughput.py)
and retained [reproducible report](../research/appimage-next-large-batch-20261102/capacity.json).
It verifies every current recipe hash, binds the exact payload and operational
manifest hashes, conserves all 1,000 paths / 732 aliases, and keeps each of the
730 identity requests within one cohort. Fifteen evidence cohorts (fourteen of
52 endpoints, one of four) preserve shared-caller priority; the first five cover
520 recipes. They are not operational manifests or guaranteed successful runs.
Time, quota and received-byte stops must still apply during actual acquisition.

Confirmed by replay through the existing storage interface: replacing a 52-source
manifest with a six-source subset retires 46 entries and disables their aliases,
although retained bodies and observation ages remain intact. Consecutive small
replacement manifests therefore cannot deliver cumulative migration. This is
existing documented retirement behavior, not a production defect to remove.

The 52 current plus 732 candidate endpoints require 784 source descriptors. A
**synthetic**, ten-digit-ID union serializes to 282,791 manifest bytes versus the
64,000-byte parser cap, independently of the source-count guard. The hypothetical
IDs/evidence pointers are never written as an enrollment manifest. The current
50,000,000-byte tree permits less than 63,775 mean body bytes at that count after
metadata overhead. Actual new body lengths are unknown; this is a budget, not a
prediction that the tree does or does not fit. Worst-case permitted bodies alone
would total 6,272,000,000 bytes. Splitting requests does not solve either limit.

### Proposed sequence, not accepted architecture

1. Use the complete frozen evidence queue to acquire exact public identity and
   numeric release metadata under bounded, resumable work units. Retain failures
   and redirects as exceptions rather than accepting changed identities. Keep
   raw successful evidence available for original-selector checks. Cohort size
   does not authorize a request, bypass quota, or promise a 300-second completion.
2. Measure real aggregate body/index/lookup sizes and request times. Validate all
   original selectors and classify actual compatible paths before changing
   enrollment. Do not choose `latest` or pagination substitutions to save bytes.
3. If measured union storage fits the existing publication budget, evaluate a
   separate full enrollment inventory and exact collection subset at the storage
   seam. Untouched observations retain provenance and age; omitted collection
   targets must not mean retirement. Exact subset approval, same-run artifact
   recomputation, parent conflict refusal and source refresh coverage need tests.
   This would still require an explicitly bounded larger inventory representation;
   the current manifest parser cannot represent the union.
4. If retained exact bodies exceed the tree budget, incremental collection alone
   is insufficient. Evaluate bounded publication shards with one atomic routing
   pin, including both readers and managed standalone helper delivery. That is a
   separate format/delivery change; no implementation or acceptance is implied.

The smallest sufficient choice remains conditional on actual evidence. No source,
manifest, collector guard, workflow, reader or production recipe changed here.
Four focused checks pass: full queue conservation, changed-source refusal,
duplicate refusal, and actual storage retirement replay. No new metadata GET,
push, dispatch, repin, installed migration or full-suite pass is claimed. Ticket
remains claimed; bounded live acquisition and operational delivery are unfinished.
