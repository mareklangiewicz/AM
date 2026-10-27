# REST observation storage and publication — v1 proposal

Prepared 2026-10-27 following Marek's acceptance of provisional REST-first
collection and moving ahead without waiting for a day sample. This is a
reviewable design for an offline prototype, not an implemented collector,
publication permission, retention guarantee or accepted ADR.

## Why this representation

[Baseline](../research/churn-baseline-40500475496-findings.md) and
[hour repeat](../research/churn-hour-40508899451-findings.md) cover six endpoints.
All six exact bodies changed in 63m26s, only in download/reaction counters;
projection fields and ordered release/asset identities stayed equal. Packed
history grew 4,324 bytes exact versus 458 bytes projected. Stable exact body
files therefore remain worth testing for compatibility. The sample does not
establish fleet storage, long-term growth or an operating quota.

Retain every body byte, field and sequence within the requested response.
Do not sort JSON, remove counters, merge pages or synthesize REST from GraphQL.
The collector never selects a release or asset. A raw page preserves only its
own scope; a page with further Link relations is not complete repository history.

## Module interface and implementation

The storage module presents one operation to the collector:

`apply(previous_tree, reviewed_manifest, attempt_results) -> candidate_tree + report`

The interface accepts inert HTTP results with explicit status, source, times,
headers and bounded body bytes. It performs identity matching, conditional-state
validation, observation transitions, hashing and whole-tree validation. It has
no network or Git side effects. Reject malformed batches rather than partially
writing a candidate tree. A well-formed batch may contain individual failures;
valid observations and retained older observations can coexist.

The HTTP implementation supplies results; a saved-result adapter supplies the
same interface for offline verification. The existing probe is evidence and a
source of fixtures, not an interface the future client must learn.

The publication module accepts a validated candidate tree and its expected
parent commit. It either publishes that complete tree as one commit or reports
a conflict/failure. It never recollects metadata or interprets release fields.

The eventual client interface is `lookup(request_url, publication_commit)`:
return exact bytes plus observation metadata, or an explicit refusal. Resolve
representation/version from the catalog format, and hide path/hash lookup from
app-specific filters. This design does not implement that interface or redirect
any current installer/updater. Existing filters continue to decide versions.

## Reviewed input manifest and request identity

Start with a small reviewed manifest derived from the six measured endpoints,
not automatic enrollment of all 8,337 unverified inventory strings. Record the
manifest's SHA-256 and collection-code commit in publication provenance.

Each descriptor has an exact HTTPS URL, pinned REST version and Accept value.
Compute request_id as SHA-256 of its UTF-8 JSON using sorted keys, compact
separators and ensure_ascii=False; no trailing newline. Do not normalize query
strings, fold URL case, deduplicate aliases by guess, or include credentials.
The descriptor's actual fetch URL determines conditional-state compatibility.

An explicit reviewed aliases map translates consumer request URLs to request IDs.
For example, the old WezTerm recipe URL maps to a descriptor whose URL uses
repositories/120568143/releases?per_page=100. Preserve the original alias,
explicit target and redirect investigation provenance. Changing the target,
query, version or Accept creates a new request_id and invalidates prior
validators; it does not rewrite historical provenance or follow redirects.
Duplicate aliases or aliases to absent descriptors are invalid.

Only public GitHub release list/latest/named-tag paths are eligible initially.
Reject a descriptor outside reviewed hosts/path classes, or responses exposing
draft releases or access-restricted data. Token visibility must not turn private
data into a public catalog. An authenticated response cannot by itself prove
public visibility: verify/enroll public sources explicitly and exclude sources
where the token has privileged visibility until a public-only method is defined.

## Published tree

```text
index.json
bodies/<request_id>.json
```

The publication branch has only the latest validated tree at its tip. The Git
history preserves earlier trees. Body paths are stable for an unchanged request
descriptor, allowing the Git-delta layout actually tested. A body digest belongs
in the index, not in a new filename on every counter change. Do not add gzip
copies, a content-addressed blob store, an all-bodies archive, Git LFS, or a
second projection catalog to v1.

