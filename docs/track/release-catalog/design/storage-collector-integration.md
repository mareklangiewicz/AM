# Collector to observation storage integration

Ticket 17, 2026-10-27. Actual implementation beside the supervised collector;
prototype branches remain historical references. This step stages validated
candidate artifacts using the read-only collector workflow, without remote
publication privileges, a catalog branch, a schedule or app migration.

## Boundary and format

storage.apply(previous_tree, exact_manifest_bytes, inert_attempts, trusted identity,
generated time, source revision and run/attempt provenance) returns a closed byte
tree and per-source transitions. It does not perform IO or mutate inputs. validate
rechecks the entire candidate and all retained bodies. Export is index.json plus
bodies/<request_id>.json, preserving exact response bytes and all upstream fields.
The candidate schema_version=1 is this integration's format, not a promise of a
stable downstream format or adoption of either earlier prototype schema.

The index embeds the exact UTF-8 manifest text, including whitespace, alongside
its exact SHA256; it can therefore independently verify the same hash approved for
the workflow. Descriptor IDs, immutable repository IDs, reviewed aliases, source
revision and run provenance remain distinct. Numeric-only enrollment validation
is shared by workflow and storage through manifest.py. Duplicate manifest/body/
index keys and nonfinite JSON refuse. The manifest still contains exactly six
reviewed sources; no automatic discovery or identity lookup is introduced.

A usable 200 requires complete measured transport evidence, exact length, release
list/latest/tag object shape, positive release IDs, string tags, draft=false,
parseable UTC publication timestamps and an asset list with positive IDs/string names.
It preserves fields and order. A valid empty list replaces an older body. These
checks supplement the accepted restricted-token visibility boundary; JSON shape
cannot independently prove repository visibility or binary authenticity.

Receipt and validation use response_completed_at, with separate explicit measured
time bases. generated_at never refreshes an observation. Request start <= completion
<= attempt finish <= generation, per-source chronological order and prior generation
are checked. A legitimate 304 needs available matching prior bytes/descriptor and
the exact actual prior validators; it changes validation only. No missing-prior 304
retry is added. An unavailable source requires a new valid 200 to recover.

Temporary failures retain prior availability/body/timestamps; new failed sources
stay unknown. 404/410, redirects, non-quota auth refusals, invalid content and
protocol/clock refusals become unavailable while preserving historical bytes.
No status/body from an incomplete transfer becomes an observation. Not-attempted
entries remain unchanged. Removed aliases receive explicit inactive tombstones,
even when their descriptor stays active. Changed targets get new IDs/no validators;
removed descriptors retire. Re-enrolling retired descriptors needs a future explicit
review operation and currently refuses.

Every candidate is atomic: index <=2,000,000 bytes, each body <=8,000,000, total
closed tree <=50,000,000, including retained history in the current tree. There are
no extra files or unsafe body paths. artifact_io.read_candidate checks regular,
nonexecutable files, rejects symlinks/extra directories, bounds reads before loading
and reruns full validation. It reads directories, not arbitrary archives; future
remote artifact extraction must be separately bounded and reviewed.

## Workflow and local publication

The existing manual workflow collects at most six serial GETs under its unchanged
contents:read permission. It first retains inert report/bodies, then calls storage.
A refused batch retains that evidence and a fixed storage_refusal report without a
candidate directory. A valid candidate gets its own directory and a storage report
with per-file byte counts/SHA256s. Invalid individual release bodies generate
unavailable entries and fail the workflow success condition, rather than silently
publishing them. Runtime Python/system are now explicitly recorded in report.json.

publication.publish_local validates a tree and creates one complete local Git
commit, using a private index and atomic compare-and-swap of refs/heads/catalog.
It refuses any configured remote and has no push/fetch/clone operation. It refuses
a stale parent, disables hooks/ambient Git configuration injection and uses an
explicit local commit identity. It conservatively caps current object-file sizes
plus candidate raw bytes at 128 MB before ref advancement; this is an offline
safety bound, not a measured remote pack/retention policy.

lookup_local requires one full commit for index and selected body, verifies the
manifest/descriptor/alias, byte length and digest, measured timing and availability.
It caps blob sizes before reading, refuses future publication/observation times,
uses age <=86,400 seconds as fresh, and requires stale acceptance bound to exact
commit/request ID/body hash afterward. It has no network fallback or installer
entry point. Local tests demonstrate an older pinned generation after a newer
commit and stale-parent refusal. The live workflow stages byte trees only; it does
not invoke this local publication helper or acquire a writer credential.

## Validation and live envelope

62 offline tests pass: 17 collector, 20 supervised transport, four workflow
preflight, and 13 storage/artifact/local-publication/integration tests, plus eight
historical churn checks included in the total. The measured first adapter baseline
is replayed without HTTP; exact bytes and hashes are checked. Additional checks
cover transitions, bounds, alias lifecycle, provenance, candidate safety, pinned
reads/freshness and evidence retention when storage refuses.

Marek authorized continuation, pushes and workflow runs. The live check for this
step uses one new manual dispatch of the unchanged six-source manifest, with the
exact new pushed revision and existing approved manifest hash. Recheck workflow
isolation and record the resulting candidate hashes; no retries or expanded source
set. Remote delivery needs a separate writer implementation and operational design;
this integration does not silently grant collection repository write permission.

## Live verification

[Run 40531417616 findings](../research/storage-integration-40531417616-findings.md)
record successful candidate staging on Python 3.12.3/Linux and independent body/
index/pinned-read verification. The workflow currently starts each run with no
previous tree. Cross-run persistence and live conditionals are not wired yet.
