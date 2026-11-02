# Expand AppImage migration beyond the original 124-recipe slice

Type: task
Status: resolved
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

**922 compatible recipes are published and accepted**, with 78 frozen exceptions
unchanged. The approved 14-shard live run, independent acceptance and matching
recipe source/daily pin are recorded in the [rollout result](../research/appimage-next-large-batch-20261102/live-rollout.md).
Installed host delivery remains separate.

### Initial prepared result (historical)

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

## Verified identities

The subsequent user instruction, “go ahead finish migration”, authorized advancing
the whole frozen queue. The [bounded acquisition runner](../../../../tools/catalog-collector/large_evidence.py)
completed all 730 identity requests: 669 public identities matched their exact
original owner/name (case-insensitive comparison only), 59 returned redirects and
two returned 404. Redirects were not followed. Release collection attempted all
671 endpoints of the matching identities: 670 accepted responses and one refused
at the unchanged 8,000,000-byte limit. An initial stop on that response's missing
parsed quota was followed by a network-approved resume of **unattempted** URLs;
its retained HTTP 200 headers independently showed quota headroom. No GET was
retried. The resume reconstructed previous results from hash-checked bytes.

[Exact public acquisition evidence](../research/appimage-next-large-batch-20261102/evidence.tar.gz)
SHA256 `2b574f20f705225247c79233168bda2d998562aeec5e96286e5f9a6b0c469c16`
contains original headers/bodies/reports and final accounting. Total retained
response bytes including headers: 230,056,932. The resume's start/end times cover
the resume only; individual reports preserve the original acquisition times.
The credential was explicitly acquired from gh, passed through private pipes,
and never persisted. Four concurrent requests per wave bounded release response
allocation below 32 MB, with 300-second wave and 30-second request deadlines.
The session ceiling was one hour / 1 GB, plus at most one in-flight wave; this is
an evidence-acquisition ceiling, not a change to publication/storage limits.

