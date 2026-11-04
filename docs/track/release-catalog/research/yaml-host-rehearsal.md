# Sunshine and host rehearsal — November 4, 2026

Ticket 104 continues ee89ef3bd on isolated `prep/yaml-host-rehearsal`, worktree
`/tmp/am-yaml-host-rehearsal`. Frozen source/package revision:
`d79100e5f2d358961782c2442a61044b0ac3c728`. Main runtime and live installations
remain unchanged. Source commits: 117617148 (Sunshine/audit), 1876fd399
(rehearsal/capacity harness), d79100e5f (measurements/growth and reporting).

## Source and client coverage

Sunshine adds one exact x86_64 policy/recipe bound to repository 438803890.
Its saved numeric-list page contains 30 releases/651 assets, 1,535,547 bytes,
SHA-256 ea360c2ecb2b4ca1b77a861ef59c8ba63b7433f96a0b83662ccaf3ba6d3f72ab.
Source: archived release-0531 from the accepted earlier large-batch experiment.
The loader checks status/URL/size/hash and preserves original receipt times.
Legacy and proposed URL selections agree on that page; full selection tuples
agree across Python, mawk, GNU awk and BusyBox awk. Existing URL/architecture
eligibility is preserved. Published-time/ID ordering remains an explicit proposal,
not a guarantee to reproduce upstream release/asset response order.

New candidate-only `docs/track/release-catalog/design/yaml-manifest.json`
deduplicates old endpoint variants and adds Sunshine: **50 sources, 256 app names,
476 format-2 recipe paths**. Another **986 shared source paths remain format 1**.
The unchanged 52-source ceiling, all trial policy limits, format-1 staged manifest
and active workflow files are preserved. Only YAML workflow code/inactive proposal
select the new manifest. Old experiments retain their original scoped inputs.

All four inventoried managed catalog clients now have deterministic bound source
replacements: Obsidian, Neovim, Neovim nightly and Sunshine. No installed recipe
has been changed. The 17 legacy updaters remain ineligible for recipe-only apply.

## Exact legacy behavior audit

[Audit](yaml-host-rehearsal-20261104/legacy-updaters.json) records all 17 installed
script hashes, current source hashes, adapter requirements and reviewed behavior.
The audit reads known scripts only, refuses hash/scope drift and executes none.

- Closest direct shared-executable candidate: yt-dlp (still missing its explicit
  numeric enrollment/policy and installed-updater transition).
- Archive entry adapters: fzf, lazygit, rclone, zellij and zmx; preserve nested
  layouts and the different architecture/OS exclusions.
- Directory-layout adapters: btop and kitty, including bin/kitty, bin/kitten and
  supporting files. An app-named root file is not their binary inventory.
- EmmyLua: four same-release archives/tools, with deliberate interrupted-set
  recovery. Logseq DB nightly: publication-time version identity/refresh.
- Embedded AppImage self-updates: appimagetool, AppImageUpdate, Neovide stable/
  nightly, rclone-ui and Satty. The AppImageUpdate updater includes Marek's patch
  recording the URL actually used; do not silently remove it in an adapter.
- Logseq OG: a direct shared-AppImage candidate only after explicit /latest
  replacement and numeric/list evidence.

The user was asked for a preference between exact selected-asset direct downloads
and preserving embedded self-updates with mismatch refusal. No response has been
assumed and no existing updater behavior has been changed.

## End-to-end disposable rehearsal

`test_yaml_host_rehearsal` builds real local format-1 index/raw/lookup and format-2
YAML publications from the same saved Sunshine observation. It executes actual
format-1 helper/updater before migration; guarded exact-source manager/modules
are delivered by same-filesystem metadata-preserving renames inside a temporary
root. The installed transaction tool verifies/preflights/replaces the bound recipe.
The new updater succeeds without a binary change at the same selected URL.

An explicitly synthetic next-release fixture then drives the actual manager
update dispatch/functions in the existing isolated harness (service/configuration
functions stubbed), using the inert downloader. Binary and version really change
in that disposable root. Recipe rollback refuses their hash drift. A separately
retained original binary/version pair restores the original guards; recipe,
manager and modules are restored, and actual restored format-1 updater/helper
execution succeeds. Original binary/version bytes and metadata are checked.

This is not complete delivered-manager startup acceptance, a production module
installer, atomic multi-module or binary/version pair restoration, real-app binary
rollback or power-loss evidence. No real host updater/binary was run. The test
shows the needed sequence and separate recovery obligation, rather than extending
the recipe migrator's rollback promise.

