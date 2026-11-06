# Twenty existing AppImage recipe conversions

Ticket [133](../issues/133-prepare-large-existing-recipe-batch.md), November 6, 2026.
Marek requested a big batch after the completed two-app pilot. This implements
**twenty local source conversions**, using the existing literal declaration and
shared installer. Collection enrollment remains 23 recipes / 21 repositories;
these twenty new declarations are not yet available from the production catalog.
No push, dispatch, publication, installation, installed recipe refresh, runtime
module deployment or yadm change accompanies this work.

## Scope and primary evidence

Started from unchanged whole-template instances at pinned upstream
`bbffd15c19d01ef9124fbf99b5b9c41d2661ea22`, checked against current fork bytes.
Fresh full inventory SHA-256: `cf9100c853c98f43469823509e5ea62d41fa27f30490d1e3fb327c6cefe92dc7`.
Screened 31 existing recipes: 29 passed metadata/source selection preparation,
then 20 passed payload gates. `ace-step-studio` exceeded the 400 MiB per-payload
limit; `aegis` redirected repository identity and was left for separate review.
No unmatched/custom fork recipe was overwritten. Templates and generator remain
original Git objects, with exact byte reconstruction, repeated parameter checks,
and pinned original hashes. The companion [runtime research](large-batch-runtime-review.md)
records shared behavior and differences; syntactic recognition alone is insufficient.

[Portable receipt](large-batch-evidence.json) binds complete first-page API JSON,
Git provenance, canonical numeric repository identities, selected release/asset
IDs, URL/name patterns, payload SHA-256/size, tool versions, full numeric-owner
filesystem listings, desktop/icon link chains and exact metadata bytes to the
[compact evidence archive](large-batch-evidence.tar.gz). Full payloads are kept
only in `/home/marek/Documents/Codex/am-large-batch-20261106/`, without execute
permission; the archive contains static metadata and AppRun bytes as inert
evidence only. Every converted app has matching published and computed full-file
digests. A published digest is metadata integrity evidence, not an independent
publisher authenticity guarantee.

First-party observations use `https://api.github.com/repos/OWNER/REPO` and
`/releases?per_page=100`, recorded separately for each app. These are saved
observations, not claims about current availability or complete history.
Selectors replay the complete response including text fields through a closed
local curl stub, then the maintained selector consumes structured facts from
that same response. All twenty selected URLs agree. Release/asset counts,
observation timestamps and exact URLs are in the receipt and response archives.

| Recipe | Canonical repository / numeric ID | Observed selected asset |
| --- | --- | --- |
| 0x808 | `averagenative/0x808` / 1180896595 | `0x808-1.5.0-x86_64.AppImage` |
| 0xsynth | `averagenative/0xSYNTH` / 1182510445 | `0xSYNTH-1.1.0-x86_64.AppImage` |
| 3mf-katalog-manager | `Bexxs75/3mf-katalog-manager` / 1362591273 | `3MF-Katalog-Manager-0.17.2-Linux-x86_64.AppImage` |
| 5ire | `nanbingxyz/5ire` / 739667828 | `5ire-0.15.4-x86_64.AppImage` |
| 6502-emulator | `acwright/6502-EMULATOR` / 1166443294 | `ac6502-emulator-3.5.0-linux-x86_64.AppImage` |
| a0-launcher | `agent0ai/a0-launcher` / 1100653513 | `a0-launcher-1.9-linux-x64.AppImage` |
| aartiq | `Latestinssan/Aartiq` / 1289277101 | `Aartiq-0.3.8.AppImage` |
| abcarus | `topchyan/abcarus` / 1124235503 | `ABCarus-x86_64.AppImage` |
| accordserver | `DaccordProject/accordserver` / 1160442164 | `Accord_0.2.4_amd64.AppImage` |
| accshift | `klNuno/accshift` / 1140627160 | `accshift_1.0.5_amd64.AppImage` |
| ace-gui | `daisy/ace-gui` / 134057106 | `Ace.by.DAISY-1.4.6.AppImage` |
| actiona | `Jmgr/actiona` / 2405281 | `actiona-3.11.5-x86_64.AppImage` |
| ada | `black141312/ada-releases` / 1305051933 | `Ada-0.1.69.AppImage` |
| adbkit | `Drenzzz/ADBKit` / 1089623281 | `ADBKit-2.0.0-linux-x86_64-system.AppImage` |
| adelie | `lmliheng/Adelie` / 1404226270 | `adelie-desktop-linux-x86_64.AppImage` |
| adt-studio | `unicef/adt-studio` / 1153610647 | `adt-studio-0.9.0.AppImage` |
| adventshow | `AdventTools/AdventShow` / 1207343947 | `AdventShow-Linux.AppImage` |
| aeroftp | `axpdev-lab/aeroftp` / 1119622081 | `AeroFTP_4.2.6_amd64.AppImage` |
| aether | `AliSawari/aether` / 1300721529 | `Aether_0.1.0_amd64.AppImage` |
| aethersdr | `aethersdr/AetherSDR` / 1180091786 | `AetherSDR-v26.11.1-x86_64.AppImage` |

