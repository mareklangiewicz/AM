# Prepare real-transport and identity-enrollment review

Type: task
Status: open
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
