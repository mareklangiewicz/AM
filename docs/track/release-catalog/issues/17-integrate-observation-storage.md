# Integrate live collector evidence with observation storage

Type: task
Status: claimed
Triage: ready-for-agent

## Scope and authorization

Marek said to continue and approved pushing and running workflows. Implement the
next actual integration: pure bounded storage apply/validate, closed candidate tree
artifact generation from the collector's measured results, and a local publication
commit fixture. Preserve the six enrolled sources and contents:read workflow.
Verify offline with the saved supervised baseline and focused transition/integrity
checks, then push and run one bounded six-endpoint validation of this integration.
No publication writer, remote catalog branch, schedule or installer change here.

## Acceptance

- Exact entity bytes, measured receipt/validation provenance, manifest/revision/run
  binding and public release-shape checks before accepting observations.
- Conditional 304/prior integrity, failure retention/availability, alias tombstones,
  retired/changed identities, future/out-of-order timestamps and atomic bounds.
- Closed byte tree: index <=2 MB, each body <=8 MB, all files <=50 MB, no stray
  paths/files. Prior and input data must not be mutated on refusal.
- Stage a candidate in the workflow artifact without repository write permission.
  Local Git commit/read checks must preserve a pinned older generation and reject
  stale-parent updates. No remote Git path in the publication helper.
- Record exact revisions, candidate hashes and verified live outcomes persistently.
