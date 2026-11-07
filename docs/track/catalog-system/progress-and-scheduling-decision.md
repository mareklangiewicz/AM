# Durable progress and fair scheduling

## Current accepted baseline — November 7, 2026

Marek answered “yes to both” to these two choices:

1. If a runner dies, the next run may redo its unfinished work. Preserve the last
   published catalog and accept repeated requests instead of building cross-run
   recovery infrastructure. Work acquired but not published may be lost, including
   complete sources from the interrupted run. No separate checkpoint store,
   cross-run response-replay guarantee or durable per-request journal is required.
2. Public health updates at run start and finish. If a run has a start record but
   no finish record, display “started, no completion recorded”. Do not infer its
   outcome or partial-source counts. Continuous progress updates are not required.

Marek then accepted keeping the existing oldest-first batches and retrying failed
sources on a later scheduled run, without automatic retries inside a run.
Use the existing ordering: never-attempted first, then oldest recorded attempt,
then numeric source ID. Use published attempt metadata; no new durable scheduler
journal is required. If an interrupted run publishes nothing, its work may repeat.
Each selected source gets one acquisition attempt for its requested scope per run;
normal pagination is part of that attempt, not a retry. Keep existing budget,
quota-reserve and auth/rate-stop protections. The next scheduled run still obeys
those protections; it is an opportunity to retry, not an unconditional request.
Do not add the old cooldown counters, jitter or retry-state machinery.

Previously published observations stay intact until a new candidate passes
validation and exact-parent publication. A rerun uses actual new response receipt
times; a failed run does not freshen old data. Existing saved-response replay for
explicit local evidence remains useful, without becoming automatic crash recovery.

These decisions supersede the historical durability/fencing/gate/minute-update
design below. The ticket remains claimed: discovery versus refresh scheduling and
necessary minimal concurrency/publication handling still need simple questions
and human answers. The previous 4:1 weighting, cooldowns and 24-hour replay window
are not accepted requirements. This is planning, with no runtime changes.

## Historical superseded design

Preserved for context only. The following is not implementation authority.

Target design selected November 7, 2026, continuing Marek's “you decide” delegation
and subsequent “go on”. Owner:
[Choose durable progress and fair scheduling](issues/04-choose-durable-progress-and-fair-scheduling.md).
No collector, schedule, budget or persistence implementation changes here.

## Units of work and identity

Maintain three distinct states: discovery candidates, verified identity proposals,
and explicitly enrolled sources eligible for release refresh. Verification never
enrolls a proposal automatically. A discovery cursor describes a finite scanned
input revision and known remaining candidates, not all GitHub or all AM apps.

A refresh work item binds numeric source identity, verified source binding,
requested page size/page limit/reconciliation mode, acquisition/normalization
contract revision, relevant policy digest and input catalog commit. Display labels
and stable/nightly aliases do not create duplicate source requests. Work reuse
compares these inputs explicitly; a matching app name alone is insufficient.

Separate the logical work item from an acquisition attempt and from a run.
Each network retry gets a new attempt identity. A resumed run can adopt a durable
successful acquisition, recording its original attempt/run and receipt times.
It does not claim a new observation or a new HTTP request. A run identity is a
lowercase UUID token; public ordering is a monotonically increasing registration
number allocated by compare-and-swap in the status channel. Registration retries
first check the UUID so a lost response cannot allocate the same run twice.

## Registration, ownership and durability

Register the run before acquisition, with exact inputs, requested work/budgets
and a durable initial state. Require acknowledged public registration for supported
scheduled/live runs; if it is unavailable, stop before upstream acquisition.
Offline saved-response replay needs no public registration or credentials and
cannot claim publication without the explicit publication stage.

Use one fenced acquisition owner per catalog environment initially, rather than
parallel HTTP workers. A monotonically increasing fence token guards durable queue,
checkpoint acceptance and publication requests. A successor may take ownership
only through an atomic lease/registration operation. An expired owner must check
its fence before each request and every state mutation. A stale owner cannot
commit checkpoints or publish, although an already in-flight request can still
complete and consume quota. Never promise exactly-once HTTP activity.

Lease expiry alone must not transfer remote publication authority. The supported
publication gate must reject stale fences, serialize write initiation with owner
transfer, and durably register each intended remote write. Before allowing a new
publisher, prove the prior publisher has terminated and reconcile its in-flight
write. If that cannot be established, block publication rather than risk a late
write. A token check followed by an unguarded Git push is insufficient fencing;
the storage/interface decisions must supply and test this gate. Acquisition can
recover independently while publication remains blocked.

The durable store must survive process termination and loss of the workflow runner,
including cancellation; a runner-temp file or end-of-job artifact alone does not
satisfy this design. The storage ticket chooses the backend, lease timing,
acknowledgment protocol and crash-consistency mechanism, and must demonstrate
this guarantee before live activation. Failure to acknowledge a checkpoint stops
further acquisition rather than quietly falling back to memory-only progress.

