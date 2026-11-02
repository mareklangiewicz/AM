# Complete the approved 65-recipe rollout

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Marek approved ticket 68's exact enrollment -> one collection -> acceptance ->
recipe publication -> daily-pin sequence. Enrollment and one successful 16-shard
run are published. Recipe publication and daily repin require complete acceptance.

## Current result

[Acceptance stopped on reproduced local clock regression](../research/appimage-exceptions-next-20261102/live-rollout-stop.md).
Both full read-only attempts passed artifact/Git recomputation and all 1,974
selectors, then refused at a pinned shell reader. A trace proves a 0.501250-second
backwards wall-clock step; body hash matched and the guard behaved correctly.
No complete acceptance exists, so no recipe push or daily repin. Daily dispatch
remains gated by the deliberate source/pin mismatch; no unfinished run.
Existing rollout approval persists; system time changes are outside scope.

## Next

Establish a stable execution clock, recheck controls and repeat same-run read-only
acceptance for run 41479232632/source ab04b9d8c/parent 6f21b8c1d. Only full acceptance
permits reviewed recipe delivery 5ab112d25 and matching pin. No collection retry,
guard weakening or silent parent/source replacement. Preserve both original refusals.

## Answer — completed November 2, 2026

[Same-run full acceptance and exact approved publication completed](../research/appimage-exceptions-next-20261102/live-rollout-accepted.md).
All 16 shards, 987 recipes, 1,974 selectors and pinned readers passed. Source and
daily pin now equal 5ab112d25; accepted catalog e391f35f6 remains unchanged.
Final workflow/run controls passed. The prior stop above is historical;
finite clock probes passed but the original regression cause remains unverified.
No collection retry or host delivery. Original refusal evidence is preserved.