The index contains schema_version=1, generated_at, manifest_sha256,
collector_revision, run provenance, aliases and entries. Each entry contains:

- request descriptor (URL, API version, Accept) and derived request_id;
- observation: relative body path, SHA-256, byte length, received_at,
  validated_at, latest validation status (200/304), response Link header and
  scope="single-response";
- cache validators for the same descriptor (ETag/Last-Modified), separate from
  observation data and the latest response headers;
- latest_attempt: time, outcome, HTTP status if received, and selected public
  diagnostic headers, including Location, Retry-After and quota fields;
- availability: available, unavailable, unknown or retired.

Observation is null when no usable body has ever been recorded. No body path or
hash may point outside bodies/, contain traversal or disagree with request_id.
Entries must refer to regular files with matching digest/length. Index entries
and paths form a closed allowlist; fail validation on unexpected files/symlinks,
duplicate JSON keys, unrecognized schema version or contradictory timestamps.

Header values, errors and upstream JSON are data: no shell evaluation, sourcing,
rendered HTML interpretation or executable file mode. Preserve only an explicit
public response-header allowlist; never persist request authorization, cookies,
tokens or environment dumps. Failed HTTP response bodies stay in bounded run
evidence, not at a successful observation path in the publication tree.

The publication commit ID is supplied externally by Git. Do not embed its own ID
inside index.json, which would require a circular self-reference. generated_at
is the publication time, not the freshness of every endpoint.

## One-entry example

[Example index](storage-v1-example.json) shows the proposed field names using
one real Obsidian response from the hour evidence. It is an illustration, not
a publication tree: the referenced body is in the evidence archive and
manifest_sha256 is deliberately null because a reviewed publication manifest
has not been created yet. A real publication must reject that null value. The example uses the recorded
check-start timestamp to illustrate received_at/validated_at; those per-response
completion times were not separately measured by the probe and must be captured
explicitly in a future collector.
The request descriptor's canonical JSON and SHA-256 are:

```json
{"accept":"application/vnd.github+json","api_version":"2022-11-28","url":"https://api.github.com/repos/obsidianmd/obsidian-releases/releases"}
```

`d92c3c4967197d82f80e71136968483888912ce00376f5cba817553cf6495273`

## Transition rules

| Attempt | Body/observation | Freshness and availability |
| --- | --- | --- |
| Valid 200 | Store exact bounded bytes and their hash; update received_at and validated_at | available |
| Legitimate 304 | Require prior validated bytes, matching descriptor and an actual conditional request; retain body and received_at, refresh validated_at | available |
| Timeout, 429 or 5xx | Retain prior observation, record bounded failure metadata | prior availability remains; validated_at does not move |
| 404 or 410 | Retain prior body only as historical evidence, record explicit absence | unavailable; never serve as a current observation |
| 3xx | Never follow automatically; retain prior data and record Location for review | unavailable pending reviewed remapping; do not refresh validated_at |
| 401/403, invalid JSON/shape, oversized body or invalid provenance | Retain prior evidence, record refusal | unavailable; distinguish quota-related 403 as a temporary rate-limit failure when response evidence establishes that |
| Not attempted this batch | Preserve entry unchanged | generated_at does not refresh it |
| Removed reviewed source | Mark retired, retain alias tombstone for explicit refusal | no current body offered; cleanup can remove its file from the current tree |

Before publication validate top-level shape, whole body completion and expected
public release content without changing bytes. A 200 list [] is a valid empty
observation; it must not be replaced by older nonempty data. A 304 without a
known matching body is invalid and does not trigger an implicit retry. Refresh
validators only from successful responses; retain old validators when a 304
omits them. Keep current response headers separate rather than merging an old
Date/quota value into a new attempt. Stop collection on rate-limit/error bounds;
do not let publication retries become network retries.

Clients may read a retained observation after a temporary upstream failure only
if its availability permits it and its own validated_at is within the accepted
freshness interval. New sources with a transient failure remain unknown. An
unavailable source stays unavailable through later transient failures until a
valid 200/304 restores it. A roughly 24-hour stale observation needs explicit
acceptance; no automatic direct-GitHub fallback or source remapping.

