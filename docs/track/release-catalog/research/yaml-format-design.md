# Catalog YAML design interview

Provisional design constraints agreed with Marek on November 2, 2026.
This records design discussion; implementation awaits shared-understanding confirmation.

- Simplify the published catalog into a defined YAML subset. Do not distribute raw upstream JSON responses; publish important release facts.
- The catalog offers observed release facts. Clients retain decisions about which release to install, browse, present, or otherwise use.
- Human inspection, understandable diffs, and named-field extraction with short POSIX awk scripts are acceptance criteria.
- Published files must be valid YAML; the shell reader accepts a precisely specified subset with explicit string rules and rejects unsupported syntax.
- Prefer a simple, fast coordinated migration. This fork has one user and few installed apps; prolonged compatibility ceremony is unnecessary.

Open: release coverage/completeness; important fields; meaning and limits of trusted observations; YAML grammar; storage layout; client selection compatibility; freshness and failure handling.

## November 3 answers

- Release coverage remains undecided: prefer multiple available releases, but bound acquisition if full history consumes excessive GitHub quota.
- Trust boundary: Marek trusts the known, inspectable AM workflow on official GitHub-hosted runners, acquiring metadata only from GitHub API. Avoid redundant provenance fields; publication commit time is proposed as catalog timestamp. Per-source freshness consequences remain under discussion.
- Agreed normalized fields: source/release identity, tag, title, release page URL, publication/update times, prerelease status; all assets with identity, original name, download URL, byte size, content type, and upstream digest when available; observation time and acquisition status (timestamp representation still under discussion). No release notes or author profiles initially. Clients interpret architecture/package type and choose assets.
- Adapt consumers directly and verify equivalent release/asset choices before switching publication. No prolonged dual-format rollout.

Primary documentation checked: GitHub List releases supports per_page up to 100 (default 30), with page parameter. GitHub Actions GITHUB_TOKEN primary quota is 1,000 requests/hour/repository, with secondary limits also applicable. More releases per page do not themselves add primary request counts; pagination adds requests. Response size and runtime remain separate costs.
Sources: https://docs.github.com/en/rest/releases/releases#list-releases and https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api

## Settled collection and freshness decisions

Marek accepted Q9–Q11:
- Fetch one page of up to 100 published releases per repository, including prereleases; do not follow more pages initially. Explicitly indicate more pages when present. Absence from this window does not establish nonexistence. No indefinitely accumulating historical archive initially.
- Use Git publication commit time for publication time. Preserve one per-repository checked_at timestamp for the last successful API validation, plus a small check status. Failed sources may retain older data while other sources publish updates.
- Preserve GitHub's latest release designation as a source fact for clients. Acquisition request cost and semantics are being checked before settling the budget.

## Settled layout and grammar decisions

Marek accepted Q12–Q14:
- One YAML file per upstream repository, plus a small YAML map from AM app names to repository files; shared upstream data is not duplicated per app.
- Strings are double-quoted on one physical line, using literal UTF-8 and only escapes for quote, backslash, newline, carriage return, and tab. One shared shell decoder serves consumers. Its small size must be demonstrated before the grammar is finalized.
- Releases and assets are mappings keyed by quoted upstream numeric IDs. Schema keys are fixed, indentation uses spaces, and records have deterministic ID ordering. Clients choose version/display ordering.
- No multiline scalars, anchors, tags, implicit string typing, or other general YAML features outside the schema.

## November 3: reader responsibilities and reopened collection budget

- Q16 accepted: shared reader exposes validated facts; clients apply freshness policy. Initially preserve AM's 48-hour installation limit and explicit stale override; browsing may display older observations.
- Structural shell validation must remain very simple. Marek is willing to reconsider consumer validation and trust publisher validation if achieving that proves difficult; no decision to remove validation yet.
- Proposed by Marek: every YAML file links to the subset/schema description. Exact representation remains to be agreed.
- Q17 accepted: one shared shell interface for release/asset listing and named-field access, without reconstructing raw JSON; clients retain selection policy.
- Q15 not accepted: collection budget and latest handling reopened. Investigate list ordering/selection guarantees, full-history pagination request costs, and how many current upstream repositories exceed 100 releases before choosing between full history and bounded window plus latest request.

## Collection facts checked during Q15 reconsideration

GitHub documents only page and per_page for List releases, no sort parameter or guaranteed newest-by-publication ordering. Listed records do not expose a documented latest designation; fetching all pages cannot by itself preserve GitHub's latest answer. Keep newest-by-publication, newest-by-creation, and GitHub-designated latest distinct. A separate latest endpoint remains necessary if preserving that designation.

Local active sharded inventory inspection found 777 endpoint descriptors across 772 distinct numeric upstream repository IDs (755 list endpoints, 22 latest endpoints). Retained release arrays are first-page observations and do not establish how many repositories have over 100 releases. No live all-repository count census performed. Full history request cost and coverage remain undecided.

