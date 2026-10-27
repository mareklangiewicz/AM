# Persist prior state and publish the bounded catalog

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Marek instructed continuation with push/workflow authorization still in effect.
Wire exact previous-publication input into conditional planning and storage.
Publish only validated index/bodies to the unused release-catalog branch from a
separate contents:write/actions:read job. Collection stays contents:read. Both jobs
execute approved checked-out code; no artifact code execution or credential reuse.
Keep six enrolled endpoints, manual-only workflow, no schedules/installers.

## Acceptance

- Bootstrap requires absent publication branch; later runs require exact full prior
  commit. Refuse mismatched/moved refs, invalid prior trees, future times and state.
- Bounded same-run artifact download with identity/digest checks, safe ZIP parsing,
  full tree validation and recomputation from prior + inert attempt evidence.
- Local CAS commit then normal fast-forward push to fixed release-catalog only;
  no force push, arbitrary ref, automatic retry/recollection or history rewrite.
- Focused offline mutation/conflict/conditional tests, then approved bootstrap and
  one exact-prior repeat to validate persistence; record both run/commit pairs.
- Independently read the published pinned index/bodies and verify freshness/hashes.

## Answer

Implemented exact-prior conditional planning and separate artifact-validating
publisher to release-catalog. Bootstrap 40533557297 published efcaeb2f3; pinned
repeat 40533858562 published its child d612ff34b. Both jobs succeeded in both runs
with six HTTP 200 responses. All six repeat condition tuples match prior validators;
no live 304 is claimed. Verified both public commit trees, 12 pinned aliases each,
actual job permission logs and unauthenticated pinned index/selected body reads.
[Findings and persistent exact evidence](../research/catalog-delivery-findings.md)
include a two-commit Git bundle. 66 tests passed before live runs; final ZIP metadata
allocation hardening passes 67 tests and both actual artifact replays. No schedule,
force push, retry, source expansion or installed-app integration.
