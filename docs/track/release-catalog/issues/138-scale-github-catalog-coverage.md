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

## First cohort published

Marek authorized the push/publication package in 140. Three successful manual
runs publish all 131 apps / 128 repositories, with successful observations for
every source and zero failures. Final pin `e9d713eb74ca02dca24a5269ace5ee9e28466f41`;
[publication report](../research/bounded-catalog-publication.md) records exact-parent
readback and preservation checks. This supersedes the preparation-only status
above. Installed host is unchanged. Broader attribution/redirects and snapshot
scaling remain; this ticket stays claimed.

## Next bounded cohort — local preparation

[142](142-reduce-full-snapshot-processing.md) reduces repeated decoding/publication
work; same-evidence 128-source replay improves from the recorded 311.45 seconds
to 94.51 seconds, with equivalent output and unchanged bounds.
[143](143-prepare-224-source-cohort.md) prepares 97 additional app identities,
reaching 228 apps / 224 sources. Metadata verification uses 206 bounded requests,
including eleven explicit alias/canonical numeric-ID checks; the original six
deferred renames are included. Fresh local five-batch preflight succeeds for all 224 sources, with zero failures.
[Report](../research/next-224-catalog-expansion.md) and receipts record capacity
and preservation checks; 144 is the pending push/publication package.

Correction to the earlier inventory description: the 3,524 unsupported recipe
bindings span all four scanned architectures, including x86_64, rather than being
solely other-architecture recipes. They need explicit attribution work; an
unmatched template is not proof of a non-GitHub source or custom behavior.
Whole-snapshot materialization, reader/history bounds and the three-hour schedule
still constrain broad coverage. No all-GitHub completion claim or new publication.

## 224-source publication and larger refresh assessment

[144 resolved](144-publish-224-source-cohort.md): source `fde55f598` is pushed;
five successful runs publish all 228 apps / 224 sources, final exact pin
`26d82aa94bb5a8f70449e42500dc78a597583ab3`. Reader, source identity, retained
release and effective-observation preservation checks pass, zero source failures.
[Publication receipt](../research/next-224-publication.md). Installed host unchanged.

[145 resolved](145-assess-larger-metadata-refresh-batches.md) revisits the inherited
52 ceiling using official quotas and actual one-GET/source use. The proposed
500/hour profile gives a 14-hour nominal rotation for the existing 6,504-name
unverified queue (42 hours at three-hour cadence). Full current 224-source offline
main and synthetic 500-source retained publications pass with larger byte/time
budgets. Six focused batch regressions pass. The profile remains proposed; the
deployed workflow remains 52 / three hours.

New quantified storage boundary: a fresh local transfer of published history
(55,312,540 object bytes) plus the 500 fixture (74,963,368 YAML bytes) exceeds the
128,000,000-byte history guard; direct publisher refusal preserves the ref.
The 1,024-file reader also allows only 1,023 source documents. Next broad-coverage
work must address snapshot materialization/history and measured enrollment,
not merely raise the request constant. GitHub's generated-file repository-health
guidance belongs in that design discussion; it is not an accepted storage change.
Preserve selected-record 48-hour freshness, page-scope observations and source
attribution independently of recipe migration. [Assessment and validation](../research/refresh-batch-sizing.md).


## Hourly refresh profile deployed

[146 resolved](146-roll-out-hourly-metadata-refresh.md) implements and publishes
500 attempts hourly, 512 MiB transfer, 900-second cooperative acquisition,
30-minute job, safe quota/reserve and source-age/history diagnostics. The measured
history allowance rises to 256 MiB, enrollment ceiling to 500; actual scope stays
228 apps / 224 verified sources. Full 159-test collector regression passes.
Source `09ae7fe81`, successful run 42366263140 and exact pin
`59b3f3f398bc1013c7b5caf0f37b19a4f3fc9821` verify a full 224-source refresh in
one command (205.27 seconds, zero failures), preserving identities/releases/
observations. [Report](../research/hourly-refresh-rollout.md) distinguishes the
observed core 5,000 allowance from the conservative documented 1,000/hour plan.
No installed or recipe change; natural hourly cron has not yet been observed.

The earlier 128 MB barrier is now superseded by measured 256 MiB headroom for
the 500-source fixture plus published history. This does not remove whole-tree
materialization, the 1,024-file reader bound or retained growth. Continue verified
source attribution and measured cohorts up to the ceiling; qualify a broader
storage/read design before thousands. Selected-release freshness stays 48 hours.
