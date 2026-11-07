# Choose durable progress and fair scheduling

Type: grilling
Label: wayfinder:grilling
Status: resolved
Assignee: codex-progress
Blocked by: 01

## Question

What logical queue/checkpoint state and scheduling rules let work resume safely
without repeating completed successful acquisition or falsifying observations?

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

## Answer — November 7, 2026

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
