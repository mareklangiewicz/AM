# Prepare bounded hourly freshness automation

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Prepare an inert, reviewable hourly dispatcher and offline orchestration checks.
Keep the existing six-source manual collection/publisher unchanged. Propose a
24-hour activation window, explicit approved source revision, no app operations,
and a concrete activation/disable plan. Do not install an active schedule or
change repository variables/settings during preparation.

## Answer

Prepared [hourly pilot and activation/stop plan](../design/hourly-refresh-pilot.md),
inert workflow outside .github/workflows, dormant dispatcher and offline tests.
Existing manual collector/adapter/publisher are unchanged. Default branch checked
live as main-marek. Proposed 24-hour hourly window requires explicit approval;
repository variables enforce exact source revision and bounded dispatch interval.
No schedule or remote setting has changed; no collection/dispatch/publication.

**111 tests passed** in 48.902 seconds, including four new orchestration tests.
Proposed YAML parses and active collector is still manual-only. Fixed root API
route formatting afterward; targeted four dispatcher tests passed again. Diff
and local design-link checks pass. Real scheduler-token dispatch, timing and
operational history growth remain unverified until the separately approved pilot.
Next [36](36-activate-hourly-refresh-pilot.md) is ready for a concrete decision.
