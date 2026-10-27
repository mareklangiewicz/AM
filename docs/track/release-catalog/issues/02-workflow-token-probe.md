# Measure workflow-token release reads

Type: prototype
Status: claimed
Triage: ready-for-agent

## Question

What quotas and conditional-request behavior does this fork's real GITHUB_TOKEN expose, and can it read public upstreams using both REST and a small GraphQL batch?

## Acceptance

- Workflow has read-only contents permission, no publication, no schedule, and bounded fixed requests.
- Record REST and GraphQL budgets separately; perform a conditional REST request only when an ETag exists.
- Record HTTP status, response headers, GraphQL cost/errors, payload size, and pagination flags. Treat 200 instead of 304 as evidence requiring interpretation, not automatic success of conditional caching.
- Preserve response evidence as a short-lived artifact and append the run URL and interpretation here.
- Document inability to run or access logs without claiming measurements.

## Progress

2026-10-27: prepared tools/catalog-probe/probe.sh and .github/workflows/catalog-quota-probe.yml; shell syntax, ShellCheck, and YAML checks pass. Offline fixtures passed for success with an empty-body 304, GraphQL errors, and HTTP 429 stopping without further requests. Read-only git ls-remote confirmed SSH connectivity and that origin/main-marek still matches local HEAD. Real Actions run is pending approval to push. The workflow covers two distinct public upstreams in one small GraphQL query; it does not reproduce the earlier full sweep or establish 24-hour coverage.

## Comments

Marek authorized use of mareklangiewicz/AM. The inherited home AGENTS.md requires asking before a push. Local gh auth status reports an invalid configured credential; connector reads remain available. Report push/authentication results accurately.
