# Persist prior state and publish the bounded catalog

Type: task
Status: claimed
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