## Selection and lifecycle policy

All twenty use any release channel, publication time descending then numeric
release ID, bytewise asset name then ID, structured name-based architecture and
platform exclusions, retained releases, URL version identity, ordinary 48-hour
release-observation freshness with explicit stale acceptance, and direct full
asset acquisition. This carries forward the completed pilot direction and ADRs
0001/0002; it does not promise old response-order behavior across unseen releases.
Narrow anchored patterns retain observed product/platform/architecture spelling,
generalizing only clear dotted numeric versions. Fixed-name assets remain exact;
new naming schemes/prerelease version strings require deliberate review. Some
unqualified AppImage names do not independently prove architecture; the inspected
payloads have x86_64 ELF64 AppImage runtimes. No GUI compatibility is asserted.

`DESKTOP_STRIP_NO_SANDBOX=true` is explicit in all twenty declarations because
all original templates globally stripped that literal substring. Observed desktop
transformations match the original behavior through inert lifecycle checks. Each
has one visible logical root desktop; any nested duplicate is byte-identical or
a target of the root symlink. `.DirIcon` chains resolve internally within the
shared ten-pass bound. Quoted executable names, hidden/action launchers,
distinct additional desktops, missing Exec or absolute metadata links refuse.
Full listings retain image ownership; raw layout does not deploy the root tree.

Only recipes and the generated selection registry change. Shared runtime code
is unchanged. Existing-install ownership, additional historical desktop files,
custom commands and remover reconciliation still need a separately scoped
transition. Embedded AppImageUpdate/delta selection and numbered legacy backups
are replaced by shared direct/staged acquisition and existing failure behavior.
The generated remover owns the primary command/app tree/main desktop; inert
checks exercise that behavior, not a live migration or durable binary rollback.

## Exclusions

All following recipes remain byte-identical to their pre-batch sources:

| Recipe | Reason |
| --- | --- |
| abundio | unsafe/unsupported metadata link |
| acp-ui | unsafe/unsupported metadata link |
| acreom | missing published SHA-256 digest |
| actone-screenplay | distinct additional desktop entries need review |
| actual | missing published SHA-256 digest |
| adiman | missing/multiple Exec |
| advanced-rest-client | missing published SHA-256 digest |
| aero-sync | multiple/missing/hidden root desktops |
| aes-lacrima | distinct additional desktop entries need review |

For `abundio` and `acp-ui`, `.DirIcon` points to an absolute build-host path.
`actone-screenplay` and `aes-lacrima` have distinct additional desktop entries;
`aero-sync` has no usable single root desktop, and `adiman` lacks a usable Exec.
The three missing-digest assets are older releases. Two had already been fully
downloaded before missing-digest refusal; they were not accepted or inspected as
verified payloads. The acquisition helper was tightened to reject absent digests
before transfer; its intermediate None handling error was corrected. All
acquired files together total 3,738,516,565 bytes, below the 4 GiB batch limit;
26 digest-verified files total 3,473,447,617 bytes. Excluded raw assets are inert
local evidence, not installed applications.

## Verification

`test_large_batch.py` provides three retained offline test methods covering all
twenty recipes: exact original reconstruction and selector/identity receipts;
60 full-page selection comparisons (mawk, gawk, BusyBox awk); and actual converted
recipe lifecycle with authored inert extractors and the real saved desktop/icon
metadata. It checks install, unchanged updater, changed-URL updater, data/custom
desktop preservation, executable/icon/launcher/version bytes and remover. No
AppImage/AppRun/downloaded launcher was executed. Desktop/icon bytes are hashed
before use; executable AppRun data never enters the executable fixture.

Validation results are finalized in ticket 133. No real GUI launch, existing-app
migration, full collector/container suite or catalog capacity/publication trial
is claimed. Enrollment and operational capacity must be checked separately before
making these declarations usable through production publication.