This refines, rather than implements, the exploratory client behavior. Exact
expiry edges, allowable future-clock skew and stale-acceptance UX belong in the
client prototype. Stale policy never changes the reported observation time.

## Atomic publication and selective reads

Prepare a complete candidate from one previous publication commit and one
reviewed manifest revision. Validate hashes, statuses, scope and paths before
constructing a Git tree. A successful no-change batch may still change only the
index because checks advanced; no-attempt/no-change batches need no publication.

Commit the candidate as one child of the exact parent used for preparation.
Push only as a normal fast-forward; if the parent has moved, stop and rebuild
offline against that parent with conflict/provenance checks. Do not force push,
overwrite another publisher or recollect data to conceal the conflict. One
publisher at a time is the initial operating rule.

Clients resolve the configured publication ref to a commit once, then fetch
index.json and selected body paths at that same commit. Verify digest and byte
length before exposing bytes to filters. A branch moving during those reads
must not mix generations. If a pinned file is unavailable, report failure and
do not silently fetch from a newer branch tip. Digest checks prove consistency
with the trusted index, not independent authenticity of the upstream binaries.

The eventual remote publication branch name, source of its initial empty tree,
hosting transport, ref resolution and client lookup integration are operational
choices still to review. An offline local Git fixture exercises the consistency
contract without choosing a hosting service or publishing remotely.

## Collection versus publication privileges

The eventual collector has read permissions and produces bounded inert evidence.
A separate publication job validates a closed tree and gets only the write
permission necessary to publish. It runs reviewed code from an approved source
revision, not scripts bundled into the collected artifact. Reject archives with
path traversal/symlinks, unexpected executable files or missing provenance.
No credentials or installed app state move between collection and clients.

The current workflow remains a read-only manual experiment. This design does
not change workflow permissions, enable a schedule, create a publication branch
or establish remote privilege separation. Those need a concrete implementation
and separate operational authorization.

## Retention and collection budget

Keep normal append-only history for the small offline prototype; no per-run
archive is committed to the proposed publication branch. Current tracker
evidence archives remain historical experiment records in main-marek.

Do not infer an indefinite retention policy from 4,324 bytes of packed growth
across six endpoints. The prototype reports body, index, loose-object and packed
history sizes separately. Before expanding beyond the small manifest, agree an
explicit request/body/job budget and storage threshold, then measure against it.
No automatic history rewriting, rotation or force push. If storage crosses the
agreed threshold, stop publication and discuss a new generation or retention
policy; coordinate any eventual client implications explicitly.

The initial request count remains static-inventory arithmetic, not a scheduler.
Selecting which endpoints are due is collection scheduling, not release ranking.
A future bounded incremental collector must handle uneven activity, failure
backoff and actual quotas while preserving per-source freshness. No full hourly
sweep, fleet enrollment or production cadence is chosen here.

## Smallest next prototype

An offline tool accepts a previous tree, the six reviewed descriptors and saved
baseline/hour attempt evidence. It writes a candidate tree and a validation
report into a temporary directory, then creates a local Git publication commit.
It makes zero HTTP requests and has no remote write path.

Verify through the storage/publication interface:

1. Replay baseline/hour: exact response bytes are preserved and counter-only
   changes remain visible; partial earlier baseline cannot masquerade as complete.
2. Synthetic 304: body stays unchanged, validated_at advances and received_at
   does not. Missing body, descriptor mismatch or missing condition refuses it.
3. Temporary errors, removal, redirects, invalid/oversized bodies and empty
   lists follow the transition table without falsely refreshing old data.
4. Changed aliases/version/target cannot reuse old validators. Unreviewed sources,
   invalid hashes, duplicate keys and unsafe file paths fail before publication.
5. A reader pinned to commit A gets a consistent index/body pair after B is
   published. Concurrent-parent mismatch stops publication without force push.
6. Record index/body/loose/packed sizes and explain differences from the churn
   probe's simpler experimental index. No collector/client integration or live
   workflow run is necessary to answer these questions.

Review the resulting schema and state behavior before building remote publication
or migrating any app. This proposal deliberately leaves long-term storage and
hosting choices open rather than promoting exploratory arithmetic into policy.


