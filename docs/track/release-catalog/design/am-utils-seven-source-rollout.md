# Seven-source am-utils rollout for approval

Prepared October 31, 2026 under [47](../issues/47-enroll-scoped-migration-sources.md).
This is a local, reviewable source change. No live operation below has been run.
The full candidate source SHA is the commit containing this package, supplied
explicitly with the approval request; it cannot be embedded in its own commit.

## Exact scope

Replace the operational manifest with the byte-identical reviewed
[seven-source candidate](staged-manifest-am-utils.json), SHA256
`96fd3477b59a9806584f155c9180be1cd9c7ce368d02e0973b28afd2e0c4da62`.
The existing six rows are unchanged. The only addition is:

- Repository identity: public `ivan-hc/am-utils`, ID `1225768109`.
- Fetch: `https://api.github.com/repositories/1225768109/releases`.
- Alias: `https://api.github.com/repos/ivan-hc/am-utils/releases`.
- Request ID: `033cc5f80e8fbd7074c6a2e48cace911348e6ff63652618cbf8f3d95cdfb2700`.

The controller binds this exact manifest hash; workflow step labels say seven.
No permission, workflow trigger, cadence, collector count/byte/time bound, recipe,
consumer, host payload or additional AppImage endpoint changes in this package.
The 356 utility recipes are not migrated by enrolling their source.

Historical six-source tests now read the exact manifest from the retained original
baseline archive, rather than assuming the operational manifest stays six forever.
The original archive manifest matched the prior operational bytes exactly. Tests
bind the controller's forwarded hash to the actual seven-source operational file,
preserve all six historical descriptors and exercise first enrollment, conditional
repeat/failure handling, artifact recomputation and exact-prior publication offline.

## Observed live state before rollout

Read-only checks on October 31 found:

- Remote `main-marek` and `CATALOG_SCHEDULE_REVISION` both
  `6dddde9f6f55a7f0919d59fc8be56aa93acb33ac`.
- Current `release-catalog` parent
  `067f236b205d8fe01c6f4e79744887e4979437fc`.
- Only `catalog-collector.yml` and `catalog-schedule.yml` active; all six other
  registered workflows disabled. No in-progress runs in the control API response.
- The installed manager and install module matched the pushed ticket-66 source
  after the user's normal sync. No further host action is part of enrollment.

These are observations, not authority to overwrite intervening changes. Recheck
all controls, the default branch, queued/running collector work and exact parent
immediately before execution. If source/pin/isolation changed, stop for review.
If only a natural daily publication advanced the parent, present the replacement
parent for approval before dispatch; do not silently reuse the stale one below.

## Approval payload and execution order

Approval covers the candidate source push, **one** bounded manual seven-source
collection/publication, its read-only evidence/selector/resource validation, and
then continuing the existing daily schedule with seven sources by repinning the
same reviewed source. It does not cover a second manual run, new source enrollment,
recipe migration, host synchronization or host app execution.

1. Review the full candidate SHA and its diff from the live source above. Confirm
   a fast-forward, unchanged original six rows and all unchanged runtime bounds.
   Recheck live controls and the exact publication parent before pushing.
2. Push that exact source SHA to `origin/main-marek`. **Leave the schedule pin at
   the old source initially.** Its existing equality guard prevents the new source
   from automatically collecting the seventh source before acceptance. Keep this
   rollout window short; a scheduled event in this window will be skipped.
3. Recheck branch SHA and publication parent. Dispatch exactly once:

   ```sh
   gh workflow run catalog-collector.yml --repo mareklangiewicz/AM \
     --ref main-marek \
     -f approved_revision=FULL_APPROVED_CANDIDATE_SHA \
     -f manifest_sha256=96fd3477b59a9806584f155c9180be1cd9c7ce368d02e0973b28afd2e0c4da62 \
     -f previous_publication=067f236b205d8fe01c6f4e79744887e4979437fc
   ```

   The six original descriptors reuse validators from the exact prior catalog;
   am-utils is initially unconditional because it has no published observation.
   Each approved request is attempted at most once, without redirect or retry.
   On an ambiguous dispatch result, inspect run state; never resubmit blindly.
4. Observe the exact run's collector and publisher. Retain artifact ZIPs, their
   API digests and publication provenance before seven-day expiry. Apply the
   acceptance checks below before moving the schedule pin.
5. Only after acceptance, patch `CATALOG_SCHEDULE_REVISION` to the exact approved
   candidate SHA and verify source/pin equality and workflow isolation again.
   Cadence remains `17 3 * * *`; no synthetic schedule event is dispatched. This
   authorizes future natural seven-source daily runs, not another manual run.
6. Record actual source/run/artifact/publication IDs, results and remaining limits
   in ticket 47 and the map. Accept the utility-source stage explicitly before
   unblocking 48. Ticket 49 remains blocked on its separate 50-endpoint enrollment;
   the broader ticket 47 must not be declared fully resolved from this one stage.

## Acceptance checks

- Exactly seven approved descriptors attempted/completed, matching source/context/
  manifest hashes. Inspect each status, actual condition, bytes and timing. An
  initial am-utils 304 without a matching published prior must refuse. Any failed,
  invalid or missing seventh result prevents publication; it must not fabricate age.
- Recompute the candidate from the exact prior plus original transfer evidence;
  verify ZIP digest, body/index/lookup integrity, complete published Git tree,
  exact single parent and branch advancement. All six prior aliases remain active.
- Run the fixed original-selector differential audit against the **actual returned
  am-utils body**, with no additional HTTP or binary execution. Require 356/356
  real asset selections and unchanged recipe hashes. The existing offline verifier
  can be loaded with its `BODY` and `OUT` set to the retained run evidence directory;
  provide its `report.json` with the verified body SHA256. Preserve the October 28
  evidence unchanged. Missing assets block migration acceptance, not permission to
  invent replacement URLs or filters.
- Verify the new alias through shell/Python readers pinned to the actual published
  commit. Measure age from actual `validated_at` with the inclusive 48-hour policy;
  do not run an app installer/updater to query metadata.
- Record actual artifact/tree/history growth and collection/job duration. Bounds
  remain 8 MB/body, 64 KB/headers, 2 MB/index, 50 MB/tree, 105 MB/artifact,
  128 MB/history and 10/30/300-second connect/request/batch limits. Existing job
  timeouts remain five minutes. No claim of live timing or seven-source repeat
  behavior is made from offline replay; the next natural run supplies repeat evidence.

## Failure and rollback

Before the source push, a refused preflight changes nothing. After it, failed or
ambiguous runs must be inspected and their evidence retained without automatic
retry. Do not move the schedule pin to an unaccepted candidate or leave daily
operation blocked indefinitely.

The bounded rollback included in the proposed approval restores the previously
reviewed six-source tree: revert the rollout commit locally, verify the resulting
tree is byte-identical to `6dddde9f6f55a7f0919d59fc8be56aa93acb33ac`, push the
new revert commit as a fast-forward, then repin to that exact verified rollback
SHA. Record it and restore normal six-source daily operation without manually
dispatching another collection. If the tree differs or any intervening source
change exists, stop for a separate review. Never force-push source or publication
history. If a seven-source publication already succeeded, retain that evidence and
catalog history; restoring the old source does not rewrite the catalog branch.

## Prepared evidence

[Offline verification](../research/am-utils-rollout-20261031.json) records the
manifest, retained selector/body audit and replay resource measurements. These
are saved genuine bodies plus explicitly synthetic repeat events in temporary
local Git repositories, not new observations or an operational freshness claim.
