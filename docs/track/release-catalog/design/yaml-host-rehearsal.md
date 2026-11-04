# Sunshine and host cutover rehearsal

Ticket 104, based on consolidated ee89ef3bd. This is isolated source preparation.
Main runtime, installed applications, active workflows and remote refs remain
unchanged. No cap/policy acceptance follows from passing saved-data tests.

## Sunshine and the YAML-only enrollment manifest

Sunshine's prior identity is 438803890, from the verified large-batch manifest.
Its saved numeric-list page is release-0531 in
research/appimage-next-large-batch-20261102/evidence.tar.gz: 30 releases/651 assets,
1,535,547 bytes, SHA-256 ea360c2ecb2b4ca1b77a861ef59c8ba63b7433f96a0b83662ccaf3ba6d3f72ab.
The fixture loader verifies that body identity and original receipt time; it never
requests or fabricates another page. Selected URL agrees with the old selector
on this saved response. Three awk implementations agree with the Python reference.

The explicit policy preserves case-insensitive AppImage URL filtering and the
existing architecture exclusions. Client ordering is published_at/release-ID
and asset-name/asset-ID as in the reviewed format-2 candidate; it does not promise
upstream list order equivalence. Unknown bindings still refuse. Sunshine's source
recipe gains the two opt-in declarations. Its custom legacy selector is retained
for review and format-1 fixture use, rather than evaluating catalog data as shell.

New yaml-manifest.json deduplicates the existing 52 endpoint variants into 49
numeric list identities, keeps all their reviewed aliases/evidence, and adds
Sunshine: 50 sources / 476 bound paths / 986 excluded shared paths. It is schema
2, within the unchanged 52-source cap. YAML workflow code and inactive proposal
use this manifest. Existing staged-manifest.json and all active .github workflow
bytes are untouched. Old scoped experiments retain their original inputs/counts.
The host package can now derive replacements for all four managed clients.

## Legacy installed updater audit

legacy_updater_audit.py hashes each of the 17 inventory-bound local scripts and
checks the reviewed behavior marker before reporting. It never executes them,
changes them or grants automatic migrator eligibility. The existing recipe-only
transaction tool applies only to known generated exec-recipe updaters.

- yt-dlp is closest to a direct shared-executable candidate, but still needs
  numeric enrollment, release policy and explicit updater transition.
- fzf, lazygit, rclone, zellij and zmx need reviewed archive-entry adapters;
  rclone includes a nested ZIP and the latter tools have distinct OS filters.
- btop and kitty require retained directory layouts and supporting files;
  kitty has both kitty/kitten executables. A single app-named file is insufficient.
- EmmyLua updates four same-release archives; interruption and multi-file recovery
  require an explicit contract. Logseq DB nightly uses publication-time version
  identity, not asset URL.
- AppImage self-update cases require an explicit decision about embedded update
  targets versus selected catalog URLs. AppImageUpdate has a local patch recording
  the URL actually used by self-update. No generic takeover may remove it.
- Logseq OG needs an explicit replacement for /latest before a shared-lifecycle
  transition. Selection and installed-updater migration are distinct changes.

A reviewed reinstall is not automatically safer: it can replace launchers,
resources or local behavior. Keep these exact hashes as a future adapter boundary;
a changed script requires a new review. Full legacy migration remains open.

## Disposable end-to-end rehearsal

The test publishes valid local format-1 raw/lookup data and local format-2 YAML
from the same hash-checked saved Sunshine observation. It creates a fully bound
legacy installed recipe, generated trampoline, inert binary/version pair and
old exact source manager/modules in a temporary installation. All fake HTTP
reads come from pinned objects in the local bare Git repository.

The actual format-1 helper/updater first runs successfully. Guarded exact-source
manager/module delivery uses the transaction tool's metadata-preserving rename
primitive. The installed migrator checks the newly delivered bytes, preflights
the exact selected record, replaces the recipe and successfully runs its updater
without a binary change. An explicitly synthetic next-release fixture drives an
actual manager update dispatch/functions in the existing isolated harness with
service/configuration functions stubbed and the inert downloader; binary and version change.
Recipe rollback correctly refuses their drift. A separately retained original
binary/version pair restores those guards; recipe rollback and old manager/module
restoration then permit the actual format-1 updater/helper to execute again.

This demonstrates the required sequence and distinguishes recipe rollback from
binary recovery. It is not a production manager/module delivery command, an
atomic multi-module operation, a pair-atomic binary/version restore, a power-cut
test or a promise of binary rollback for real applications. For production,
record and guard the post-update pair, retain trusted artifacts, stop competing
updates/sync, and recover binary and version deliberately before recipe rollback.
Complete delivered-manager startup is not tested. No real host updater or app
binary is executed in this test.

## Capacity evidence and package freeze

host_capacity.py normalizes hash-checked saved list responses for the new numeric
scope, preserving original page sizes/receipt times and unchanged trial caps.
It reports missing list evidence honestly; latest singletons never become fake
list pages or complete bootstrap. Its saved partial tree is a measurement sample,
not a publishable workflow bootstrap. It measures the actual shell reader's
asset_facts projection for the largest saved document and Sunshine with mawk,
GNU awk and BusyBox, comparing complete output hashes and timing/RSS externally.
Harness address-space/CPU/elapsed limits are test controls, not a new consumer
watchdog framework or accepted production limits. Parent RSS and each measured
process's RSS are distinct, not aggregate peak memory.

Freeze the exact-source package only after tests and both review axes pass. It
must still have null live publication/selection pins and apply_ready=false.
Remaining gates include actual page-100/live capacity, policy/stale acceptance,
legacy adapters, reviewed delivery/recovery and explicit source/publication/host
cutover authorization. Keep format-1 support for the 986 remaining source paths;
four local managed replacements alone cannot retire that publication.


sunshine_growth.py separately clones saved Sunshine asset-density/string shapes
with synthetic noncolliding IDs and receipt dates until the unchanged retained
file cap refuses. It checks exact retained facts/default/schema/last-success
preservation and validates the failed-metadata document within the same cap.
This is a retention-limit test, not a claim to observe additional releases or a
reason to trim records/increase caps.
