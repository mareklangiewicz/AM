# Choose durable progress and fair scheduling

Type: grilling
Label: wayfinder:grilling
Status: open
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
