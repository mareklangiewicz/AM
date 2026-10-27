# Measure workflow-token release reads

Type: prototype
Status: open
Triage: ready-for-human
Blocked by: 05

## Question

What quotas and conditional-request behavior does this fork's real GITHUB_TOKEN expose, and can it read public upstreams using both REST and a small GraphQL batch?

## Acceptance

- Workflow runs only by explicit manual dispatch, with a matching job event guard, read-only contents permission, no publication, and bounded fixed requests.
- Record REST and GraphQL budgets separately; perform a conditional REST request only when an ETag exists.
- Record HTTP status, response headers, GraphQL cost/errors, payload size, and pagination flags. Treat 200 instead of 304 as evidence requiring interpretation, not automatic success of conditional caching.
- Preserve response evidence as a short-lived artifact and append the run URL and interpretation here.
- Document inability to run or access logs without claiming measurements.

## Progress

2026-10-27: prepared tools/catalog-probe/probe.sh and .github/workflows/catalog-quota-probe.yml; shell syntax, ShellCheck, and YAML checks pass. Offline fixtures passed for success with an empty-body 304, GraphQL errors, and HTTP 429 stopping without further requests. Read-only git ls-remote confirmed SSH connectivity and that origin/main-marek still matches local HEAD. Real Actions run is pending approval to push. The workflow covers two distinct public upstreams in one small GraphQL query; it does not reproduce the earlier full sweep or establish 24-hour coverage.

## Comments

Marek authorized use of mareklangiewicz/AM. The inherited home AGENTS.md requires asking before a push. An early sandboxed gh check incorrectly suggested invalid credentials. Superseded: gh works with the keyring outside the sandbox. Report push/authentication results accurately.

2026-10-27, after push approval: pushed fc0e2be7d to origin/main-marek successfully. GitHub Actions run listing filtered to main-marek returned zero runs; this commit has no check runs. The public workflow listing reports five existing active workflows but does not list Catalog quota probe. The browser Actions URL returns a signed-out 404, so it does not establish the underlying repository setting. No real token quota or ETag measurements were obtained.

Superseding diagnosis via gh: repository Actions permissions report enabled=false. Existing five workflows are individually active, but the repository-wide switch prevents execution. No Actions settings have been changed.

Marek requires experimental workflows to run only by manual dispatch and wants to avoid triggering other workflows. Removed the push trigger and added a job-level event guard. Next: push the manual-only revision with approval; agree how to register it on default main, disable existing workflows while repository Actions is still off, and enable Actions only after verifying isolation. Do not dispatch an experiment without an explicit run instruction. No live quota measurements yet.

2026-10-27 continuation: manual-only revision 4a2083e2a is pushed. gh confirms Actions remains off and there are no pending runs. Registration/isolation is tracked separately in [05](05-isolate-and-register-manual-probe.md); no dispatch or repository enablement has occurred.

2026-10-27: default branch changed to main-marek with Marek's approval. gh workflow list now shows Catalog quota probe (398162689). Registration is resolved without a stub. Repository Actions is still disabled; [05](05-isolate-and-register-manual-probe.md) now covers only remaining isolation/enablement. No quota probe has been dispatched.
