# Release catalog exploration

## Notes

Work in Marek's active AM fork, on main-marek. Goal: find a simple reliable approach, evolve it through experiments, then propose it upstream. This map and tickets are intentionally tracked by Git.

Earlier work: [2026-10-20 design and measurements](../../design/version-catalog.md), with throwaway code on proto/release-catalog in tools/proto-catalog/. Preserve that branch and its evidence. The earlier design combines a GraphQL collector, CI version selection, and a generic installer. The newer direction separates upstream observations from app-specific selection and leaves selection on the client. Neither is immutable policy.

## Decisions-so-far

- [01: prior research reconciled](issues/01-reconcile-prior-work.md): retain useful measurements, but distinguish the earlier resolved catalog from the current observation catalog. The reported 825-point sweep is GraphQL evidence, not a REST response-catalog capacity measurement.
- Working direction: collector preserves upstream metadata without ranking releases or selecting downloads; app scripts keep policy. Public upstream metadata is not independent binary authenticity.
- Explore a dedicated AM publication branch, hourly collection, reviewed endpoint inventory, retained observations on temporary failures, per-observation checked times, explicit stale-data acceptance beyond 24 hours, and selective client downloads pinned to a publication commit.
- Raw GitHub response snapshots are the initial compatibility hypothesis. Reconsider format and endpoint strategy based on measurements and reuse needs. Exact-response compatibility and efficient GraphQL batching may conflict.
- Catalog work does not execute the active app installer or installed updaters. Existing app management behavior remains unchanged during experiments.

## Fog

- [02: measure workflow-token behavior](issues/02-workflow-token-probe.md): REST headers and conditional requests, bounded GraphQL batching, actual Actions quotas. Local probe is prepared; a remote run is pending.
- [03: inventory request coverage](issues/03-inventory-release-requests.md): current fork's exact requests, shared upstreams, pagination, unsupported dependencies, and client helper availability.
- [04: compare collection strategies](issues/04-compare-collection-strategies.md): whether REST snapshots, structured GraphQL observations, or a limited combination best balance compatibility, simplicity, payload size, and freshness.
- Retention and Git growth; volatile response fields; large asset lists; removed upstream data; standalone updater migration; actual publishing privilege separation; eventual upstream preferences.

## Progress

2026-10-27: read prior design and prototype source without checking out the prototype branch. Prepared a bounded sh/curl/jq workflow-token probe, using only read permissions and retaining public responses and quota headers as a seven-day Actions artifact. Default branch on GitHub is main while live development is main-marek, so the probe also has a narrowly scoped main-marek push trigger. Publishing/running requires the approved push; no schedule is enabled.

2026-10-27: fc0e2be7d pushed to origin/main-marek with Marek's approval. Probe did not appear in run/check listings or the public workflow registry. [Ticket 02](issues/02-workflow-token-probe.md) is open with ready-for-human triage pending a signed-in Actions configuration check. No runtime quota measurements yet.
