# 922-recipe sharded rollout — exact operational sequence

Local preparation only. Source publication remains subject to Marek's explicit
push decision under the home AGENTS.md instruction. No workflow was dispatched,
repinned or enabled/disabled while preparing this package.

## Frozen enrollment stage

- Enrollment source: `9f114d25fff27b0bd2f0ecf561871ca267a9f29f`.
- Inventory SHA256: `bf7248af7b047a02fa567a32f8f6f3f8b374e969296e219b3513101dbbeedec0`.
- 14 shards, 719 descriptors total: the unchanged operational 52 plus 667 new.
- Compatible recipe patch: `prepared/recipes.patch`, 922 paths. The enrollment
  source contains this inert review patch, but has not applied it to programs/.
- Expected prior catalog: `29e37bd9207ae9557e8f57afa010699c649d4cde`.
- Verified remote source and daily variable before publication:
  `d6e7421579d5a0f65588e39bb72995a675b9f08a`.
- At that read, only the legacy collector and daily dispatcher were active;
  the latest 100 runs contained no unfinished run. Recheck before mutation.

The enrollment source is a fast-forward descendant of the verified source, via
the four local continuation/evidence commits and the prepared implementation.
It does not rely on the unrelated 56-source/eight-recipe preparation branches.
No redirects or extra aliases from those branches are accepted by this package.

## After the push decision

1. Recheck source, daily variable, exact catalog parent and workflow isolation.
   Refuse drift or overlap instead of assuming these November 2 observations
   remain current. Verify the enrollment commit's ancestry locally.
2. Push **only the enrollment source** to main-marek using the already documented
   `git -c core.sshCommand='ssh -F /dev/null' push` transport. Do not alter SSH
   configuration or send the later recipe commit at this stage.
3. Verify GitHub registered `.github/workflows/catalog-shards.yml`; disable the
   legacy `catalog-collector.yml`, leaving only the new sharded workflow and daily
   dispatcher active. If registration/isolation fails, stop before dispatch.
   The old daily variable intentionally no longer matches source HEAD, so the
   scheduler is gated while enrollment is unaccepted.
4. Submit exactly one `catalog-shards.yml` dispatch at main-marek with the three
   frozen input values above (`approved_revision`, `inventory_sha256`, and
   `previous_publication`). Do not automatically retry a failed/ambiguous dispatch.
5. Require successful completion of all 14 collection jobs and the root publisher.
   Retain original ZIPs, run metadata/logs and publication provenance. At most four
   shards collect concurrently. Any failed collection prevents root publication;
   prior catalog observations remain untouched and continue aging normally.
6. From the locally reviewed recipe checkout, execute the read-only acceptance
   helper with the actual run ID, frozen enrollment revision, exact parent and a
   fresh output directory:

   ```sh
   python3 -B tools/catalog-collector/accept_large.py \
     --run-id ACTUAL_RUN_ID \
     --revision 9f114d25fff27b0bd2f0ecf561871ca267a9f29f \
     --parent 29e37bd9207ae9557e8f57afa010699c649d4cde \
     --output /tmp/am-922-acceptance-ACTUAL_RUN_ID
   ```

   The helper verifies run/source/attempt, every artifact digest and provenance,
   all-shard storage recomputation against the exact parent, atomic root metadata,
   exact Git parent/modes/paths/blobs, all 1,844 original selectors against actual
   new assets, and actual pinned shell/Python reads for architecture representatives.
   It downloads metadata only. It never dispatches, pushes, repins or installs.
   If any check refuses, do not publish the recipe commit or advance the schedule.
7. Only after acceptance, fast-forward publish the separately reviewed recipe
   commit, then set `CATALOG_SCHEDULE_REVISION` to that exact source SHA. Its
   collector, inventory and daily controller bytes must match the accepted source.
   Recheck source/pin equality, accepted root, exactly the two intended active
   workflows and no unfinished run. Preserve final controls with the acceptance.

No host sync, reinstall, installed-updater rewrite, yadm pointer bump or binary
download is included. Repository recipe publication does not migrate already
installed standalone updaters. The 78 thousand-queue exceptions and the separate
eight prepared redirect leftovers remain unchanged.

## Failure and rollback scope

The root publication is atomic. An incomplete collection or rejected artifact
cannot partially replace it. Git parent races refuse; never force-push or silently
rebase a publication. Do not reinterpret an oversized or redirected source to make
a failed run pass. Preserve its exact evidence before deciding a follow-up.

Before recipe delivery, the old recipes and old catalog remain usable with the
unchanged shell reader. If abandoning enrollment, prepare and review a normal
forward source change restoring the legacy controller/active workflow set and
matching daily pin. Do not reset history or silently repoint the catalog. After
recipe delivery, removing new catalog aliases would break those recipes, so a
rollback must coordinate both source and catalog availability rather than simply
restoring a legacy catalog tip.
