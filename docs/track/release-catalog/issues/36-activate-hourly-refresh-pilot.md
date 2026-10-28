# Activate one 24-hour hourly freshness pilot

Type: task
Status: claimed
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