## 2026-10-27 offline review refinements

The [ticket 08 findings](../research/storage-prototype-findings.md) support the
bounded interface and transitions, not a production schema or operating cadence.
Marek authorized continuing the review. The following are working proposals for
further offline verification; they authorize no remote operation.

### Receipt, validation and provenance

A future adapter must record request start and response completion separately.
For a complete valid 200, received_at and validated_at use response completion.
For a legitimate 304, only validated_at advances. Preserve the original receipt
and its provenance. Publication generated_at cannot substitute for either time.
Validate request_started_at <= response_completed_at <= generated_at and reject
out-of-order per-source results. A failed/partial response never advances either
observation timestamp. Do not use server Date as the local completion clock.

The saved baseline/hour rounds remain historical evidence with missing individual
completion times. Their labelled round-completion upper bounds are fixture-only;
production validation must refuse them as measured freshness. Prefer separate
received_time_basis and validation_time_basis fields if timing provenance is
retained: one field cannot describe a saved receipt followed by a newly measured
304 correctly. This supersedes the prototype's single timing_basis field.

Embed the reviewed manifest alongside its canonical SHA-256 in the next offline
schema fixture. Keep collection-code revision, evidence/run provenance and the
manifest revision distinct. The illustrative one-entry index remains illustrative.

### Public-only enrollment boundary

A manifest assertion is necessary but insufficient evidence of public visibility.
Before any operational implementation, record an explicit public visibility check
for each repository identity, its time and evidence, and exclude repositories
where collection credentials can see privileged data. A public check alone cannot
make later privileged collection safe: public repositories can become private.

The preferred operational design to evaluate is anonymous public REST collection,
with authenticated publication as a separate stage. Its usable quotas and delivery
cost are unmeasured here; do not infer workflow-token quota applies anonymously.
An alternative authenticated collector needs a demonstrated public-only credential
and revalidation method before adoption. Neither approach is selected for a live
run. This may reopen collection strategy; the offline fixture does not settle it.

Reject drafts, unpublished/restricted observations, unreviewed hosts and descriptor
changes before publication. Response shape checks alone do not prove public access.
The six existing fixture enrollment assertions are experimental inputs only.

### Proposed bounded next-experiment limits

Keep the existing six descriptors; no discovery/enrollment expansion. For the next
offline experiment, cap each body at 8,000,000 bytes, the index at 2,000,000 bytes,
and the candidate tree at 50,000,000 bytes, including retained retired bodies.
Reject the candidate atomically on any breach, preserving the previous publication.
Use at most one supplied result per descriptor per batch; publication retries must
not recollect. The offline runner has a network-request budget of zero.

For a disposable local publication history, stop adding publications if pack plus
index exceeds 128,000,000 bytes under the explicitly recorded packing method.
Measure in a disposable copy before advancing the publication ref. Report ordinary
GC and full-repack sizes separately; do not use favorable repacking as a retention
guarantee. No history rewrite, force push or automatic threshold escalation.
These are conservative experiment caps, not approved fleet or live-job budgets.
Live request/time/error budgets need a separately reviewed collection design.

### Alias lifecycle

A reviewed alias remap creates or references the exact new descriptor identity;
no validator crosses identities. Preserve the former descriptor as retired when
removed from the manifest. Explicitly removed aliases need tombstones even if
another alias keeps their old descriptor active: entry retirement alone cannot
represent alias retirement. Model alias state separately in a later fixture.
Re-enrollment requires an explicit reviewed event and starts without cache
validators or current availability; historical bytes remain evidence until a
valid new 200. A 304 cannot restore an unvalidated re-enrollment.

### Next client question

Proceed with an offline freshness/lookup prototype before defining remote delivery.
Its decisions must preserve receipt and validation provenance and distinguish
available-but-stale data from unavailable or retired data. The proposed initial
boundary is age <= 86,400 seconds fresh, greater age requiring explicit acceptance
for that specific observation digest and publication commit. Refuse future-clock
observations for now; do not silently clamp negative ages. These exact edges are
prototype inputs, not accepted client UX. See [ticket 10](../issues/10-offline-client-freshness.md).
