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
and shared installer callers. Unknown external readers are not inventoried.
Consumer migration/selection review is still required before v2 retirement.

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
