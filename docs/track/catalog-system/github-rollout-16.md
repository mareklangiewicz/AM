# Full GitHub v3 rollout package

## November 9 approved retry — published and runtime delivered

Marek approved the ArduLoops correction with “go ahead.” Source and schedule now
pin `5be202a7376aa9c1349046cb4180e6152602fd41`; schema/runtime authority remains
`040614f86cbbf31fc19596c8d32225c82de77acf`.
[Run 42715139284](https://github.com/mareklangiewicz/AM/actions/runs/42715139284)
succeeded, publishing catalog `6baf50c003b2de25f31107e82e3f2742adcde43b` and status
`cef10df754f736ce3d734c38f9b729a669512c17`. Exact published catalog inputs and
producer match those pins and this run. Collection was **partial**: 500 selected,
120 attempted, 119 successful, one failed, 380 selected but deferred. This used
121 HTTP requests and 90,950,036 charged response bytes; the source-response bound
stopped collection before the shared 512 MiB budget or API quota was exhausted.

The published snapshot has **618 sources**: 617 collected within 24 hours, one at
least 48 hours old, and **7,695 enrolled sources without successful data**. Neither
successful collection nor enrollment proves every recipe has a usable payload.
[Result and installed hashes](github-rollout-success-16.json), the exact
[published summary](github-rollout-success-summary-16.yaml), and the compressed
[acquisition report](github-rollout-acquisition-16.json.gz) preserve the evidence.

After confirmed publication, all five shared runtime modules were replaced on
myxps after checking every before-hash, staged after-hash and committed authority.
Final hashes/modes, native validation of the exact catalog, shell syntax and
actual AM help passed. Before-images are under
`/home/marek/Documents/Codex/am-full-github-rollout-20261109/runtime-before-42715139284/`.
The delivery receipt is committed in the result above. No app payload was
downloaded/executed, installed recipe/updater replaced, or yadm operation run.
**Delivery is complete: do not reapply the original before-hash manifest.**

### Further rotation — local correction awaiting push approval

The failed source is `wekan/wekan` (repository 16089035). A single response larger
than the 16 MiB response bound incorrectly ends the whole batch. Since a failed
new source has no catalog document, it remains first in the next rotation; an
offline two-run reproduction confirms starvation of later sources. This is a
coverage blocker despite successful publication and the enabled hourly schedule.

The local correction keeps the response bound and charged bytes, records the
oversized source as failed (`source_validation` in published status), and continues
when shared bytes remain. Exhausting shared bytes still stops acquisition. It
does not advertise Wekan as collected. Replay of all 618 published source
identities selects Wekan then BORIS; with authored 4/20-byte response/shared bounds,
the corrected collector refuses Wekan and successfully reaches BORIS. The
[published-metadata replay](github-rollout-rotation-replay-16.json) is portable;
no network or app payload is involved. All 55 affected batch, Git observation,
contract and publication tests pass, including repeated rotations and refusal
when the shared byte budget is exhausted.

After approval, re-read remote main, push the new reviewed correction tip, repin
only `CATALOG_SCHEDULE_REVISION` to that tip, and dispatch a bounded run. Keep the
schema/runtime authority above; runtime redelivery is unnecessary. Inspect the
actual new source counts and failures before claiming further expansion. Ticket
16 remains claimed; capacity targets and full source/payload coverage are still
unqualified. The successful rollout does not establish working rotation until
this further correction is published and verified.

## Initial approved attempt — historical failure

Marek approved this package with “go on.” The reviewed tip
`51c862f1ed0e1d45849e2a9e08b05100511b9273` was pushed, the schema pin was set to
`040614f86cbbf31fc19596c8d32225c82de77acf`, and the schedule pin was set to that
pushed tip. [Run 42701570728](https://github.com/mareklangiewicz/AM/actions/runs/42701570728)
failed before upstream acquisition: `retained repository identity mismatch`.
No candidate artifact or new catalog was published. The catalog remains
`263ee9e67ffbc11c66edd0f502981942b7e3e87d`; independent failure reporting advanced
status to `5c77c8f2a6a150847539690a2c360bcf0446e1ce`.
[Recorded result](github-rollout-result-16.json) and the exact
[published summary](github-rollout-failure-summary-16.yaml) preserve that outcome.

The sole mismatch is numeric repository **1369127769**: retained facts name
`alex-pokydin/ArduLoops`, while enrollment names `ArduLoops/ArduLoops`.
GitHub's numeric repository endpoint confirms the latter name with the same ID.
The local correction explicitly permits only this directional ID/name transfer;
all other mismatches still refuse. Retained names, facts and times remain intact
until successful acquisition produces a new observation. The 14 batch tests pass,
including failure preservation, wrong-ID/name rejection and reverse-transfer
rejection. Replaying the exact validated 499-source parent with one inert
response now passes the original failing collector path.

All five installed before-hashes and staged authority/after-hashes matched.
Runtime delivery remains pending successful publication. The schema/runtime
authority is unchanged. After approval of the correction push, capture the new
final tip, recheck remote main, push, repin **only the schedule revision** to that
tip, then dispatch and follow the publication/runtime checks below. The current
schedule still points to the failed source tip and will retry it on its ordinary
hourly schedule until a correction is pushed and repinned. Expanded coverage
remains unestablished; ticket 16 remains claimed.

The prepared migration binds **10,392 recipes** to v3 and enrolls **8,670 app
identities / 8,313 verified numeric sources**. **49 recipes** with unverified
public source identities now refuse explicitly before installation. These are
source changes; expanded successful acquisition and public coverage remain to
be established by the rollout. [Migration report](github-migration-16.md) owns
the implementation counts, evidence and validation.

## Reviewed inputs

- Contract/runtime authority: `040614f86cbbf31fc19596c8d32225c82de77acf`.
- Push the final reviewed local `main-marek` tip, including this package. Capture
  that exact SHA as `rollout_tip` before the push; use it for the schedule pin.
- Read-only remote survey during preparation: main and schedule pin were both
  `90a9f01b09f8262b38710d01f7d2b7ee510af525`; `CATALOG_V3_ENABLED=true`;
  `CATALOG_SCHEMA_REVISION` was absent. The observed public v3 parent was
  `263ee9e67ffbc11c66edd0f502981942b7e3e87d` and status parent was
  `6d63147e07d671957113ed4a61a36f0d5586568d`.
- [Schema transition evidence](schema-transition-evidence-16.json.gz) verifies
  the real 499-source / 1,000-document public snapshot. Retained source bytes
  change only in their schema header; all source facts and times are preserved.
  The workflow resolves current parents again when it runs.
- [Runtime manifest](runtime-delivery-16.json) binds the exact five shared files
  and their current installed before-hashes. Staged bytes are in
  `/home/marek/Documents/Codex/am-full-github-rollout-20261109/modules/`.
- [Installed selection comparison](installed-policy-comparison-16.json) records
  identical old/new selections for 21 managed apps / 24 tool or asset choices
  against the same exact public snapshot. APP-MANAGER and appimage.am already
  match live source; their delivery is unnecessary.

## Authorized sequence after approval

1. Re-read remote main and check the local tree. Push the reviewed tip to
   `origin/main-marek` using ordinary fast-forward enforcement. A changed remote
   requires review before adapting the package.
2. Set `CATALOG_SCHEMA_REVISION` to the contract/runtime authority above. The
   workflow fetches it in both shallow checkouts and passes the same revision to
   collection and publication. Retain this pin on later unrelated source changes.
3. Set `CATALOG_SCHEDULE_REVISION` to the exact newly pushed `rollout_tip`.
   The schedule gate otherwise skips new source revisions.
4. Dispatch `catalog.yml` at that reviewed main tip. It reads the actual current
   v3 parent, acquires within the existing request/byte/time/quota budgets,
   revalidates and rebinds retained sources, and publishes with exact-parent
   enforcement and independent final status reporting. Check its actual result
   and exact published catalog/status pins before claiming rollout success.
5. Continue the existing bounded acquisition rotation toward all 8,313 sources,
   recording successful, failed and pending source coverage. Enrollment and recipe
   conversion alone do not establish fresh data or usable asset selection.
6. After a successful publication, recheck every runtime before-hash and staged
   after-hash, then replace **only** these files under `/opt/am/modules/`:
   `catalog-yaml.am`, `catalog-yaml-policy.am`, `catalog-contract-reader.am`,
   `catalog-contract-parser.am`, `catalog-contract-tables.am`. Verify their final
   hashes and manager help. Application binaries, installed recipes/updaters,
   other hosts and yadm remain outside the delivery operation.

No real application payload was downloaded or executed during preparation.
The future acquisition may report upstream failures or bounds; preserve those
results explicitly. The existing defaults remain 500 selected sources, 750
requests, 512 MiB response allowance, live quota reserve and bounded elapsed
acquisition. Freshness/history capacity targets remain unqualified. Browser
source changes are included; the separate saved-data review-site deployment
retains its own scope.

## Approval boundary

The local source commits and staged runtime are complete, reviewable inputs.
Marek's home guidance requires asking before pushing. Approval of this package
covers the source push, explicit schema/schedule variable changes, initial bounded
acquisition/publication and the five-file runtime delivery described above.
