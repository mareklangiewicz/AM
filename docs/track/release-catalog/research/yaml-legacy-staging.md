# Legacy layout staging and installed transition contracts

Ticket [106](../issues/106-prepare-legacy-staging-adapters.md) continues the direct
selected-asset direction in 105. This is a **maintainer-only disposable rehearsal**,
not a delivered consumer adapter or an installed migration tool.

`tools/catalog-collector/yaml_legacy_staging.py` verifies all 17 original source
hashes against 104's unchanged `legacy-updaters.json`. It consumes a trusted local
JSON map of already reviewed full selected records and already downloaded files.
It creates a new private directory containing `payload/` and `review.json`. It
never downloads, executes an asset, runs an embedded updater or writes an existing
installation. Failed validation produces no output; an I/O failure while writing
can leave disposable partial output. Existing output directories are refused.

Example invocation (paths are explicit, absolute, disposable local inputs):

```sh
python3 tools/catalog-collector/yaml_legacy_staging.py --app yt-dlp \
  --downloads /tmp/review/downloads.json --out /tmp/review/staged-yt-dlp
```

The JSON map has one app key, or EmmyLua's four tool keys, each containing `path`
and `selection`. `selection` is the full result of the existing Python selection
reference (including commit, numeric repository/release/asset IDs, observation,
publication, tag and asset URL), after validation and selected-record freshness/
consent review. This tool checks structural identity only; it does not perform
source enrollment, catalog validation, freshness acceptance or release selection.
The six-line shell protocol cannot supply Logseq's publication identity.

## Layout contracts

| Apps | Staged layout and identity |
| --- | --- |
| appimagetool, appimageupdatetool, logseq-app-og, neovide, neovide-nightly, rclone-ui, satty | Selected local file at app name; URL identity. No embedded target selection. |
| logseq-app-db-nightly | Selected file at app name; `nightly` tag required, publication-time version identity even when URL repeats. |
| yt-dlp | Selected local executable at app name; URL identity. |
| fzf, lazygit, zellij, zmx | Exact root executable entry required; retain archive supporting files. |
| btop | Require `btop/` archive root and `bin/btop`; strip only that reviewed root. |
| kitty | Require `bin/kitty` and `bin/kitten`; retain supporting tree. |
| rclone | Require one `rclone-…-linux-amd64/` root and exact rclone binary; retain supporting files. |
| emmylua | Four exact executable-only archives: emmylua_ls, emmylua_check, emmylua_doc_cli, luafmt; distinct asset IDs from the same publication/repository/release/observation/tag. Stage all before output. |

Tar and ZIP member names must be normalized relative paths, with no traversal,
backslashes, control characters, duplicates, file/directory collisions, links or
special files. Empty directory members also refuse pending explicit layout review;
nonempty directory structure is recreated from its files. Existing archive executable permission bits are retained as 0755;
other files become 0644, with required entrypoints executable. Ownership and
special permission bits are not imported. Links require a future explicit review;
this is a safe refusal, not a claim that every real kitty or other release archive
has passed. Fixed rehearsal bounds: 10,000 members per archive, 512 MiB compressed
input per asset (checked before allocation with a bounded read) and expanded payload overall. Catalog caps and manifest stay intact.

## Transition and behavior boundaries

Every report binds the original source and installed-updater hashes, but **does
not read/revalidate the current installed updater**. `contracts()` records the
requirements for a future installed transition: exact updater hash check; numeric
source/policy/runtime/publication bindings; backups of updater, optional recipe,
version, binary/tree and affected launchers; all-assets staging; durable intent,
receipts and per-path drift guards; interrupted binary-inclusive recovery; an
explicit standalone-updater replacement. The recipe-only migrator remains
ineligible for all 17. These are requirements, not an implemented transaction.

No source is enrolled here. All reports say `enrollment_ready=false` and
`apply_ready=false`. Numeric identity/list evidence and final release/channel
policy remain pending for every app. The 50-source manifest and 52-source cap
are unchanged. Zellij/zmx platform exclusions must be applied in that selection
review; stage takes the already selected artifact, not an arbitrary archive as
proof of platform eligibility. Neovide nightly retains its URL substring gate;
its final tag and same-URL refresh policy remain pending. Logseq's nightly tag
and publication identity are checked, but authenticity of that record is external.

Embedded updaters previously attempted self-update even with unchanged scraped
URLs. Direct acquisition intentionally removes that target override; this tool
never calls embedded updates. Reports require explicit reviewed refresh requests
rather than promise detection of changed bytes behind unchanged URLs. This does
not settle the eventual delivered updater's refresh/channel semantics. Preserve
those as a separate review gate. AppImageUpdate's original actual-URL patch stays
untouched, and the regression test checks its marker plus selected A versus an
inert file mentioning embedded B. This verifies staging identity only, not an
execution rehearsal of the historical embedded updater.

Local SHA256 values describe supplied download/staged bytes. They do not prove
that a file came from the URL, provide publisher authenticity, or add a catalog
binary-digest guarantee. Selection remains separate from asset acquisition. No
acquisition backend interface, consumer watchdog or reservation scheme was added.

## Validation

Offline tests cover all 17 shapes, supporting file/permission retention, four
same-release EmmyLua assets, Logseq same-URL/new-publication identity, inert
selected-A/embedded-B bytes, channels, unknown layouts, empty files, unsafe archive
members, links, duplicates, collisions, budgets, source drift, output preservation,
symlink parents and CLI/private output. Real downloaded release archives and live
installed transitions have not been tested. Production staging, module delivery,
updater activation, interrupted apply/rollback and release/capacity acceptance
remain subsequent work; the frozen package from 104 remains unchanged.


Verification at source 8164e767f (2026-11-04):

```sh
cd tools/catalog-collector
python3 -m unittest test_legacy_updater_audit test_yaml_installed_migration test_yaml_cutover_package test_yaml_legacy_staging
```

All 31 tests passed in 162.039 seconds (1 audit, 11 installed transactions,
9 cutover package, 10 new staging groups). The final 10 staging groups also passed
independently after review fixes. `git diff --check` passed. Initial parallel review
of db230336a against handoff base 2f18bd3be found two Standards-axis correctness
issues and one overlapping Spec issue; fixes in 8164e767f were independently
confirmed on both axes with zero remaining actionable findings.

[107](../issues/107-prepare-delivered-legacy-adapters.md) records the remaining
consumer/runtime, evidence/enrollment and installed transition work. No main
runtime promotion, installed or remote changes occurred.