Status is a sanitized projection of durable execution evidence, not the private
checkpoint store. Publish public progress on lifecycle changes and at most once
per minute during acquisition, coalescing source updates; register/finalize without
that delay. A failed progress update need not discard already acknowledged private
work, but its measurement time stays unchanged. Require functioning registration
again before the next live run. No token/header/body dumps enter public status.

## Checkpoint boundaries and source atomicity

Before issuing a request, durably record its intent and charge one request slot.
After receiving a complete bounded response, durably record its bytes or a
content-addressed reference, integrity digest, receipt time, pagination evidence,
request parameters and sanitized accounting. Acknowledge this before another
request. Then normalize/validate and acknowledge a complete-scope acquisition
record before advancing the queue. Record terminal source outcomes and retry
eligibility durably even when no new release facts can be accepted.

Intent is not proof of receipt. A crash between upstream completion and durable
receipt may require repeating a request. Count the uncertain intent conservatively
as charged, with received bytes unknown. Never reconstruct an observation time
from resume, file modification, normalization or publication time.

Only a successfully completed requested source scope can update retained release
facts. Durable pages are evidence, not independently publishable partial success.
After interruption, if all scope receipts and termination evidence are durable,
finish normalization without HTTP. Otherwise restart that source's whole requested
scope on its next eligible attempt; do not append a new pagination tail to old
partial pages across process interruption. Keep incomplete evidence until bounded
cleanup, clearly non-publishable. This trades occasional repeated multi-page work
for a simpler, auditable scope boundary. Ordinary uninterrupted multi-page scope
still does not claim a transactional upstream snapshot.

One source failure does not invalidate other complete durable sources. A budget
stop mid-source fails that scope, preserves its old observations, and marks work
not started as deferred/unattempted, with no fabricated attempt time. A cancelled
run stops new requests, checkpoints complete in-flight responses when possible,
and finalizes what is known. Forced termination retains only acknowledged evidence.

## Reuse, merge and publication

Prefer valid pending acquisitions before spending HTTP quota again. Reuse complete
scope evidence for at most 24 hours from its oldest response receipt, with original
observations. Reject future/invalid timestamps. This is a replay eligibility limit,
not a freshness guarantee or deletion policy for already published facts.
On expiry, schedule a fresh attempt; do not freshen or silently mutate saved data.

Revalidate integrity, identity, scope, normalizer/contract revision, relevant policy
and all domain/budget constraints before reuse. A source/policy/semantic-code change
invalidates reuse unless the relevant digests and explicit compatibility identity
still match. Mere unrelated source checkout changes need not invalidate work.
Missing required raw/normalized evidence or a failed integrity check refuses reuse.

Publication remains explicit. Build a candidate from completed eligible acquisitions
and a single pinned parent; validate the entire candidate and reader bounds before
exact-parent publication. Validation failure preserves the remote last-good catalog
and checkpoints; mark blocked work with its cause rather than reacquiring blindly.

On a lease conflict, fetch the new parent. Reapply saved acquisitions only for
sources whose prior source-document digest is unchanged from the recorded base,
and whose identity/policy still matches. Merge against that new parent and fully
revalidate. Thus unrelated-source progress can be reused without HTTP, while a
concurrently changed same source is marked superseded, not overwritten by older
observations. No last-writer-wins timestamp comparison or implicit reconciliation.
If every source is superseded, adopt no release updates; report the outcome.

Allow at most three publication attempts per invocation, including the initial
one. Continued conflict defers publication with durable evidence and releases
ownership. It does not restart collection. Pending evidence stays eligible only
within its replay window and applicable validation limits.

After an ambiguous push result, reconcile exact candidate identity and parent
lineage before creating another candidate: candidate at the ref or in its accepted
ancestry proves publication, even if a later run advanced the ref. Lack of proof
is unknown, not success or confirmed failure. Unrelated lineage/reset blocks
automatic recovery. A later status update records confirmed C without claiming
atomic visibility of C and status S.

Publication success acknowledges incorporated acquisitions for cleanup; it does
not erase their durable run receipt. Unpublished/unknown results cannot be cleaned
up as successful. Evidence may expire under an explicit bounded retention policy,
but expiry must record lost replay capability and never invent a publication result.

## Scheduling and fairness

Use two network lanes: enrolled release refresh, and discovery/identity verification.
Default weighted service is four refresh request slots to one discovery slot.
Count every outbound request, including permitted redirects and retries, against
its lane and the shared run/credential budgets. Initial refresh scope remains one
page of 100, preserving the existing product semantics; deeper scopes are explicit.
Discovery does not receive enrollment authority or extra quota.

Implement weighted round-robin at request boundaries. Multi-page work can pause
between requests while the other lane receives a turn, retaining source staging
within the same live acquisition. If one lane has no eligible work, lend its slots
without accumulating future debt. Do not reserve unused discovery slots or idle
refresh capacity. Already received/replayed work uses CPU/storage budgets, not
fictional HTTP slots; reserve stage time for validation/publication separately.