The first rehearsal fixture was refused by storage.apply before updater execution
because saved descriptor metadata included an audit request_id field. Mapping
only url/api_version/accept to the existing descriptor contract fixed the test;
the production storage check was unchanged. The same command then passed both
new groups in 11.145 s. This was a fixture-shape failure, not an installed failure.

## Saved capacity and retained growth

[Saved-capacity evidence](yaml-host-rehearsal-20261104/capacity.json), measured
against source 117617148 with the maintained reader/normalizer:

- 48/50 enrolled sources have hash-checked saved list evidence: 45 default-page-30
  responses and three page-100 responses, preserving original observation times.
- 37,558,161 raw bytes; 1,146 releases; 19,496 assets; 253 covered app names;
  7,001,851 YAML bytes. Largest document: 1,251,982 bytes, under the unchanged
  2,097,152-byte trial per-file cap.
- PolyMC and Vivaldi have no saved list-response evidence in this set. Their
  latest singleton facts are not invented list pages or complete bootstrap.
- Largest-document asset_facts: mawk 0.73 s, GNU awk 1.32 s, BusyBox 3.62 s;
  identical full-output hashes (784,800 bytes). Sunshine: 0.14/0.23/0.60 s,
  identical 142,535-byte projection. Measured child max RSS: 7,840–8,168 KiB.
- Total local wall 67.503 s, parent max RSS 142,780 KiB. This is local processing
  and per-process memory evidence, not live API timing or aggregate peak RSS.

[Growth evidence](yaml-host-rehearsal-20261104/growth.json), source 1876fd399,
clones Sunshine's saved density/strings using explicitly synthetic noncolliding
IDs and receipt dates. Cycle 12 refuses collection_limit, preserving 330 releases,
7,161 assets, schema/default/last-success state and 2,085,551 prior YAML bytes.
The failed-metadata document validates at 2,085,584 bytes, still under the same
2 MiB cap. Local wall 10.583 s; parent max RSS 100,624 KiB. These are not observed
additional releases, future API history, capacity acceptance or grounds to trim
records. The source reader remains unchanged.

## Verification and review

At 1876fd399:

```
PYTHONPATH=tools/catalog-yaml-prototype:tools/catalog-collector python3 -m unittest test_yaml_host_rehearsal test_yaml_cutover_package test_yaml_workflow test_yaml_enrollment test_legacy_updater_audit -v
PYTHONPATH=tools/catalog-yaml-prototype:tools/catalog-collector python3 -m unittest test_yaml_appimages -v
```

26 tests pass in 73.474 s and five AppImage groups pass in 457.186 s: **31 distinct
test groups**, including all **115 inert AppImage manager installs/generated
updaters**, prior scope enrollment preservation, final 50-source enrollment and
new Sunshine transition/recovery behavior. Shell syntax, Python compilation and
whitespace pass. ShellCheck passes with existing SC1091/SC2034 exclusions for
external shared declarations; the initial unfiltered command reported SC1091.

Code-review's independent parallel Standards and Spec axes compared against
fixed ee89ef3bd, including d79100e5f follow-up. Zero actionable findings on each.
Spec's requested reporting qualification about the extracted manager harness is
explicit above and in the candidate design. Reviewers did not duplicate heavy tests.

## Frozen updated package and next boundary

Private review package:
`/home/marek/Documents/Codex/2026-11-04/am-yaml-host-rehearsal-d79100e5f`.
Source d79100e5f2d358961782c2442a61044b0ac3c728;
legacy source 83af4473f8ba77825562acb4bac1a38c70cfaf8c.
70 payload files total 149,160,999 bytes, including all four bound replacements,
complete source/runtime, host inventory and before-images. Build rechecked the
captured installed inventory before and after; package verification passes.
Manifest SHA-256:
`b35836f25c6e55eac0ed05e17e60876de27480220b3c94a1104fd8a7656d748b`.
Publication/selected-record pins remain null and apply_ready=false. No test
fixture pin or observation is offered as live migration authority.

Remaining: explicit legacy adapter policies/transitions (especially embedded
self-update behavior, multi-asset and publication-time identities); bounded real
page-100 collection/capacity and missing list facts; operating budget/stale UI/
selection acceptance; reviewed production manager/module and binary recovery;
then separately authorized source push/publication/workflow and installed cutover.
The existing format-1 ref and its 986 source consumers cannot be retired from four
local replacement recipes alone. No live acquisition, installed writes, pushes,
publication, active workflow changes, repin, main runtime promotion or yadm pointer
work occurred in ticket 104.
