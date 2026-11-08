# Scale and compatibility preflight

November 8, 2026. Preparatory measurements while ticket 13 remains claimed;
ticket 14 is not claimed or resolved. These expose a concrete contract issue
before the full scale/history rehearsal. No acquisition, source enrollment,
collector activation, installed-host change or yadm operation occurred.

## Root representation fails the reference workload

Reproduce without network or modifying saved evidence:

```
python3 -B tools/catalog-collector/qualify_scale_roots.py \
  --saved-data /tmp/am-browser-review-data-20261108 \
  --output /tmp/am-scale-roots.json
```

[Exact receipt](scale-roots-preflight-14.json) checks 5,000 synthetic app identities
and distinct source references using the saved unknown-binding shape and a
separate fixture with shared/template/custom/unknown architecture evidence.
No synthetic identity is enrolled or represented as a real upstream source.
The apps root is 245,159 bytes and passes. The provenance root is 2,300,165 bytes
for unknown bindings, or 13,415,165 bytes for the three-evidenced-architecture
scenario. Both exercise the maintained `document bound` refusal at 2,097,152 bytes.
This is a root representation check, not complete-tree or live capacity evidence.

Simply deploying the present pipeline at the reference workload would therefore
predictably fail an ordinary root document. No cap, whitelist or contract was
changed to conceal this finding. Full scale/history qualification remains open.

### Proposed correction, pending Marek's answer

Split provenance by source at `provenance/<source-label>.yaml`, loaded only when
opening that source. Reuse the current provenance document kind and architecture
bindings; include every AM identity pointing to that exact source document,
including distinct stable/nightly entries. Derive the provenance path from the
already validated `repositories/<source-label>.yaml` app reference, without a
second app/source index. Keep the exact C pin, schema/recipe/rule/input checks,
immutable recipe links and conservative unknown behavior.

This changes the unreleased v3 path/layout contract. Update writer/validator,
shared shell/browser path checks, publisher/artifact allowlists, saved-review
converter/stager and fixtures together, then measure the representative workload.
Require each binding's app to point at that source and its numeric repository
identity to match; a missing or invalid required provenance file must refuse a
candidate rather than be silently omitted. Preserve original observations.

The alternative is a measured larger root limit plus off-main-thread/chunked
processing and its resource cost. A higher byte limit alone would still make an
app opening retrieve/parse evidence for the whole catalog. The per-source proposal
is recommended; it has not been accepted or implemented. A question was sent to
Marek during this work. Do not treat absence of a reply as authorization to change
the accepted layout.

## Scheduling preflight

```
python3 -B tools/catalog-collector/qualify_scheduling.py \
  --output /tmp/am-scheduling.json
```

[Receipt](scheduling-preflight-14.json) drives the actual oldest-attempt scheduler
with 5,000 synthetic sources, twelve simulated hourly runs, 500 selected sources
per run and mocked successful empty upstream responses. All sources receive their
first simulated successful refresh within ten batches; subsequent batches return
to the oldest sources. This checks ordering/scope progression, not real quota,
response density, transfer time, scheduler reliability or acquisition capacity.
The 750-request configured allowance and ordinary 1,000/hour planning premise are
inputs, not observed headers. Failures/dropped schedules remain exceptions; the
historical saved transfer and full-parent validation costs still need to be
included in the complete workload qualification.

## Consumer inventory

```
python3 -B tools/catalog-collector/qualify_consumers.py \
  --output /tmp/am-consumers.json
```

[Source inventory and hashes](consumer-inventory-14.json) identify 529 recipe files
with a literal format-2 declaration: 57 newer declaration recipes and 472
transitional recipes, across x86_64 (309), aarch64 (214), i686 (4), armv7l (2).
The current enrollment is separately 509 app identities / 500 sources. These
counts are different denominators; neither proves what is installed on a host.
The receipt also hashes the maintained reader/parser/policy/acquisition modules
and shared installer callers. The original receipt did not inventory external
readers; Marek confirmed on November 9 that there are no unknown external
readers/consumers. That earlier measurement limitation is not a retirement gate.
Migration/selection review of maintained consumers is still required before v2
retirement.

## Additional recovery check

```
cd tools/catalog-collector
python3 -B -m unittest \
  test_pipeline_publication.Pipeline.test_corrective_direct_child_preserves_old_pin_and_observations -v
```

Passes in 1.906 s using disposable local Git remotes. Starts from the actual
publisher, publishes a validated metadata correction as a direct child, preserves
the old pin and effective observations, and successfully queries the old source
through the maintained shell reader. Earlier conflict/ambiguous-write/status
failure and saved seed-plus-three evidence is reused; it was not rerun.

## Still required

After the provenance-layout decision: actual representative source/tree and
full-validation/incremental/dual-output resource measurements, status retention,
12-month history projection, actual maintained selection differences, retained
site restore and the exact rollout package. Live quota/collection/publication
checks still need their reviewed authorization. This preflight does not resolve
13, 14 or 15 and does not justify enabling the collector.

## Accepted correction and partition check — November 8, 2026

