# Assess larger catalog metadata batches against GitHub quotas and freshness

Type: research
Status: resolved
Triage: ready-for-agent

Marek asks to revisit the inherited 52-source refresh ceiling using official
GitHub quotas and actual API use. Assess around 500 as a candidate, propose and
validate a sensible batch size and schedule for broad coverage with the existing
48-hour selected-release freshness requirement. Distinguish upstream restrictions
from local safety/processing bounds. Metadata only; no recipe migration or
installed-app operations.

## Evidence

[Official quota research](../research/github-refresh-quotas.md),
[combined sizing report](../research/refresh-batch-sizing.md), and
[authorized publication](../research/next-224-publication.md).

## Answer

[Combined sizing report](../research/refresh-batch-sizing.md) and
[portable validation](../research/refresh-batch-validation.json) recommend a
**500-source hourly ceiling**, with 512 MiB / 900-second acquisition and a
30-minute job candidate. The ordinary Actions token permits 1,000 REST
requests/hour/repository; collection uses one serial release-list GET/source,
not one call per app/asset. Live-header/reserve reporting is required before
rollout. The 52 limit, 96 MiB, 300 seconds, history/read bounds are ours.

The unchanged 96 MiB budget succeeds for only 104 of the 500 fixture sources.
With the candidate budgets, both 500-source local publications and full retained
read complete; independent exact-pin checks confirm identities, releases and
observations, correcting the original overly strict attempt-timestamp oracle.
The whole main command also succeeds for all actual 224 enrolled sources in one
batch against exact published history: 126.35 seconds / 284,692 KiB peak process
RSS, 179,239,534 saved response bytes, unchanged history/document guards.

The 750-source fixture provably fails the real publisher's history guard on a
second identical tree. Even a 500-source fixture plus freshly transferred
published history exceeds 128,000,000 bytes (130,275,908 measured). The reader
allows only 1,023 source files plus map. These storage constraints block simply
enrolling the broad queue; they are not GitHub quotas. Local synthetic fixtures
do not qualify live 500-source CI or thousands of upstream identities.

At 500/hour, the existing 6,504-name unverified queue has a 14-hour nominal
rotation versus 42 hours at three-hour cadence; retain the 48-hour selected-record
rule and monitor actual successful in-scope ages. Page-1 refreshes do not freshen
retained records outside its 100 releases. Proposed profile is **not deployed**;
metadata remains independent of recipe migration/installed applications. Broad
snapshot/history and attribution work remains with 138.
