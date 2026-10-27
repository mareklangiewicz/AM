# Release observations exploration brief

Status: exploratory, subject to evidence and revision.

Investigate a shared catalog of observed upstream release metadata for AM, eliminating reliance on third-party API proxies. Keep version ordering and asset selection in consumers. Potential reuse by Portable Linux Apps is a motivation, not an integration commitment.

Experiment control: experimental workflows run only by explicit manual dispatch. Isolate them from existing workflows before enabling repository Actions. Hourly collection describes a possible eventual solution, not the experiment trigger.

Initial scope: public GitHub release endpoints, complete response fields and order where exact response snapshots are used, explicit source/query/pagination provenance, per-observation last checked time and error status. Unsupported endpoints are surfaced rather than silently replaced. A catalog observation describes what upstream reported, not independent software authenticity.

Provisional client behavior: download a small index and needed response files from one publication commit, cache locally, require explicit acceptance beyond a roughly 24-hour freshness target, and offer explicit direct-GitHub checks for unavailable/unsupported data. Missing, invalid, or removed information skips the affected app by default; temporary failures retain previous observations without refreshing their age. More precise status rules need testing.

Provisional collection: reviewed request inventory, no installation-script execution, deduplicated requests, conditional-request state, incremental hourly collection and a dedicated publication branch. Successful checks can publish while failed ones retain older observations. Reassess schedule and representation using actual cost and churn.

First completion boundary: a bounded workflow-token probe, documented results and limitations, and a request inventory sufficient to choose the next prototype. Full collector, generic installer, mass updater migration, scheduled publication, and upstream PR are outside this experiment.

See [earlier design](../../design/version-catalog.md) for prior GraphQL measurements and a different resolved-catalog architecture. Do not combine the earlier sweep's cost with full REST compatibility claims.

## 2026-10-27 continuation

After the bounded baseline/hour experiment, Marek accepted provisional exact REST snapshots and proceeding without waiting for a day observation. Day sampling is optional, not a blocker or scheduled work. Storage/publication design is recorded under design/storage-publication-v1.md; it remains a proposal pending offline verification. Full live collection, remote publication, installer integration and schedules remain outside the current authorized work.