## Settled client selection and next experiment

Marek accepted Q20–Q21:
- Drop GitHub-designated latest from the required facts; do not make a separate latest request. Clients explicitly select using available facts (publication/update times, prerelease status, version or repository-specific rules). Existing latest-endpoint consumers need explicit rule review; identical selection is not promised.
- Measure full-history cost before choosing release coverage: pages, response bytes, provisional normalized YAML size, and collection duration. A bounded staged measurement may stop and report uncertainty. Production collection remains unchanged.
- Q18 accepted: every YAML file has a format version and immutable source-document/schema link; readers recognize schema locally without downloading documentation.
- Q19 accepted: demonstrate small parsing and structural validation on valid and malformed fixtures before deciding to omit consumer validation. Grammar may be reconsidered if strict validation is too complex.

This supersedes the earlier requirement to preserve GitHub's latest designation. One-page coverage is reopened pending measurements.

## Q21 measurement result

[Bounded experiment](yaml-history-measurement-20261103/findings.md): uniform sample 24/772 upstream repositories, 23 single-page histories and one 227-release/3-page history; all sampled pagination completed. 26 API requests, 13,117,687 response bytes, 2,338,942 provisional normalized YAML bytes, 27.23 seconds. No production changes or raw response retention. Full coverage remains a decision: sample does not bound rare large histories, asset completeness or Git growth.

## Settled full-history and failure policy

Marek accepted Q22–Q24:
- Collect all published release pages by default, with explicit request/byte/runtime ceilings. If a ceiling prevents completion, report it; never represent partial acquisition as complete.
- If a repository fails partway through acquisition, retain its previous complete observation and mark the check failed, instead of mixing old and new pages.
- Omit unavailable optional fields. Empty quoted strings represent actual empty values; do not introduce YAML null as another scalar type.

Open next: asset-list completeness, first-observation failures, pagination consistency limits, reader interface and remaining scalar/schema details. Exact production ceilings remain to be chosen using broader measurements.

## Settled asset observation and empty/unavailable cases

Marek accepted Q25–Q27:
- Publish embedded asset lists from release responses initially, without additional per-release asset requests. Document that full history means complete release pagination, not independently audited embedded-asset completeness. Revisit if truncation evidence appears.
- Permit exactly {} for an empty mapping: releases: {} means a successful observation found no releases; assets: {} means no assets were returned. Optional unavailable scalar fields are omitted.
- Before any successful observation, publish source identity and failed-check status, omitting release data and checked_at. Later failures retain the previous complete observation and its original check time.

Primary reference for separate paginated asset endpoint: https://docs.github.com/en/rest/releases/assets#list-release-assets . No explicit embedded-array completeness guarantee was established.

## Settled timestamps, file identity and failure vocabulary

Marek accepted Q28–Q30:
- Quote fixed UTC whole-second timestamps, YYYY-MM-DDTHH:MM:SSZ. No redundant epoch fields; readers convert only when needed for freshness.
- Repository YAML paths use stable numeric repository IDs (repositories/ID.yaml), with readable owner/name and numeric identity inside. App mapping provides navigation and aliases survive upstream renames.
- Use small stable check_status/check_reason vocabularies, including distinguishable rate-limit, transport, invalid-response and collection-limit failures. Do not publish arbitrary error messages; detailed diagnostics remain in workflow logs.

## Settled archives, reader interface and snapshot trust

Marek accepted Q31–Q33:
- Preserve GitHub-generated source archive URLs as source_zip_url/source_tar_url when supplied, distinct from uploaded assets.
- Shared reader supports validation, release/asset ID listing one per line, and named scalar lookup with decoding. Missing fields have a distinct nonzero result; false, zero and empty string are valid. Add batching only for demonstrated consumer needs.
- A single pinned Git commit identifies a client command's snapshot; fetch all its files from that commit via GitHub HTTPS. Remove per-catalog-body hashes/sizes and redundant JSON/TSV representations. Retain transfer limits and structural validation; upstream asset digests remain facts.

The design frontier is ready for final shared-understanding confirmation. No parser experiment or production implementation has begun.

## Confirmed checkpoint and completed reader experiment

Marek confirmed shared understanding and authorized the schema/reader experiment ("yes, go ahead"). The prior pending-confirmation boundary is superseded. [Findings](yaml-reader-experiment.md) and [schema draft](../../../catalog-format-v2.md) are retained on main; prototype code is archived on research/yaml-reader-prototype at 8a3e5c623, not merged into production.

Validation and queries fit in 210 lines of shell/awk. Eight test groups pass on mawk, GNU awk and BusyBox awk. The independent YAML parser revealed Unicode line-break folding: three additional fixed escapes \N/\L/\P are proposed, pending acceptance. A real large-history selection case justified an experimental batch projection operation; clients retain all policy. Per-file memory is linear and measured; production budgets/streaming strategy remain to be settled before integration.
