# 52-source enrollment and 107-recipe delivery

Local preparation after migration commit `2496e90e4419ab6ec29a252e5143cc8526430946`.
No push, dispatch, repin or host delivery is authorized by this file.

## Two exact candidates

`prep/appimage-52-enrollment` is based on accepted public source
`cc2ba588d5446df5a9fdb5366ad689e672986a2a`. It carries the 52-source collector,
manifest/controller/workflow switch and evidence, while preserving all 107 recipe
files and the AppImage module at their previously published bytes. Its focused
CI/storage/reader tests are independent of the unpublished recipe migration.

`main-marek` merges that enrollment candidate with `2496e90e4`. It carries the
107 migrated recipes, dotted-name support and their tests. The enrollment candidate
is its ancestor, permitting a later fast-forward recipe publication. Exact full
SHAs are supplied with the review; neither candidate's SHA can be embedded in itself.

Both use manifest SHA256
`8d9eb1ec29b5e9a28e940e9a898cef20dcdf8246a57820e7ceb328ff8378e265`.
All eight accepted descriptors/aliases remain exact; 44 reviewed endpoints are
added. Four redirects and one 404 remain excluded. Cadence and permissions remain
unchanged, with 52 attempts maximum and unchanged request/batch/byte caps.

## Verified baseline and replay

[Control snapshot](../research/appimage-batch-20261102/rollout-controls.json):
remote source/daily pin `cc2ba588d5446df5a9fdb5366ad689e672986a2a`, default main-marek,
only collector/dispatcher active, all five unfinished statuses empty. Exact current
catalog parent is `9f4e356ec2d50260196748374b00efdda397d7f7`, source cc2ba588d,
run 41435841172 attempt 1, generated November 2 at 11:19:14.848066 UTC.
Its Git tree, body/index/lookup integrity and original eight-source manifest were
verified; this is not a new full run/artifact acceptance claim.

[Current-parent replay](../research/appimage-batch-20261102/rollout-checks.json)
preserves eight exact conditional requests and 44 initially unconditional ones;
full artifact reconstruction/ZIP roundtrip pass. First-new 304, timeout and missing
result refuse. The prior snapshot is retained as a hash-bound ZIP. Replay events
are explicitly synthetic for old sources and use real retained new bodies.
Recheck live controls and exact parent immediately before execution; drift requires
updating the review. No synthetic daily dispatch or automatic second run.

## Single rollout authorization to request

1. Push the exact enrollment candidate to origin/main-marek as a fast-forward.
   Keep the old daily pin initially; its equality guard prevents scheduled expansion.
2. Recheck source/parent/isolation; submit exactly one manual run:

   ```sh
   gh workflow run catalog-collector.yml --repo mareklangiewicz/AM \
     --ref main-marek -f approved_revision=EXACT_ENROLLMENT_SHA \
     -f manifest_sha256=8d9eb1ec29b5e9a28e940e9a898cef20dcdf8246a57820e7ceb328ff8378e265 \
     -f previous_publication=9f4e356ec2d50260196748374b00efdda397d7f7
   ```

   Inspect an ambiguous dispatch response; never submit it again blindly.
3. Require exactly 52 successful once-only attempts and full publication acceptance:
   source/context/manifest, artifact digests and recomputation, exact Git parent/tree,
   preserved aliases, actual original selectors for all 107 recipes, and both pinned
   readers. Keep all time/byte/history caps. Retain actual timing/resource evidence;
   synthetic replay does not prove future 52-request timing or live 304 behavior.
4. Only after acceptance, fast-forward source to the exact merged main-marek
   candidate and set CATALOG_SCHEDULE_REVISION to that same SHA. Verify equality,
   isolation and the accepted catalog tip. This delivers recipe source; it does not
   synchronize hosts, migrate installed updaters or execute/download app binaries.

## Pre-delivery rollback

`prep/appimage-52-rollback` is a prepared source commit whose sole parent is the
enrollment candidate and whose entire tree equals accepted source cc2ba588d.
It is not based on the migration commit, which already contains the new recipes.
Use this bounded rollback only before the post-acceptance recipe publication,
with no intervening source changes; otherwise require a new concrete review.

If no new catalog publication exists, fast-forward source to the rollback commit
and repin daily operation to that rollback SHA. If a 52-source publication exists
but fails acceptance, first restore the exact prior eight-source catalog tree
as a new commit whose sole parent is that new publication. Verify old tree/body
hashes and unchanged observation times, then fast-forward the catalog ref with
an exact-parent guard. Only then push/repin the prepared source rollback. The old
collector cap is eight and cannot consume a 52-source prior; retaining that prior
would block subsequent daily operation. Do not rewrite history or advance ages.

The concrete catalog rollback commit depends on the actual future publication SHA;
it must be constructed/verified from that run's exact parent and saved prior before
execution. Source/catalog drift or uncertain publication state stops rollback for
review. No second manual collection belongs to rollback authorization.
