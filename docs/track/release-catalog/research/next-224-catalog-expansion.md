# Next catalog cohort: 228 apps / 224 repositories

Local preparation for [143](../issues/143-prepare-224-source-cohort.md), November 6,
2026. Published baseline remains 131 apps / 128 sources; no push or deployment.

## Scope and source proof

Adds 97 catalog-only app identities covering 96 additional numeric sources. The
result is 228 apps / 224 sources: 57 existing recipe identities and 171 catalog-only
identities. No recipe, shared client policy or installed-host file changes.
[Identity evidence](next-224-identities.json) retains source paths/hashes, exact
whole-template/literal source bindings, numeric canonical metadata and release-probe
digests. Verification rechecks Git originals and working-tree bytes; 206 bounded
public metadata reads produce all 97 proposals, with zero deferred cases.

Eleven renamed repositories have separately checked alias/canonical public numeric
IDs, including the six previously deferred renames. Redirect review is explicit;
default verification still defers renames. Proposal scope is independent of active
enrollment capacity, but each verifier invocation retains its 200-request cap.
None of this treats arbitrary GitHub mentions as app source bindings. No app
payload downloads, static payload inspection or per-new-app lifecycle tests.

## Capacity and preservation

[Fresh preflight](next-224-preflight.json) starts at recorded published parent
`e9d713eb74ca02dca24a5269ace5ee9e28466f41`; five sequential remote-free child commits
successfully observe every enrolled source. Each attempts 52 repositories, for
260 successful attempts / 224 distinct sources, zero failures. All previous app
identities remain; unattempted documents are byte-identical, retained release IDs
are preserved, and effective observation times never decrease.

| Batch | Seconds including collection/publication | Response bytes | Apps / sources |
| --- | --- | --- | --- |
| 1 | 135.12 | 39,252,127 | 184 / 180 |
| 2 | 134.73 | 27,043,901 | 228 / 224 |
| 3 | 154.82 | 41,611,917 | 228 / 224 |
| 4 | 159.03 | 59,925,254 | 228 / 224 |
| 5 | 137.62 | 28,596,807 | 228 / 224 |

Final candidate `aa2efb77f74c8b0f80a25cbd9ef93a04a3a6c2ff` contains 33,145,346 YAML
bytes, largest document 1,159,110 bytes. The controller peaks at 657,068 KiB RSS
under a 1 GiB address-space limit. Batch timings exclude its initial parent read.
[Whole maintained command](next-224-workflow-replay.json), including reading the
full 224-source parent, succeeds separately in 138.57 seconds / 200,208 KiB peak
RSS under 1 GiB with saved fresh fifth-batch responses. It excludes HTTP/CI setup;
it is not a measured GitHub Actions job. Offline attempt times use receipt times.
Receipts bind the pre-commit source hashes relative to `e38c04cd1`, not a claim
that this candidate already existed in that commit.

Enrollment ceiling is prepared at 224. Unchanged limits: 52 requests/run, one
100-release page/source, 16 MiB/response, 96 MiB/run, 300-second cooperative
acquisition, 2 MiB/document, 1,024 files and 128,000,000-byte local Git history.
The three-hour schedule nominally rotates in five runs / 15 hours. Selected release
freshness remains 48 hours, independent of attempts or publication. Existing
failure/auth/rate stopping and retained observation semantics remain.

The [unchanged browser parser](next-224-parser.json) accepts the 6,278-byte app map
and all 224 source files in Node. No real browser DOM/CORS/mobile/accessibility
acceptance or website rebuild is claimed.

## Validation and limits

[Snapshot-processing changes](snapshot-processing.md) remove duplicate decoding,
prefer the safe C parser with safe Python fallback and reuse unchanged Git blobs.
The snapshot remains fully materialized; thousands of sources are not qualified.
The reader/history bounds, retained growth and collection cadence still constrain
broad coverage. At 52 attempts every three hours, nominal 48-hour throughput is
832 attempts before failures, so all-GitHub coverage will need further scheduling
and snapshot work, rather than enrollment-cap changes alone.

[Validation receipt](next-224-validation.json): the broad collector run executes
149 tests; 147 pass and two declaration checks hit `manifest scope` because the
manifest changed while that process retained its imported old cap. The complete
three-test declaration module then passes on the final configuration, as do two
final enrollment tests and six final source-verification tests. No fresh full
149-test rerun followed. New publication tests cover safe-loader fallback,
one validation/document, unchanged-blob reuse and exact tree additions/deletions.
Regenerating the client policy registry leaves it byte-identical.

[144](../issues/144-publish-224-source-cohort.md) is the concrete push/publication
package awaiting Marek's call. Workflow operation at this scope remains unobserved;
no installed policy/module/recipe refresh, app install/update or yadm bump is included.
Full raw release pages, local Git rehearsal objects, logs and reproducible controllers
remain at `/home/marek/Documents/Codex/am-catalog-expansion-20261106/scaling/`.
Broad all-GitHub coverage remains with 138; this cohort does not complete it.
