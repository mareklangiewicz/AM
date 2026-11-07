# Choose durable progress and fair scheduling

Type: grilling
Label: wayfinder:grilling
Status: resolved
Assignee: codex-progress
Blocked by: 01

Current resolution: [simplified recovery and final reporting](#answer--simplified-recovery-and-final-reporting-november-7-2026).
The following reopening note and intermediate answers are chronological history.

## Historical reopening — simplicity correction, November 7, 2026

Marek rejected the proposed separate checkpoint store as too complex and requires
prioritizing simplicity of implementation. He permits relaxing recovery guarantees
and asks for simple questions before further decisions. The previous Answer and
linked design are preserved as historical proposals, not implementation authority.
Cross-run durable replay, fencing/gates, retry machinery and related requirements
must be reconsidered with him. No replacement recovery design is selected yet.

## Question

What simple recovery and scheduling rules preserve the last published catalog
and truthful observations while permitting repeated work after interruption?

Build on existing oldest-attempt batching and discovery checkpoints. Keep discovery,
verified identity/enrollment and release refresh distinct. Define work identity,
source/requested-scope atomicity, checkpoint boundaries during a run, validity
against source/policy changes, retry/backoff and fairness. Separate known pending
work from an unverified or unmeasurable discovery universe.

Walk through interruption after acquisition, normalization, durable checkpoint,
validation and publication; process death mid-source; failure/oversize; budget/
quota reserve stop; cancellation; concurrent runs; and exact-parent conflict.
Decide whether and when saved valid acquisition can be rebased/revalidated without
another network request, and when reacquisition is necessary.
Do not promise exactly-once network activity across an unknowable crash window.

Set recovery guarantees and bounded retry policy with Marek. This ticket owns
logical state/semantics; the storage ticket chooses the physical persistence and
maintenance mechanism. Preserve old retained-release effective observation times.

## Historical superseded answer — November 7, 2026

Marek said “go on” after delegating the preceding design choice with “you decide”.
Continuing that decision delegation, selected
[Durable progress and fair scheduling](../progress-and-scheduling-decision.md)
as the target semantics. This records an agent-selected design under delegation,
not a claimed human interview or an operational change.

The linked resolution owns work/run/attempt identity, durable registration and
fenced ownership, response/scope checkpoints, 24-hour complete-acquisition reuse,
original observation preservation, same-source conflict refusal and unrelated-
source rebase, publication reconciliation, 4:1 request-weighted refresh/discovery
service, eligibility ordering and bounded retries/cooldowns. It walks each
interruption boundary and names the required future fault-injection evidence.

Source scopes remain atomic; incomplete pagination restarts after interruption,
while complete durable acquisitions can be replayed without HTTP. A receipt lost
before durable acknowledgment can cause a repeated request. Lease expiry alone
cannot authorize a competing remote publisher. Existing request/byte/time/quota
ceilings remain the initial measurement profile, with discovery sharing them.

The physical store, ownership/publication-gate realization, lease timing and
cleanup/retention remain with the storage/interface decisions; health owns exact
public metric definitions and enums. Those existing tickets cover the newly
precise obligations, so no duplicate decision ticket is needed. Storage must
demonstrate runner-loss durability and the publication gate before activation.

No runtime implementation/tests, remote operations, schedule/enrollment changes,
installed-host operations or push accompany this resolution. Planning link/graph
and whitespace checks apply; the selected retry/fairness values are design policy,
not measured capacity or an hourly freshness guarantee.

## Accepted simplification — November 7, 2026

Marek answered “yes to both”: a new run may redo unfinished work after runner
loss, preserving the last published catalog; public health need only update at
start and finish, with “started, no completion recorded” for a start lacking a
finish. The [current baseline](../progress-and-scheduling-decision.md#current-accepted-baseline--november-7-2026)
owns the revised recovery scope. Cross-run durable acquisitions, separate store,
fencing/lease machinery and continuous progress are no longer requirements.

The earlier Answer is superseded historical context, including its unreviewed
scheduling/retry choices. This ticket stays claimed until simple scheduling,
retry and minimal publication/concurrency questions have been answered. Do not
resolve it from these two recovery answers alone.

### Accepted batching and retry policy — November 7, 2026

Marek answered “yes” to keeping existing oldest-first batches and retrying
failures on the next scheduled run, without automatic retries inside a run.
The linked current baseline records ordering, one source-scope attempt per run
and existing budget/quota/auth protections. Published attempt metadata suffices;
interrupted unpublished work may repeat. No persistent retry counters, jitter or
cooldown machinery is required. Discovery/refresh allocation and minimal
concurrency/publication handling remain open; the ticket stays claimed.

### Accepted manual discovery — November 7, 2026

Marek answered “yes” to keeping discovery of new apps manually triggered for now,
while scheduled runs only refresh already-enrolled sources. Discovery and verified
identity proposals remain separate from explicit enrollment. No mixed-work queue,
4:1 service ratio or persistent fairness state is required. Applicable resource/
quota limits still apply to manual work. Minimal concurrency/publication handling
remains open; the ticket stays claimed.

### Accepted single active collection — November 7, 2026

Marek answered “yes” to running one collection at a time and letting the active
run finish rather than cancelling it when another is triggered. Use ordinary
workflow concurrency controls shared by scheduled/manual collection. No custom
lease/fencing service or durable queue is required. No guarantee that every
pending trigger executes is implied. The current baseline records this choice;
publication-conflict and failed-start-update handling remain open.

### Accepted stop on publication conflict — November 7, 2026

Marek answered “yes” to stopping a run if publication conflicts with a newer
catalog, leaving a later scheduled run to try again rather than automatically
merging/rebasing/retrying. The newer catalog is preserved; unpublished work need
not survive. The linked current baseline records this behavior. Failed-start-
update handling remains the last open recovery-policy question here.

## Answer — simplified recovery and final reporting, November 7, 2026

Marek explicitly replaced the start/finish proposal: no public “run started”
update. Attempt a final health summary for every normal outcome, including
collection, validation and publication failures. Abrupt termination or failure
to publish that summary may leave no report. Show the previous report with its
original timestamp as “last reported run”, never as proof of the latest attempt.
Link to the specific Actions run and recent collection runs; Actions may require
GitHub sign-in, while the public summary remains readable without it.

Together with the preceding live answers, this resolves the recovery/scheduling
policy: rerun lost unpublished work, retain oldest-first batches, retry only on a
later scheduled run, keep source discovery manual, allow one active collection
without automatic cancellation, and stop publication on an exact-parent conflict.
The [current baseline](../progress-and-scheduling-decision.md#current-accepted-baseline--november-7-2026)
owns the complete current resolution. Earlier answers and comment sections are
chronological history; all public-start and cross-run durable-recovery requirements
are superseded. No separate store, leases, retry queue or reconciliation service.

Implementation simplicity remains the priority. Exact summary semantics/bounds,
public snapshot storage and workflow interfaces remain with their owning tickets.
No runtime implementation, deployment, dispatch, push or installed-host changes
accompany this planning resolution.
