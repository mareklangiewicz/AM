# Prepare the remaining 78 AppImage exceptions

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

After ticket 67's accepted 922-recipe rollout, Marek approved preparing the next
compatible batch. Classify the 78 unchanged paths, verify explicit redirect
identities and actual selectors against bounded public metadata, preserve all
accepted catalog sources, and prepare reviewable enrollment/recipe candidates.
Source publication, manual collection and installed host delivery remain separate.

## Progress

Natural-repeat check on November 2: latest daily dispatcher was run 41435818820
at 11:18 UTC, before the sharded rollout. Only sharded run is the accepted manual
41471816957. No natural sharded repeat exists yet; no extra run dispatched.

## Answer

[65 compatible redirect recipes are prepared and committed locally](../research/appimage-exceptions-next-20261102/findings.md).
58 new numeric identity/release pairs succeeded, one independently accepted pair
was reused. Both frozen selectors select actual assets for all 65 paths. Four
candidate lifecycle checks cover every inert install/generated update and both
architectures' failure/stale cases. All 13 patched controller/shard checks and
28 focused identity/resume/acceptance-input tests pass. Exact saved-body replay
preserves all old aliases/descriptors/body bytes and passes artifact/Git checks.
The remaining 13 paths stay unchanged with explicit reasons. No natural repeat
yet. [Exact two-stage rollout review](../research/appimage-exceptions-next-20261102/rollout.md)
awaits the separate home-instruction push decision; no push, dispatch or host delivery.
