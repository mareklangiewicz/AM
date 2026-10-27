# Workflow-token quota probe

Run by `.github/workflows/catalog-quota-probe.yml` in Marek's fork. Uses sh, curl, and jq from the standard runner. No installer or updater is executed. No catalog is published.

The fixed workload is five requests when an ETag is returned: baseline rate limits, one public upstream REST release list, its conditional repeat, one GraphQL query reading five releases and fifty assets from each of two public repositories, and final rate limits. Without an ETag, skip the conditional request. Stop on HTTP failures or GraphQL errors; no automatic retries.

The query requests pagination flags explicitly. These bound the experiment; it does not collect full history or prove equivalence to REST ordering/fields. REST and GraphQL consume distinct primary budgets, so compare their reported limits separately. Account for concurrent repository workflows and authoritative response headers before attributing every counter change to the probe.

The fork's default branch is main, while development is main-marek. The scoped push trigger runs when this workflow or probe files are pushed to main-marek. A manual dispatch requires the workflow to exist on the default branch; it is not currently the run path. Documentation-only pushes do not trigger this probe. There is no schedule.

The Actions artifact contains public response bodies, quota response headers, statuses, and the fixed GraphQL query. No request authorization headers are written. Retention is seven days. Record the run URL, repository commit, selected measurements, and interpretation in docs/track/release-catalog/issues/02-workflow-token-probe.md before marking it resolved.

Local checks: `sh -n tools/catalog-probe/probe.sh` and `shellcheck tools/catalog-probe/probe.sh`. Initial offline fixture checks also covered success with an empty-body 304, GraphQL errors, and HTTP 429 stopping without further requests. Offline results validate control flow, not real token permissions or quotas.
