# Collection strategy comparison — 2026-10-27

Decision pending with Marek; this is research and a proposed experiment, not an accepted design or run authorization. Sources: [inventory](request-inventory-findings.md), [manual probe](probe-run-40496182929-findings.md), its preserved evidence archive, current recipes, and historical docs/design/version-catalog.md. No new upstream observations were collected.

## Cost and coverage

8,337 literal release URLs checked daily average 347.4 REST requests/hour before overhead. This may fit the conservative 1,000/hour planning baseline; the single real run reported 5,000/hour. Neither proves production capacity. The GraphQL batch cost one point for two repositories with five releases each; it is not a full-coverage benchmark. REST and GraphQL have separate budgets.

REST endpoint snapshots preserve the requested body, fields, array order and query scope, not all upstream history. The default list page has 30 releases; per_page=100 is a different request. Latest and tag endpoints remain distinct observations. Events and ordinary tags remain unsupported in the initial release scope.

GraphQL can preserve neutral upstream observations without choosing versions, but its query defines a new contract: selected fields, explicit ordering and independently paginated release/asset connections. The probe capped releases at five and assets at fifty. More release pages existed in both repositories; none of the returned asset connections was truncated. An incomplete connection must be explicit, never silently treated as equivalent to a REST body.

## Compatibility and ordering

Obsidian recipe lines 15 and 36 split the entire response into tokens and take the first matching AppImage URL. Neovim recipes also parse the raw body. Descriptions are part of that search surface, not only asset objects. WezTerm nightly takes the last matching nightly URL from per_page=100 and separately uses events for identity. These differences are consumer policy and stay outside the collector.

The five saved Obsidian GraphQL tags and their asset name sequences agree with the corresponding first five REST releases. This small sample does not establish equivalence. Historical measurements in docs/design/version-catalog.md reported ordering discrepancies and description URL matches; retain them as evidence at that revision, not universal API guarantees. Renaming GraphQL fields to REST names cannot restore omitted fields, body search surface, or endpoint/order semantics.

The saved query omits REST descriptions, reactions, author/uploader metadata and asset counts/timestamps, among other fields. Adding fields changes size and collection requirements. A GraphQL observation need not pretend to be REST: new consumers could explicitly support it, but that requires a separately tested migration.

## Payload evidence

Offline Python JSON serialization used compact separators with ensure_ascii=False; gzip used gzip.compress with mtime=0. The full REST body was already compact. These are stored-body compression measurements, not HTTP transfer measurements or Git pack sizes.

| Saved Obsidian representation | JSON bytes | gzip bytes |
| --- | ---: | ---: |
| Full REST: 30 releases / 269 assets | 450,991 | 23,377 |
| First five REST releases / 36 assets | 63,608 | 4,844 |
| GraphQL release nodes: five / 36 assets | 10,208 | 2,480 |
| REST projection to comparable query fields | 9,714 | 2,355 |

The illustrative REST projection maps release tag/name/creation/publication/prerelease fields and asset name/size/digest/download URL. It excludes GraphQL-only isLatest and pageInfo and does not prove schema equivalence. Most apparent savings arise from fewer fields/releases; GraphQL transport alone is not a 17-fold compression result.

## Churn and Git growth

All 269 REST assets include download_count and all 30 releases include reactions. These are candidate churn sources, not measured temporal changes. Exact responses cannot drop them while retaining exact-body compatibility. Keep checked time/status separate from bodies so a successful 304 need not rewrite a body. GraphQL projections that omit volatile fields may change less; counters can also be queried through GraphQL, so the useful distinction is field contract rather than protocol alone.

A body byte total is not a Git growth forecast: compression, deltas, changed-file frequency, history retention and timestamp/index updates matter. Measure each. Even a zero-change day cannot establish annual growth. Any extrapolation should state endpoints, polling interval, change rate and retention assumptions and show sensitivity rather than a single fleet estimate.

## Options

| Option | Advantage | Main unresolved cost |
| --- | --- | --- |
| Exact REST snapshots | Closest match to existing raw filters and endpoint semantics | Counter churn, storage/history and request throughput |
| Neutral GraphQL observations | Explicit compact field contract; batching | New consumer contract, order/coverage validation and nested pagination |
| Limited combination | Can retain REST compatibility while studying a future schema | Two collection paths, duplicate storage and reconciliation complexity |

Recommendation: measure exact REST churn first, with an offline neutral projection as a diagnostic. Keep GraphQL as a candidate if REST storage or later consumer requirements justify it. Do not implement two production representations yet. Offline projections are diagnostic artifacts and cannot establish GraphQL ordering, pagination, quota or availability.

## Proposed bounded experiment — requires agreement and separate run instruction

Use six reviewed endpoints on four public repositories: Obsidian list/latest; Neovim list/latest; WezTerm list with per_page=100; sqlitebrowser list with per_page=100. Existing recipes justify the list variants; latest endpoints deliberately test a distinct API shape. This is a small diverse sample, not a representative fleet estimate.

Take three individually authorized observations, approximately baseline, +1 hour and +24 hours. No schedule, sleep-loop collector or push trigger. Each round has at most six upstream GET attempts, no retries, no extra pagination or rate_limit calls; capture response quota headers. Send saved validators on repeats; 304 retains the prior body. Stop the round on HTTP errors, quota exhaustion/rate limiting, transport failure or a conservative response/output size cap to be specified before implementation. Preserve partial/error evidence without calling it a complete observation.

Save exact public bodies and response provenance separately from check status/time. Compare body hashes, changed JSON paths and changes attributable to counters, descriptions, release/asset membership or order. Build a documented offline stable-field projection without changing originals. Use only extracted text filters for compatibility checks; never source or run installer/updater scripts. Missing selections and description-derived matches are findings, not reasons for collector selection logic.

In a disposable local Git repository, commit each observation for both exact-body and diagnostic-projection layouts, with the same timestamp/index policy. Report uncompressed totals, gzip totals, changed bodies, loose-object bytes and packed history bytes under identical Git settings. Preserve enough fixtures and commands to reproduce the comparison. Three observations provide a short-window delta, not a long-term retention conclusion.

No collector, client integration, publication branch or app changes are authorized by this proposal. Agree representation/scope first; then prepare bounded code for review. A push or manual experiment dispatch requires its own explicit instruction.

## Official API references checked 2026-10-27

- https://docs.github.com/en/rest/releases/releases — list pagination and response schema.
- https://docs.github.com/en/graphql/reference/releases — release ordering fields, asset connections and pagination.
- https://docs.github.com/en/graphql/reference/repos — repository release connection arguments.

The 2026-10-27 probe pinned REST API version 2022-11-28. Keep that version in a comparable experiment; current documentation examples may use a newer version.
