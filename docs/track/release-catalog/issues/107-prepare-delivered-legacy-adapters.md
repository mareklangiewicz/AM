# Prepare delivered legacy selection and installed updater adapters

Type: task
Status: resolved
Triage: ready-for-agent

Continue 106's disposable layout staging against 104's exact 17-updater audit and
105's direct selected-download preference. Staging is not production delivery.

Review numeric source identities and saved release-list evidence before enrolling
any source. Reuse existing evidence first; do not fabricate identities, treat a
latest singleton as list coverage, add all sources blindly or raise the unchanged
52-source cap (currently 50 sources). Keep pending/blocked sources explicit.

Implement/review consumer selection and delivered adapters in the isolated candidate,
using existing lifecycle/helpers where appropriate. Preserve archive support paths
and executable permissions; explicitly review real layout exceptions (including
links and empty directories currently refused by disposable staging). EmmyLua needs
four same-release assets with per-asset acceptance. Logseq nightly requires its
publication-time identity and repeated-URL refresh semantics. Resolve each release,
platform, channel and refresh rule explicitly; do not turn the direct acquisition
preference into acceptance of a different release rule. Preserve AppImageUpdate's
actual-URL patch as regression evidence when intentionally replacing embedded target
selection. Six-line handoff is not a digest guarantee; Logseq needs additional
reviewed publication identity. Avoid speculative acquisition backend frameworks.

Prepare durable exact-hash installed standalone-updater transition and binary/tree
recovery, with multi-path interrupted apply/rollback rehearsal and drift refusal.
Do not pass legacy updaters to the recipe-only migrator by app name. A report's
transition requirements and disposable payload are not an applied transaction.

Use code-review's parallel Standards/Spec axes for source increments. No live
installed mutation/execution, network acquisition, enrollment publication, workflow,
activation/repin, main runtime promotion, push or yadm operation is authorized by
this ticket alone. Policy/stale UI/capacity acceptance and concrete live cutover
remain separate. Do not restart 71's interview or rollout 69.

## Revised execution scope — Marek, November 2026

Marek explicitly chose the single-user reinstall strategy and said “go ahead”.
This supersedes this ticket's requirement for durable multi-path transition/
rollback machinery and its earlier operational exclusions. Implement YAML-only
catalog runtime and publication, installed-app selection/adapters, a focused
source manifest, practical layout/update smoke checks and a concrete cutover.
Save manager/app/config metadata; retain user data and launchers. Recovery is
restoring the previous manager and reinstalling apps, not a binary transaction.
Retire unsupported format-1 catalog recipes explicitly. Source pushes remain
Marek's call under the home AGENTS instructions; ask when concrete pushes are due.

Operational simplification: EmmyLua is fresh-only for all four selected assets.
Stale-consent tuples are explicitly refused for that toolset; refresh the daily
catalog instead. This supersedes the earlier per-asset stale-consent requirement
without weakening the selected-record freshness check. Existing custom executable
and desktop launchers are preserved; AM-owned links are retargeted as needed.

## Answer — live cutover completed November 5, 2026

Implemented and published source 88ca89f30222767b4bd48c8800498c6d74dcc410
(the reviewed runtime entered main at 809022416). The focused production manifest
has all 21 installed apps, backed by 19 verified numeric source identities.
Format-1 catalog runtime is retired explicitly. The old collector/shard/schedule
workflows are removed and one daily YAML publication workflow is active.

Marek explicitly approved source/catalog pushes and finishing the live migration.
The initial YAML tree 312e8d8bc9a7d800fce5a2907db66ca9806b3fad replaced format 1
as a child of 4f8d6478d93a0be8ffa9d61d2e3cd4e8a419fbf9, preserving old history.
The first real [YAML workflow](https://github.com/mareklangiewicz/AM/actions/runs/42007220573)
succeeded and published 9f6056e0b5b36adad54e7b4b9df0aaf7b6300e80. Scheduled
publication is 03:17 UTC; a natural scheduled run has not yet been observed.

All 21 real selected app payloads were downloaded, staged and checked with their
CLI version or AppImage runtime option. Archive payloads were restaged with the
final delivered adapter and matched the prepared files/permissions/links. The live
apply overlaid program files, saved old manager/modules and app metadata, and
installed all 21 YAML recipes/updaters. Original removers and desktop launchers
and all 25 executable-link targets were verified unchanged. No old remove script,
app-directory removal, home config edit or yadm pointer operation was used.

Live manager startup returns 10.6-4. A real manager update pinned to the workflow's
catalog passed for neovide-nightly, btop, kitty, emmylua, rclone, yt-dlp and
logseq-app-db-nightly: Neovide nightly downloaded/refreshed and passed its checksum
check; the other six were unchanged. Logseq's inherited generic checksum UI still
warns that its timestamp version is not a download URL; the actual selected URL
is retained in download-url. This is not an updater failure or a new digest claim.
GUI startup was not exercised by the AppImage-runtime smoke checks.

Offline coverage includes all 21 actual-manager installs/standalone updaters,
failed downloads, format-1 refusal, in-place apply/data/launcher preservation,
partial tar failure, fresh-only EmmyLua and ordinary reinstall/custom launchers.
Three existing manager integration checks also passed. Parallel review findings
were fixed and both axes confirmed zero remaining actionable findings. A final
reinstall test also caught/fixed copying recipe.am onto itself. These are scoped
checks, not a claim that all historical format-1 rollout tests still apply.

Persistent private preparation and recovery material:
/home/marek/Documents/Codex/am-yaml-cutover/.
The source worktree is source/, payloads and manifests are prepared/, and the
pre-change manager/modules/app metadata are prepared/before/. The temporary
worktree disappeared between turns; committed refs and this directory survived.
Recovery is a rerun/reinstall, with manager/metadata before-images available;
there is no atomic multi-file or binary rollback promise.

[Operating policy](../../../catalog-operating-policy.md) records supported scope,
selection/freshness behavior and recovery. Unused source recipes have not all
been converted: format-1 catalog recipes refuse and YAML recipes outside the
focused app map are not currently enrolled. That unused coverage does not block
this single-user host's completed migration.
