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

## Accepted adoption direction (2026-10-27)

Marek's current priority is to simplify AM and remove reliance on independently
operated API proxies/sources. Keep app version/asset selection in existing filters;
keep binaries at their original upstream download URLs. An upstream proposal should
use an AM-owned catalog in AM's own repository, not require trust in this development
fork or a new service. This preserves existing AM/GitHub trust; it does not make
catalog metadata or body hashes independent proof of binary authenticity.

Python can remain in CI collection/validation. Consumer/install/updater paths must
stay shell-based with the existing supported utilities, without a new Python or jq
runtime requirement, full-checkout dependency or separately distributed executable
consumer service. Share a small shell reader; adapt CI-published lookup metadata to
make safe shell consumption simple instead of porting the whole Python reader.
Preserve exact response JSON for the existing app-specific filters.

Commit pinning, measured freshness and exact stale acceptance, integrity checks
and explicit refusal remain required. Keep them centralized rather than adding
branches to every recipe. Recipe and generated-updater changes should be small
read-call substitutions and make total client logic simpler; remove genuinely
unused proxy rewriting/quota/token machinery as its callers migrate. Do not hide
a larger client framework behind a superficially small diff or remove support
still needed by other callers.

The next-session frontier is [23: shared shell reader and one small recipe/updater
migration](issues/23-shell-consumer-and-small-recipe-migration.md). Ticket 22's
Python-runtime packaging recommendation is superseded. Its actual update-path
findings and tickets 19–21's Python/opt-in evidence remain useful references.
Implementation is deferred to the next session; this decision adds no installed
migration, installer execution, schedule or automatic workflow authorization.
