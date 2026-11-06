# Snapshot delivery and GitHub Pages research

Research date: November 6, 2026. Source tree inspected: `8c729a6bf`.
Recommendation, not an accepted product/architecture decision. No site or workflow
was implemented, no repository settings were changed, and no branch was pushed.

## Recommendation

Generate real app HTML pages and a small search index at build time from one
validated, exact catalog commit. Add optional JavaScript filtering and fetch
paginated, per-repository release/asset presentation data only when needed.
Deploy one complete Pages artifact with a manifest identifying catalog SHA,
renderer SHA, recipe-policy SHA and any supplementary metadata observations.
Keep this browser output separate from the authoritative YAML publication.
This is an engineering recommendation based on the contracts and comparisons below,
not a measured performance result.

## Existing repository contract

The authoritative tree consists only of `apps.yaml` and
`repositories/NUMERIC_ID.yaml`. `yaml_publication.py` validates canonical bytes,
path/identity agreement and complete app references, reading a full 40-character
Git commit. `host_catalog.py` currently enforces 52 sources, 2 MiB per YAML file,
96 MiB aggregate response bytes and a 300-second collection allowance. The
workflow publishes using an exact-parent lease; Pages does not need to change
any of these limits. Sources:
[publication loader](../../../../tools/catalog-collector/yaml_publication.py),
[collector](../../../../tools/catalog-collector/host_catalog.py),
[catalog workflow](../../../../.github/workflows/catalog.yml).

The recorded published baseline has 51 repositories, 53 recipe names, 2,145
releases, 29,993 assets and 9,666,397 YAML bytes. Largest source is 1,142,139
bytes. These are the saved publication's measurements, not fresh remote counts.
[Receipt](../../release-catalog/research/next-ten-publication-deployment.json).

The format explicitly excludes derived JSON/TSV indexes from catalog publication.
A browser can be another client generating a **separate presentation artifact**;
adding its indexes to `release-catalog` would conflict with this contract.
Publication time, collection time and effective release observation time differ.
IDs may exceed JavaScript's exact integer range, so emitted browser IDs should
remain decimal strings. Sources: [format](../../../catalog-format-v2.md),
[selection boundary](../../../adr/0001-catalog-facts-and-client-selection.md),
[observations](../../../adr/0002-retained-release-observations.md).

There is already a manually triggered Jekyll Pages workflow, targeting the entire
repository root. `_config.yml` and `CNAME` are inherited site configuration; the
latter contains `am.osowoso.org`. This does **not** establish the fork's active
Pages settings or ownership of that domain. The active Pages configuration,
current site content and account default branch were not queried in this bounded
research. Reconcile or retire the existing deployment workflow before enabling a
new one: custom Pages settings do not bind deployment to one specific workflow.
Sources: [existing workflow](../../../../.github/workflows/jekyll-gh-pages.yml),
[config](../../../../_config.yml), [CNAME](../../../../CNAME), and
[GitHub publishing configuration](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

## Approaches

| Approach | Benefits | Costs and limitations |
| --- | --- | --- |
| Browser fetches and parses YAML | Closely exposes source data; minimal build transformation | Whole-catalog discovery can transfer/parse the current 9.67 MB, adds a YAML parser and exact-integer handling, and needs explicit commit resolution. Does not itself provide rendered app pages. |
| Generate every release and asset as HTML | Ordinary deep links and readable content without JavaScript | Many repeated pages/large HTML expansion as retained history grows; every refresh rebuilds everything. |
| Generate app HTML plus compact search and lazy history data | Small discovery transfer, useful app deep links, bounded history loading, no YAML parser in visitors' browsers | Adds a tested presentation exporter and versioned data contract; cross-deployment stale tabs need deliberate behavior. |

The third option best fits the accepted discovery-first experience. A specific
framework is not selected. Measure generated artifact bytes, initial transfer,
search latency and worst-source history rendering before setting budgets or
claiming scale readiness. Asset count/metadata growth and duplicated HTML can
outgrow today's YAML baseline; avoid embedding all 29,993 assets in the homepage.

## Current official Pages and Actions constraints

Pages serves static HTML/CSS/JavaScript. Project sites default to
`https://OWNER.github.io/REPOSITORY`; one project site is available per repository.
Generate base-path-aware real files such as `apps/NAME/index.html`, with stable
release anchors. This avoids depending on an SPA fallback for shared URLs.
[GitHub Pages overview](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).

Published sites are limited to 1 GB; source repositories have a recommended 1 GB
limit. Deployments time out after 10 minutes. Bandwidth has a soft 100 GB/month
limit. The soft ten-builds/hour rule does not apply to custom Actions publishing.
The current baseline is substantially below the site-size limit, but artifact
expansion and traffic are unmeasured.
[Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits).

Custom workflows can use any static generator. Pages artifacts must contain no
symbolic/hard links; their documented packaging allowance is under 10 GB, which
**does not override the 1 GB published-site limit**. Deploy jobs require
`pages: write`, `id-token: write`, a deployment environment and dependency on the
build job. Use SHA-pinned reviewed actions, following the catalog workflow's
existing convention, rather than copying documentation version tags blindly.
[Custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Refresh and failure recommendation

Prefer a separate Pages build/deploy job after successful catalog push in the
same workflow, with the exact published SHA passed as an output. Keep catalog
publication success and Pages deployment success independently visible. A manual
Pages rebuild should also accept an exact catalog SHA and never collect upstream
releases itself. This avoids adding secrets or token-trigger assumptions.

Do not rely on a `push` trigger on `release-catalog`: pushes made with this
repository's `GITHUB_TOKEN` generally do not start another workflow or Pages
build. Explicit dispatch is an available alternative.
[Workflow triggering](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow),
[Pages publishing configuration](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

A decoupled `workflow_run` listener is viable but must exist on the default
branch, filter for the trusted catalog workflow/branch and successful conclusion,
and obtain the **published catalog commit**, not confuse it with the workflow's
source `head_sha`. A small validated receipt could carry that pin. Treat receipts
as data and execute only trusted renderer code. This is more coordination than
the same-workflow job and is not the first recommendation.
[Workflow-run contract](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_run).

Build from pinned input, validate before upload, and deploy only the complete
artifact. A build failure should leave the prior site deployment in use and be
reported separately from catalog freshness. Use snapshot-keyed data URLs and
content-hashed assets, not mutable `latest` files fetched independently. A stale
tab whose snapshot data has been removed should offer reload rather than silently
mix snapshots. Decide whether to retain a bounded previous snapshot during final
acceptance planning. Do not promise permanent historical Pages URLs: immutable
raw YAML links at catalog commits provide a different, explicit provenance path.
This section is proposed application behavior, not a GitHub guarantee of atomic
browser requests across deployments.

## Remaining human decisions

- Same AM repository/site versus a dedicated Pages repository, and whether an
  existing site must coexist. Verify actual Pages settings before implementation;
  do not carry the inherited custom domain into a new deployment by assumption.
- Accept the hybrid generation recommendation and separate presentation indexes.
- Decide snapshot retention, outdated-tab UX, refresh failure reporting and initial
  measurable performance/size budgets during prototype/acceptance work.
