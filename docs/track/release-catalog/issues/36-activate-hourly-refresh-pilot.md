# Activate one 24-hour hourly freshness pilot

Type: task
Status: resolved
Triage: ready-for-agent

## Scope and authorization target

Approve [ticket 35's concrete plan](../design/hourly-refresh-pilot.md): install
proposed schedule on default main-marek, commit/push exact reviewed source, set
three repository variables with a 24-hour window and approved activation SHA,
observe hourly runs at minute 17 with existing six-source conditional collection
and exact-prior publication. Nominal maximum 24 collection opportunities/144
release GET attempts; API observed-count cap and limits/assumptions are in plan.
At expiry dispatch refuses; disable the schedule and assess evidence/history
before any extension. No app changes, source expansion or indefinite cadence.

## State

Await explicit schedule activation approval. Existing manual workflow still
requires individual approval outside this proposed scheduled pilot window.

Marek explicitly approved activation with “ok”. Final remote prechecks passed: default main-marek, exact source 3ad023822 and publication e8e5cf962, only collector active, no pending collector runs or preexisting schedule variables.

## Activation state

Approved schedule installed and pushed as 466e1facce4e66d4b26c06446fc1e524aa0d76df.
[Verified activation record](../research/hourly-pilot-activation.json) preserves
active workflow inventory and repository variables. Window:
2026-10-28T00:12:16Z <= dispatch time < 2026-10-29T00:12:16Z.
Only collector and dispatcher are active; six unrelated workflows remain disabled.
Four targeted tests pass; prior full suite 111 passed. No extra test dispatch.
Awaiting first naturally scheduled tick for live verification.

Do not push evidence-only commits during the window without an explicitly reviewed
repin: the approved source guard deliberately stops collection after source drift.
Window expiry stops submission; a queued child may finish afterward. Disable
catalog-schedule.yml after expiry and retain run evidence before seven-day expiry.

## Activation completed; first live tick pending

At 2026-10-28T00:19:04Z the scheduled-run listing was still empty (first intended
slot 00:17Z). No extra workflow dispatch was submitted. Bounded observation was
stopped; no background monitor was left running. Activation itself is complete,
but this ticket remains open for first naturally scheduled-run/child verification.
No scheduled collection success is claimed. Retain first-run evidence and verify
child source/prior/artifact/permissions/tree when the first event arrives.

[History baseline](../research/hourly-pilot-baseline.json) records the full
four-commit publication history before the pilot. It is an earlier verified
fetch, not a new independent remote-history measurement at every tick.
Activation evidence is committed locally without pushing it: a source push would
invalidate the approved revision and stop dispatch until a separately reviewed
repin. No repin or extension is implicit.

## Answer — first naturally scheduled run verified

At approximately 2026-10-28T08:56Z, observed exactly one successful scheduled
controller 40640684033 and its successful child 40640700123. Six conditional 200s,
exact prior, artifact digest/recomputation, published tree/parent and permission
checks pass. [Findings and retained evidence](../research/hourly-pilot-first-run-findings.md).
First scheduled path is established; hourly cadence is not. No failed scheduled
events are listed. No extra collection or dispatch was made during verification.
Window/source pin are unchanged; ticket 37 tracks expiry and overall assessment.
