# Exact next 65-recipe rollout review

Local preparation only. Marek approved exception research/preparation; no push or
collection authorization is inferred. Review the 59 explicit old-name/numeric-ID/
current-public-name mappings in [findings](findings.md#identity-mappings).
Only original aliases are added; 58 new descriptors plus one existing descriptor's
alias cover 65 recipes. Existing 719 descriptors/aliases/body bytes are preserved.
Thirteen exception paths remain unchanged.

## Frozen stages

- Enrollment: `ab04b9d8cb65e9ebbd26a5b6d1b530edc5e8263f` (65 production recipes remain legacy).
- Recipe delivery/daily pin: `5ab112d256683d0cbf27d7fb46a670f71e66406c`.
- Expected remote source and pin: `f6b3c349cf4d590d0591b9c601bb8ac01c4fc629`.
- Expected catalog parent: `6f21b8c1d2bf271f570a0177bc1068bb9ca43d0a`.
- Inventory SHA256: `1bb994e8f4cceb57b5ef11135733e3c79a7a1c4ba330ba53b475e38a693f62dd`.
- 16 independently bounded shards; 777 descriptors. No capacity guard increase.
- [Machine review](rollout-review.json), [evidence/verification](findings.md).

All operational files listed in the review are identical between stages; only
65 recipe replacements differ. Later local review/offline-verifier documentation
must not accidentally change the proposed delivery source or daily pin.

## After explicit rollout approval

1. Recheck source, pin, exact catalog parent, active workflows, and absence of
   unfinished runs. Refuse any drift/overlap; revise the review rather than
   silently replacing its parent. Check fast-forward ancestry locally.
2. Push only enrollment using `git -c core.sshCommand='ssh -F /dev/null' push origin
   ab04b9d8cb65e9ebbd26a5b6d1b530edc5e8263f:refs/heads/main-marek`. Keep the daily pin unchanged so the
   scheduler is gated. No workflow switch is needed: only catalog-shards.yml and
   catalog-schedule.yml must remain active.
3. Dispatch catalog-shards.yml exactly once at main-marek with approved_revision
   equal to enrollment, inventory_sha256 equal to the frozen hash, and
   previous_publication equal to the frozen parent. No automatic rerun/retry.
4. Require successful plan, all 16 collection jobs, and atomic publisher. Preserve
   same-run original ZIPs, logs, metadata and provenance. Stop on any failure.
5. From this reviewed recipe checkout, run read-only acceptance:

   ```sh
   python3 -B tools/catalog-collector/accept_exceptions.py \
     --run-id ACTUAL_RUN_ID \
     --revision ab04b9d8cb65e9ebbd26a5b6d1b530edc5e8263f \
     --parent 6f21b8c1d2bf271f570a0177bc1068bb9ca43d0a \
     --output /tmp/am-65-acceptance-ACTUAL_RUN_ID
   ```

   This uses the same bounded artifact/Git recomputation as the accepted 922
   rollout, additionally binding the new package and queue to source. It checks
   all 987 recipe hashes and 1,974 original selectors against actual catalog
   assets, plus pinned shell/Python architecture readers. Its original-profile
   behavior and combined source/recipe binding have offline tests; live use of
   this new package/profile remains unverified until the authorized run.
6. Only after full acceptance, fast-forward publish recipe delivery and set
   CATALOG_SCHEDULE_REVISION to exactly `5ab112d256683d0cbf27d7fb46a670f71e66406c`. Verify source/pin equality,
   accepted catalog root, exactly the two intended active workflows, and no
   unfinished run. Retain final controls and acceptance evidence.

No host sync, updater rewrite, binary download/install, yadm pointer bump, old
56-source branch merge or unrelated recipe change is included. Existing installed
standalone updaters do not migrate just because recipe source is published.

## Failure boundary

No partial root publication. Artifact failures, parent races, redirects, quota,
size or identity refusals stop delivery; do not loosen limits or repeat collection
to manufacture acceptance. Preserve evidence and prepare a separate follow-up.
Before recipe publication, old recipes remain in use. If abandoning enrollment,
review a normal forward source restoration and matching daily pin; never force
push or silently repoint the catalog. After recipe delivery, rollback must retain
availability of every alias used by the delivered recipes.

Natural sharded daily repeat and long-term Git growth/reliability remain unproven.
The earlier 922 rollout remains the only observed live sharded run.
