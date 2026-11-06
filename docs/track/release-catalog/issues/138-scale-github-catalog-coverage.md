# Scale catalog coverage to GitHub-backed apps

Type: task
Status: open
Triage: ready-for-agent
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