Marek answered “ok” to the per-source provenance proposal. That accepts the layout
change above and supersedes its pending wording. Implementation uses
`provenance/<source-label>.yaml`, exact app-group membership and unchanged evidence
fields, byte limits, observation semantics and v2 paths. The browser reads one
source partition at the chosen C; full validators refuse missing/extra/misplaced
partitions and incorrect source/recipe identities. Collection, incremental parent
validation, trusted publication, saved-review conversion/staging, fixtures and
editor associations use the same layout. The former private global path refuses;
old private candidates need rebuilding rather than permissive fallback.

[Partition-size receipt](scale-partitioned-provenance-14.json) repeats the same
5,000-app shape comparison. Unknown partitions are 625 bytes each; the evidenced
scenario is 2,848 bytes each. Total provenance grows slightly with per-document
headers (3,125,000 / 14,240,000 bytes), but an app opening reads only its source.
The apps root remains 245,159 bytes. Complete membership/identity and every byte
size are checked for the generated partitions, and the largest representative of
each identical evidence shape passes the maintained shell/domain decoder. This
is not a full 5,000-source Git/publication/live-capacity qualification.

Verification: 14 Node transport/contract checks, 12 Python contract checks
(including shared shell/browser fixtures and cross-source negative cases), 10
publication/recovery checks, and 18 browser checks across desktop/narrow Chromium
and Firefox pass. Browser fixtures now contain explicit unknown bindings for
all aliases; the nightly journey continues to show unknown without fabricated
recipe links. The source-local reader also rejects incomplete alias coverage.
Ticket 13 stays claimed and 14 stays open; remaining device/comprehension and full
workload/history/consumer-selection evidence are unchanged requirements.

The final audit also aligned full-tree/incremental revision checks with the lazy
browser: every partition's schema must match descriptor inputs, and every recipe
commit/classification-rule revision must match its own descriptor binding. Added
cross-validator negatives for mismatched schemas, recipe commits and rule revisions.
These pass together with the source/alias coverage cases. The collection overflow
fixture now binds its preserved source/provenance headers to its actual descriptor
schema revision; it still verifies byte-exact last-good preservation. Ten trusted
publication/recovery checks pass with these revision checks enabled.


The accepted partition layout is live for saved-data review from
`2d2f7fbeceaef17a48a47bd203677aeb4ebdd231` (Pages run 42501013188). Actual public
native fetch confirmed one source partition and no global provenance fetch, with
six public Chromium/Firefox smoke checks passing. Collector activation remains
outside this browser-review publication; full workload/history qualification is
still open.

## Collector/schema revision transition — November 8, 2026

The handoff's suspected schema mismatch is reproduced with disposable local Git
parents and saved empty acquisition. With a newer collector HEAD and an injected
v3 source overflow, collection preserved the prior source bytes but rebound the
descriptor and provenance to HEAD. Python whole-tree validation accepted it; a
fresh maintained `Catalog.source` read failed with `Schema input binding mismatch`.
The same regression command failed twice before correction:

```
cd tools/catalog-collector
python3 -B -m unittest \
  test_contracts.Contracts.test_collector_revision_change_keeps_retained_source_browsable -v
```

Subsequent collection now defaults to the validated parent's schema pin and checks
the relevant checkout bytes against it before acquisition. The immutable contract
document is included in that checkout scope. Collector-only changes can retain
source blobs; actual contract/schema/reader changes require an explicit schema
revision and matching source documents. Python full-tree, incremental and shared
JavaScript snapshot validation now check every document against the descriptor,
matching the existing lazy browser refusal. Failed/deferred old-schema sources
therefore stop an explicit transition before candidate output, without changing
observations, weakening browser checks or advancing either parent.

Publisher inspection found the same HEAD-only default in its trusted input
bindings. It now independently fetches/validates the caller's exact expected v3
parent to derive the default schema pin; the transferred artifact cannot choose
that authority. Explicit transitions require trusted `publish --schemas-revision`.
This adds a parent fetch/validation cost that full workload qualification must
measure. The prepared scheduled workflow uses the parent default; actual schema
changes need an explicit CLI invocation or reviewed workflow change. No workflow
was dispatched or changed in this follow-up.

The focused test also covers budget-deferred source reuse and a successful
all-source explicit revision transition. A separate disposable checkout verifies
that retaining the schema pin accepts collector-only changes but refuses changed
contract bytes. Cross-validator negatives now cover descriptor, apps and source
schema mismatches in addition to provenance. Synthetic pins/receipts and a Node
invocation of the actual lazy client are local compatibility evidence, not live
collection, physical-browser or capacity acceptance. Ticket 13 remains claimed;
14 remains open/unclaimed and its other acceptance work remains required.

Verification: `python3 -B -m unittest test_contracts test_pipeline_publication -v`
passed the 14 contract and then-existing 10 publication checks (24 total, 95.5 s).
After completing publisher default/explicit-transition handling, the full
`python3 -B -m unittest test_pipeline_publication -v` passed all 12 publication
checks in 64.1 s, including hash-correct mixed-schema refusal before either catalog
write, independent parent-derived schema reuse, artifact-only transition refusal
and explicit trusted transition success. `node tools/catalog-browser/test_catalog.mjs`
passed all 14 checks. `git diff --check` passed. No unaffected browser journeys or
saved seed-plus-three rehearsal were repeated.