Both original selectors for all candidates with accepted metadata were evaluated.
[Migration results](../research/appimage-next-large-batch-20261102/prepared/migration.json)
identify 922 compatible paths across 667 new descriptors: 676 x86_64, 245 aarch64,
one i686. Their original exact selected URLs are returned assets. The other 78
paths remain unchanged: 70 identity/release exceptions and eight selectors without
a returned GitHub asset (including Chatbox's external download links). Potential
production reduction is 62,630 lines / 2,927,077 bytes. Candidate syntax and patch
application checks pass. A nonempty selector alone is not accepted compatibility.

### Implemented bounded publication

The metadata measurements establish that one 50-MB tree cannot fit this batch.
Implemented a schema-2 root over 14 independently validated storage shards,
retaining schema-1 shard indexes. The 52-source operational manifest is preserved
byte-for-byte as shard 00; the 667 new descriptors occupy 13 further shards,
chosen by exact measured body lengths (32-MB preparation target) and at most 52
sources. Manifest schema 2 permits 1–52 sources without broadening legacy schema-1
profiles. Each manifest remains <=64 KB and bound by its exact reviewed hash.
[Inventory](../research/appimage-next-large-batch-20261102/prepared/inventory.json)
SHA256 `bf7248af7b047a02fa567a32f8f6f3f8b374e969296e219b3513101dbbeedec0`.

The new workflow validates the complete inventory before credentials, collects
at most four shards concurrently under existing per-run guards, retains each
same-run artifact, then independently recomputes every shard against the exact
root parent. Only all-shard success can publish one atomic root commit. Cross-shard
duplicate aliases, descriptors and conflicting repository locators refuse.
Unchanged shell reader paths/TSV layout preserve managed and standalone readers;
the Python reference reader fetches only root metadata, its selected shard index
and body, all pinned to one root commit. Shard indexes carry their own receipt,
validation, source and run provenance. No response body is synthesized or trimmed.

The existing 50-MB tree cap applies separately to every shard; root metadata and
lookup retain their existing 2-MB caps. The aggregate root ceiling is explicit:
at most 32 reviewed shards, each <=50 MB, plus bounded root metadata. This is a
new sharded format, not a silent increase of legacy TREE_CAP. Compressed Git
objects remain under the existing 128-MB history ceiling. Future growth still
refuses rather than silently increasing that ceiling.

[Offline replay](../research/appimage-next-large-batch-20261102/prepared/replay.json)
uses all exact accepted new bodies and the archived accepted legacy artifact.
Its legacy 304s, run context and revision are explicitly synthetic; new-source
receipt times remain actual saved transfer times. All per-shard ZIP bounds,
publisher artifact recomputations, complete temporary Git body/index roundtrips
and stale-parent refusal pass. Root: 261,415,274 bytes; index: 95,635 bytes;
lookup: 522,798 bytes; Git objects: 26,912,981 bytes; largest shard: 36,316,210 bytes.
These are one replay's measurements, not live refresh or long-term retention claims.

Enrollment and recipe publication remain separate commits/stages. Remote parent
was rechecked as `29e37bd9207ae9557e8f57afa010699c649d4cde`. The explicit home
instruction reserves pushing for Marek's decision; finish local verification and
prepare exact push/run/acceptance/recipe/pin steps before asking for that decision.

## Local implementation and verification completed

Applied all 922 compatible replacements; original candidate hashes match the
prepared report. Its `production_applied=false` records the historical preparation
stage; [final validation](../research/appimage-next-large-batch-20261102/validation.json)
records application and final verification separately. No exception recipe changed.

The all-922 inert install/generated-update run exposed one genuine lifecycle
defect: the AppImage identity guard refused the existing `icalingua++` name.
All other install/update paths, all final selector/hash checks and architecture
failure/retry/integrity/stale checks passed. A focused regression reproduced
`Invalid app identity` before the fix and passed after adding `+` to the closed
AppImage name grammar. All four actual `icalingua++` recipe checks then passed,
including real temporary-root installation and its generated standalone updater.
No second all-922 green run is claimed; the original failed log is retained with
the superseding targeted results. Empty/dot/path/control-character refusals remain.

The catalog suite passed 252 tests before the final focused additions/fix. Final
affected checks pass: 80 AppImage lifecycle, six executable lifecycle, three
sharded delivery, four shard/reader, six controller, two evidence-resume, four
frozen-queue and ten support checks. Counts overlap and are not summed into a
fictional full-suite total. All 82 installed-command container scenarios passed:
32 Debian/dash, 32 Fedora/bash, 18 native Termux. Container tests use inert
binaries and disabled runtime networking; the plus-name regression is separately
covered by the final actual-recipe and helper tests. Workflow YAML and three
embedded Python programs parse; shell syntax and diff checks pass.

[Retained verification logs](../research/appimage-next-large-batch-20261102/validation-evidence.tar.gz)
include the initial runtime failure and superseding checks, container summaries,
source fingerprints and replay results. The home checkout remains untouched by
any installer operation; all runtime tests use temporary roots or containers.

[Exact rollout sequence](../research/appimage-next-large-batch-20261102/rollout.md)
and [read-only acceptance tool](../../../../tools/catalog-collector/accept_large.py)
are ready. Immediate remote controls still showed source/daily pin
`d6e7421579d5a0f65588e39bb72995a675b9f08a`, legacy collector/dispatcher isolation
and no unfinished run. Recheck again at execution. Push, workflow switch, dispatch,
acceptance, recipe publication and repin remain the only operational steps; no
host sync or installed-updater migration is included. Ticket remains claimed and
ready-for-human for that concrete publication decision.


## Answer — approved live rollout completed

[Live rollout and retained evidence](../research/appimage-next-large-batch-20261102/live-rollout.md):
run 41471816957 succeeded across all 14 shards and publisher. Independent acceptance
passed exact artifact/Git recomputation, 1,844 selectors and pinned readers.
Published recipe source and daily pin both `f6b3c349cf4d590d0591b9c601bb8ac01c4fc629`;
accepted catalog `6f21b8c1d2bf271f570a0177bc1068bb9ca43d0a`. No host delivery.
Earlier pending-publication statements above are historical and superseded.
