# Scale catalog coverage to GitHub-backed apps

Type: task
Status: claimed
Triage: ready-for-agent
Assignee: codex
Blocked by: 137

Marek's accepted direction: catalog all GitHub-backed apps first, independently
of recipe migration; migrate straightforward recipes before custom ones.

Use 137's hash-bound discovery inventory to prepare verified app-to-numeric-source
identities. Separate ambiguous/dependency-only URLs, redirects, unavailable/no-release
repositories and non-GitHub sources; never manufacture successful coverage.
Reuse saved first-party identity evidence when available. Deduplicate sources and
architecture instances while preserving distinct AM app identities.

Prepare measured collection batches and snapshot/read bounds for thousands of
sources. Account for API request capacity, transfer/storage, elapsed time, browser
map responsiveness, retained history growth and isolated upstream failures. Keep
existing migrated recipes' freshness and selection behavior. Prefer incremental
collection using ADR 0002 semantics; do not reintroduce retired tooling by default.
Bring an explicit retention/depth/freshness tradeoff to Marek if measured capacity
cannot satisfy the current contract. Verify current API facts against primary docs.

Acceptance: reproducible verified coverage inventory, bounded collector checks,
measured preflight at proposed scope, exact-parent publication rehearsal and a
concrete push/publication package. No installed-host changes implied.

## Migration workflow steering

Catalog enrollment remains independent of recipe migration. For subsequent recipe
batches, use [family validation and bulk exact-instance translation](../../../../tools/recipe-reconstruction/README.md#current-migration-workflow--family-validation-then-bulk-translation),
recorded in [141](141-record-family-level-migration-workflow.md). Routine per-app
payload downloads, static inspection and lifecycle checks are superseded; known
exceptions and uncovered family behavior still need focused assessment.

## Initial API constraint check — November 6, 2026

GitHub documents a primary limit of 1,000 requests/hour/repository for the
Actions GITHUB_TOKEN used by our workflow:
https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api .
List-releases supports at most 100 records/page and excludes tags without a
GitHub release: https://docs.github.com/en/rest/releases/releases .
Therefore thousands of verified sources will need collection spread across time;
the present one-shot daily job cannot simply enroll the discovery inventory.
Discovery names are not yet a verified source count. Metadata identity lookup
also consumes requests and must be checkpointed separately from daily refresh.

## First bounded expansion — November 6, 2026

Marek said “go ahead” after the first catalog-only publication. Implement and
measure an intermediate enrollment ceiling of 128 sources, with at most 52
release-list requests per run, oldest-attempt-first scheduling, untouched-document
preservation and isolated source failures. Keep response/file/history budgets and
100-release page depth. Prepare a verified catalog-only cohort before any push.
This is a measured step toward broad coverage, not acceptance that the current
whole-tree read/validation path can handle thousands of repositories. Preserve
the full-coverage destination and record remaining scale constraints explicitly.

## First cohort prepared

[Report](../research/bounded-catalog-expansion.md) and
[identity evidence](../research/catalog-expansion-identities.json) prepare 77
additional app identities: 131 apps / 128 numeric sources. Scanner output is
6,732 explicit candidate identities across 7,192 recipe files; the 3,524 other
architecture recipe files still need attribution work. Six redirects remain
deferred. Identity review consumed 160 public API reads; it does not edit sources
or silently enroll arbitrary URL mentions.

Implemented separate 128-source enrollment and 52-request per-run limits,
oldest-attempt-first selection, exact preservation of untouched documents,
per-source failure records preserving successful observations, rate/auth stopping,
and publication coverage/pending-app reports. New apps enter the map only after
source success. Prepared cron is every three hours; strict all-source collection
remains available for scopes of at most 52. All previous acquisition/file/history
bounds and the 48-hour client freshness rule remain unchanged. Snapshot reads no
longer validate each blob twice, while retaining distributed-reader, canonical
byte and cross-file checks.

[Fresh three-batch rehearsal](../research/catalog-expansion-preflight.json)
successfully attempts all 128 sources with no failures, preserving every existing
app identity. Final candidate has 131 apps / 128 source documents, 21,699,088 YAML
bytes, largest file 1,159,110 bytes. The [offline full command](../research/catalog-expansion-workflow-replay.json)
then passes in 311.45 seconds / 175.35 MiB peak process RSS under a 1 GiB address-space
limit, excluding HTTP and CI overhead. Node checks confirm the existing browser
parser accepts every document; no real-browser acceptance claim is made.

Broader source attribution, redirects and an incremental snapshot read/write
path remain before qualifying thousands of sources. This ticket stays claimed;
the all-GitHub destination is not complete. The concrete first publication
package is [140](140-publish-bounded-catalog-expansion.md), pending Marek's push call.

146 collector regression tests and 44 reconstruction tests pass. The five final
batch checks additionally verify conservative accounting for failed partial HTTP
reads, request/rate stopping and observation preservation. The final main-report
path passes its dedicated workflow publication test. Full remaining limitations
and scope are in the report; no source push or live catalog expansion yet.
