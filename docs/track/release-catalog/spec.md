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

## Current repository ownership (2026-10-28; authoritative correction)

Catalog reads follow the configured **AMREPO**, exactly as this fork's package
source does. The variable is AMREPO (not APREPO); this fork defaults to
`https://raw.githubusercontent.com/mareklangiewicz/AM/main-marek`. Its catalog is
in **mareklangiewicz/AM**, on release-catalog. An upstream AM installation would
use its own configured repository. This fork must never silently read or fall
back to ivan-hc/AM's catalog. Upstream acceptance/publication is not a prerequisite
for using our fork, including its additional packages.

The shared reader takes the selected raw-GitHub source through AMREPO, validates
it, and derives the owner/repository centrally. Manager installation embeds that
source in the recipe/generated updater for standalone execution; managed updates
pass the manager's current AMREPO. An explicitly set empty source, missing source
in an unprepared script, unsupported/local source, or missing catalog refuses
without a different repository fallback. Pinning, exact stale consent, measured
freshness, integrity and original app binary URLs remain unchanged.

[29: implementation and tracker reconciliation](issues/29-respect-configured-catalog-repository.md)
supersedes the fixed-upstream ownership assumption in tickets 23–28, their linked
records, and the ownership wording in the historical accepted direction below.
The fork publisher's fixed allowlist is correct and stays unchanged. Upstream
portability/submission is optional later work, not the current continuation task.
No new workflow dispatch, collection, schedule or host app execution is implied.

## Accepted adoption direction (2026-10-27)

Marek's current priority is to simplify AM and remove reliance on independently
operated API proxies/sources. Keep app version/asset selection in existing filters;
keep binaries at their original upstream download URLs. For any future upstream
proposal, its installation should use its own configured repository. The original interpretation that our fork must also use upstream AM
is superseded by the current ownership correction above. This preserves existing
AM/GitHub trust; it does not make catalog metadata or body hashes independent proof of binary authenticity.

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

Historical next-session frontier was [23: shared shell reader and one small recipe/updater
migration](issues/23-shell-consumer-and-small-recipe-migration.md). Ticket 22's
Python-runtime packaging recommendation is superseded. Its actual update-path
findings and tickets 19–21's Python/opt-in evidence remain useful references.
That implementation and its ownership correction are now resolved in tickets 23–29;
this historical decision adds no installed migration, installer execution, schedule
or automatic workflow authorization.


## Accepted daily operation (2026-10-28; ticket 40)

Marek accepted daily scheduled catalog collection with a **48-hour freshness**
limit, superseding the initial roughly-24-hour target and hourly pilot direction
for final operation. Daily cron is 03:17 UTC, same six enrolled sources and
conditional collection/publisher contracts; no external timer. Finish the bounded
hourly pilot before remote switch. Existing source-review pin remains required;
remove the pilot-only start/end/count controls for final daily operation.
Failures preserve previous observation ages; exact explicit stale consent remains
required beyond 48 hours. No fabricated timestamps, silent fallback or automatic
retry. This does not migrate installed app scripts or silently update host helper
files. [40](issues/40-daily-refresh-48-hour-freshness.md) records implementation and
activation state; the existing pilot's shutdown/assessment remains ticket 37.
