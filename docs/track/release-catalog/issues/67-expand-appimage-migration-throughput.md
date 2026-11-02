# Expand AppImage migration beyond the original 124-recipe slice

Type: task
Status: claimed
Triage: ready-for-agent

## Scope

User requires faster, substantial migration throughput. Stop using completion of
the original 124-path queue as the overall migration boundary. Freeze at least
1,000 remaining recipes from the two already understood no-unpack source frames,
preserve exact selectors/aliases and source fingerprints, and prepare compact
candidate replacements in one batch. Keep exceptions out of its critical path.

Static replacements are candidates, not accepted migrations. Verify actual
metadata/assets before operational delivery. Do not blindly raise the 52-source
collector cap or existing time/storage caps to fit the wider queue. Establish a
bounded enrollment/publication design that can process substantial slices while
retaining previously accepted observations, provenance and pinned readers.
New publication and installed rollout remain distinct operations.

## Current result

[Exact frozen payload](../research/appimage-next-large-batch-20261102/payload.json)
and [1,000 candidate replacements](../research/appimage-next-large-batch-20261102/recipes.patch)
cover 732 exact endpoints / 730 distinct identity requests, chosen by most shared
callers first. Wider compatible lexical pool: 2,549 recipes / 2,281 endpoints.
Source hashes and original install/update selector text are frozen; candidate
filters preserve the exact pipeline tail. All 1,000 shell syntax checks and clean
patch application pass. Static recipe reduction: 67,776 lines. No new metadata,
actual-asset validation, operational migration or publication is claimed.

Next work is a bounded collection/publication capacity design for substantial
slices, rather than treating the eight redirect leftovers as the main frontier.
Keep existing guards until measured replacement capacity is specified and tested.
