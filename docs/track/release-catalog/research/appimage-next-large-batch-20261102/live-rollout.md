# Accepted 922-recipe rollout — November 2, 2026

Marek explicitly approved the prepared two-stage rollout with “go ahead”.
Remote source, catalog parent, daily pin and workflow isolation matched the review.
Enrollment source `9f114d25fff27b0bd2f0ecf561871ca267a9f29f` was pushed first.
The sharded workflow registered; the legacy collector was disabled.

Exactly one GitHub run [41471816957](https://github.com/mareklangiewicz/AM/actions/runs/41471816957)
completed successfully: plan, all 14 shards and atomic publisher. The initial
sandbox dispatch command failed before connecting; GitHub listed no run before
the network-enabled dispatch succeeded. No workflow rerun or extra collection.

Independent read-only acceptance passed against actual same-run ZIPs and Git:
exact artifact digests/provenance, full shard recomputation, exact parent/tree/blob
verification, all 1,844 original selectors for 922 recipes, and pinned shell/Python
reads for two architecture representatives. Root tree: 261,758,957 bytes.
Accepted catalog: `6f21b8c1d2bf271f570a0177bc1068bb9ca43d0a`.
Parent: `29e37bd9207ae9557e8f57afa010699c649d4cde`.

Only after acceptance, recipe source `f6b3c349cf4d590d0591b9c601bb8ac01c4fc629`
was published and CATALOG_SCHEDULE_REVISION set to the same SHA. Operational files
were verified identical between enrollment and recipe stages. Final checks confirm
source/pin equality, accepted catalog, exactly catalog-shards.yml and
catalog-schedule.yml active, and no unfinished run among the latest 100.

[Acceptance](live-acceptance.json), [final controls](live-final-controls.json), and
[original artifacts/logs/metadata/tree evidence](live-evidence-41471816957.tar.gz)
are retained. Archive SHA256: `b0984b9547de3f26ee1b6732f806ef2efcee58a2b846ef336bd75edbf67c2401`.
The archive excludes the temporary bare Git copy; exact tree listing and all
original shard/publication ZIPs needed for recomputation are included.

This establishes one successful live sharded rollout. Natural daily repeat,
long-term Git growth and refresh reliability remain unmeasured. The 78 exceptions
are unchanged. No host sync, installed-updater rewrite, binary download/install,
yadm pointer bump or unrelated branch publication occurred. Historical rollout
review JSON remains an unchanged pre-approval proposal.
