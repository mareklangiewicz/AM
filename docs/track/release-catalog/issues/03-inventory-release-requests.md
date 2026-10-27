# Inventory current fork metadata requests

Type: research
Status: resolved
Triage: ready-for-agent

## Question

Which exact upstream requests and selection filters must a catalog support in the current fork, and which requests can share observations?

## Acceptance

Inspect scripts as text, without executing installers. Count distinct endpoint/query shapes and sharing across architectures. Record source revision, pagination, named/latest/list semantics, events dependencies, variable-built requests, installer/updater discrepancies, and standalone helper requirements. Distinguish measured counts from unresolved cases. Start with the earlier classifier, but keep request discovery separate from selection conventions.

## Progress

2026-10-27: claimed for a read-only textual inventory of x86_64 and aarch64 recipes at 4a2083e2a. No installation script or installed updater will be executed.

## Answer

See [request inventory findings](../research/request-inventory-findings.md). Scanned 10,686 recipe files as text; found 8,337 distinct literal release-request URLs, plus 164 dynamic occurrences in 91 files left unresolved. Shared exact release URLs across architectures: 1,559. Marked template placeholders separately and recorded events/tags dependencies, pagination, version-line comparisons, and standalone-updater helper requirements. Reproduced the earlier classifier counts (7,230 x86_64; 1,267 aarch64). Added reproducible sh/awk inventory tools; generated bulk TSV files stay outside the repo and can be regenerated.

Capacity correction: one check per literal release URL per 24 hours averages 347.4 REST requests/hour before retries and unresolved cases; exceeding a single hourly budget does not rule out the agreed daily freshness target. Runtime quotas, data churn, payload/Git growth, and helper migration still need experiments.