Within refresh, select eligible sources by oldest durable real attempt start,
never-attempted first, then numeric ID. Retry `not_before` gates eligibility;
recorded attempts advance scheduling even if the run never publishes. Keep last
successful collection and per-release observation ages separately visible.
Within discovery, visit known candidates by oldest verification attempt, then
stable candidate identity; scan cursors bind exact input revisions. Persist both
lane position and source-attempt order across runs, so cancellation does not
continually favor the same first sources.

Freeze the eligible input revision/cohort when registering a run; newly discovered
or enrolled work enters a later run. Within a lane, unfinished multi-page sources
move behind other admitted sources after each page. This avoids one deep-history
scope monopolizing the lane; its facts still commit only after full scope success.
Bound admitted/staged work by the storage budget and defer excess explicitly.

Process a source at most once per run, except continuation of its same multi-page
attempt. Multiple AM identities sharing it cost one source attempt. Manual scopes
do not silently drain automatic refresh capacity; they must use an explicitly
budgeted invocation under the same owner and credential limits. No unbounded
priority bypass. All scheduled work remains subject to permission, quota and
storage gates; fairness is service order when capacity exists, not an hourly SLA.

Keep the present 500-request, 512 MiB/run, 900-second acquisition, 16 MiB/response,
2 MiB/document, 30-minute job and 100-primary-request reserve profile as the initial
measurement ceiling. Discovery and retries share it rather than adding allowance.
Keep the conservative 1,000/hour planning baseline; do not infer durable entitlement
from historical 5,000 headers. No enrollment/reader/history cap increase here.
Check request, byte, monotonic time and available quota gates before each request.
Never start a request that cannot fit known remaining bounds; bounded transport
must stop if an unknown response exceeds its allowance.

Known pending work has explicit scope/counts; undiscovered/unverified universe
size remains unknown. Qualification must measure queue age and starvation for
both lanes, plus retained-release freshness separately. A configuration unable to
meet the eventual freshness target requires a capacity/policy decision, not
mislabelled success or silently disabling discovery.

## Bounded failure and retry policy

Transient transport/timeouts and retryable server errors: one acquisition attempt per
source per run; after the initial failed source attempt, retry the whole source
scope no sooner than 5 minutes, then 30 minutes. Add deterministic nonnegative
jitter of 0–20% keyed by source/attempt so restart cannot redraw an earlier retry.
After three consecutive transient failed source attempts, enter a 24-hour cooldown;
then permit one probe per 24 hours until success or an explicit maintainer reset.
Success clears the episode counter. This bounds automatic pressure, not the
upstream's lifetime failure count. No tight retry loops or in-job sleeping.

Auth/403/429 or secondary-limit indications stop further requests using that
credential for the run. Honor any validated later retry-after/reset deadline and
the primary reserve; without a usable deadline defer at least one hour. Keep the
cause unknown if evidence cannot distinguish forbidden access from a rate limit.
Resume only at a later invocation and never spend quota to probe a known active
cooldown. Credential correction may require maintainer intervention; no privilege
escalation or fallback credential is automatic.

Invalid data/unsupported encoding/document oversize: block that source work under
the current semantic/policy identity. Do not repeat the same failing acquisition
hourly; permit one diagnostic retry per 24 hours, or retry after an explicit relevant
fix. Preserve old facts, record the blocker, and allow other sources through.
An absent/inaccessible identity triggers bounded verification, not automatic
unenrollment or retained-data deletion. Shared byte/time/request/quota stops defer
unstarted sources rather than incrementing their individual failure counters.
HTTP outcomes and exact public reason enums remain the health ticket's task.

## Recovery scenarios and required evidence

| Interruption or conflict | Recovery |
| --- | --- |
| Intent persisted, response not durably acknowledged | Uncertain charged request; reacquire eligible source, with no invented receipt. |
| All scope receipts persisted, normalization unfinished | Replay normalization using original receipt times; no HTTP. |
| Some pages persisted, scope incomplete | Restart that source scope; other complete sources remain reusable. |
| Valid complete-source checkpoint exists, runner lost | Next owner adopts acknowledged evidence after identity/integrity/age checks. |
| Candidate validation fails | Keep last good catalog and evidence; block/revalidate after relevant fix. |
| Another publisher changes an unrelated source | Rebase unchanged-source acquisitions and revalidate without HTTP. |
| Another publisher changes the same source | Mark saved acquisition superseded; preserve newer parent facts. |
| Push succeeds, acknowledgment/status update is lost | Reconcile exact commit ancestry; then report confirmed publication. |
| Cancellation or owner lease expires | Fence stale mutations; retain acknowledged work; unknown in-flight activity remains possible. |
| Public status update fails after private progress | Show last public measurement time/gap; private durable work remains recoverable. |

Implementation acceptance must fault-inject every boundary, kill/replace the
runner, exercise stale owners and lost acknowledgments, preserve all effective
observations, and demonstrate request-weight fairness with paginated work and
repeated interruption. Measure backend/quota/time overhead before activation.
These are required future checks, not tests run by this planning session.
