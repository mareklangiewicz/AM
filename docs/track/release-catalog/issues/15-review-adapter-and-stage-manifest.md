# Review the implemented adapter and stage manifest prerequisites

Type: task
Status: resolved
Triage: ready-for-agent
Blocked by: 14

## Goal

Review the implemented supervised transport and prepare the exact incomplete
numeric manifest and workflow integration proposal needed before live validation.

## Inputs

[Adapter findings](../research/supervised-adapter-findings.md), implemented code in
tools/catalog-collector and [transport/enrollment review](../design/transport-enrollment-review.md).

## Acceptance

- Review concrete adapter/collector interaction, credential isolation, parser bounds,
  failure cleanup and deadline behavior; fix evidenced issues with focused checks.
- Stage the six proposed numeric descriptors with historical evidence references;
  represent SQLite Browser's missing ID explicitly so loading refuses before any
  worker starts. Preserve original consumer aliases and changed request identities.
- Prepare the exact workflow adapter diff as an inactive review artifact, outside
  .github/workflows. Verify context/approved-code revision checks and contents:read
  privilege boundary. Do not enable an active workflow or dispatch anything.
- Reconcile code revision, known identity evidence, runtime/OS compatibility limits
  and the separate one-read enrollment versus six-release validation proposals.
  A runnable manifest and future exact pushed revision must be reviewed before
  requesting a dispatch; do not invent IDs, validated source evidence or approval.

## Scope

Offline preparation and review only. No API/loopback HTTP, actual credentials,
identity enrollment, workflow activation, Actions dispatch, schedule, installed-app
change or remote publication. The previous experiments remain separate historical
evidence. Public hosting and storage/client integration remain separate work.

## Answer

Reviewed the concrete adapter and fixed malformed-header acceptance before HTTP
parsing. Staged the exact six-row incomplete manifest and inactive workflow with
tested context/revision/hash preflight. [Review and run package](../research/adapter-review-and-run-package.md)
records 48 passing offline tests, compatibility limits and distinct enrollment
versus baseline proposals. SQLite remains unenrolled; loading refuses before any
worker/token creation. No active workflow, API request, push or dispatch occurred.
The next live boundary is the separately authorized one-read enrollment proposal,
not another preparation ticket or an automatically authorized collection.
