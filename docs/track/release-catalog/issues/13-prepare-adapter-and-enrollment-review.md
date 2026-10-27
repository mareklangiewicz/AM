# Prepare real-transport and identity-enrollment review

Type: task
Status: resolved
Triage: ready-for-agent
Blocked by: 12

## Goal

Prepare a concrete review package for integrating the offline collector contract,
without running it or changing the active workflow.

## Scope and acceptance

- Inspect existing saved evidence for immutable repository IDs and distinguish
  verified identities from missing/ambiguous mappings. Do not obtain missing IDs
  through hidden HTTP requests.
- Specify an explicit bounded identity-enrollment request plan for missing mappings,
  including own-workflow-repository exclusion. Keep that separate from the six
  release requests in any later collection experiment.
- Propose the real transport/credential adapter, including interruptible absolute
  connect/body deadlines, bounded allocations, actual conditional evidence,
  credential/config isolation and exception redaction. Review concrete workflow
  permission/context inputs and source revision, without changing active workflows.
- Identify the smallest useful offline adapter checks and the exact separately
  authorized live validation request, if one is still needed after review.
- Preserve storage integration, remote publication, schedules and installer migration
  as separately reviewed work; a completed collector transfer is not publication.

No live HTTP, Actions dispatch, source enrollment, schedule or installed-app change
is authorized by this preparation ticket. No day observation is required.


## Answer — 2026-10-27

Prepared the [transport/enrollment review package](../design/transport-enrollment-review.md)
and [hashed saved-evidence audit](../research/saved-identity-audit.json). Three
historical source IDs are supported by recorded Link/redirect/numeric request
evidence; SQLite Browser is missing and AM's current ID must come from trusted
workflow context. Proposed enrollment is one explicit unauthenticated metadata
GET, separate from a later proposed six-release baseline. No request was made.

The review exposed name-reassignment drift in a static name-to-ID manifest.
Propose numeric-ID fetch descriptors only in the operational adapter, with names
as reviewed aliases and new request IDs/validators for changed fetch URLs. Exact
numeric latest routes remain candidates requiring explicit bounded validation.

The proposed supervised HTTP worker supplies a genuine connection event and lets
the parent terminate blocked DNS/TLS/body IO at absolute deadlines. Its wire/frame
bounds, credential path, actual condition evidence, fixed errors and workflow
context/revision checks are specified, not implemented or proven by this review.
The active workflow was inspected and remains unchanged. [14](14-offline-supervised-transport.md)
defines the next offline implementation frontier. Real source enrollment, workflow
wiring, dispatch, storage integration and publication remain separate work.
