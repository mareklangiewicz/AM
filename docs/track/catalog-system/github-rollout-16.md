# Full GitHub v3 rollout package

## November 10 final source audit — 8,293 successful, 20 refused

Marek explicitly selected continued sequential bounded runs while coverage
increased. Twelve continued manual runs and three scheduled publications advanced
the previously reported 1,116 sources to **8,293 / 8,313**. Every enrolled source
now has successful retained data or a recorded refusal in the final run; no
unattempted source remains. The [final source-by-source audit](github-coverage-final-audit-16.json)
accounts for all **20** missing sources: **14 exact-tag conflicts, two responses
over the 16 MiB bound, and four upstream HTTP 404s**. Minimized conflict fixtures,
response sizes/hashes and sanitized transport evidence are in the
[refusal evidence](github-coverage-refusals-16.json).

[Final run 42901472181](https://github.com/mareklangiewicz/AM/actions/runs/42901472181)
published catalog `0cbe19cdc61f9f594971d830e99a0b9893a11fc9` and status
`c4bc2cd82aabc2154a9ce2c226d4f32146da89a5`. All 500 selected sources were
attempted: 479 succeeded and 21 failed. The snapshot added **317** sources and
retained all 7,976 previous sources: 7,814 byte-identical and 162 updated after
successful collection. One failed refresh, Axe-OS Multitool (HTTP 404), retained
its previous successful data and adds no missing source. All candidate hashes,
run/input bindings, published counts and retained source identities passed
verification. The [continuation ledger](github-coverage-continuation-16.json)
links the exact results, summaries, statistics and compressed acquisition reports.

Final collection used 500 HTTP attempts and 286,516,589 charged response bytes.
The existing 500-selected / 750-request / 512 MiB / 900-second acquisition bounds
were retained; acquisition took 378.296 seconds. Conflict and size rules were
preserved. Acquisition dispatch ended after the final audit established that
every remaining gap had failed in this run. No zero-growth replay was dispatched.
Further progress for these sources requires corrected upstream data or an
explicitly reviewed scope/policy change; usable payload coverage and the older
capacity targets remain unqualified. Ticket 16 stays claimed.

An intervening scheduled publication, run 42869466420, advanced 7,011 to 7,494
sources before manual run 42870336181 read its actual parent. That manual run
then published 7,976 sources successfully. Its later **local** artifact extraction
failed on disk quota; publication had succeeded. Recovery extracted only the
report from a compressed archive on physical disk and checked every candidate
hash against the published Git tree. Further evidence retrieval used this method.
The earlier temporary automatic-approval usage-limit failure was resolved before
the live recovery checks; neither event changed catalog facts or runtime files.

Remote source and hourly schedule remain pinned to
`47211b286188113e6111033e9f17f8a7315d16bd`; schema/runtime authority remains
`040614f86cbbf31fc19596c8d32225c82de77acf`. Runtime redelivery, installed-app
changes and yadm operations were unnecessary. The new evidence commits are local
and require Marek's push approval. A documentation push must also repin the
schedule to its new tip so the existing schedule gate continues to run.

## November 10 continuation — initial checkpoint

Marek requested continuation. Scheduled runs 42740899290 and 42794542725 had
already raised successful source coverage from 1,116 to 1,613 and then 2,109.
The first continued manual run, 42839585692, published successfully and added 495
sources, reaching **2,604 / 8,313**, with **5,709** lacking successful data.
Its 500 selected sources were all attempted; five failed. Every previous source
document remained unchanged. The [continuation ledger](github-coverage-continuation-16.json)
links each further run's exact published counts, summary, statistics and candidate
hash/retention verification. Sequential acquisition retains the existing bounds
and pins and stops on failed publication, changed authority or no added sources.
No further source push, schema/runtime change or installed delivery is involved.

The recurring refusals are not all collector defects. Current public metadata
reproduces Nuclear's exact-tag conflict (`player@1.23.3`, release IDs 298492443 and
298492446) and Pixelorama's (`v1.1.10`, 315135795 and 315135796). Each two-release
fixture fails `same_tag_conflict`; either release alone passes. ADR 0002 requires
refusal rather than choosing an ID. VSCodium's captured response is 25,105,372
bytes, exceeding the unchanged 16 MiB response bound; its unbounded offline
projection passes, which does not authorize bypassing acquisition limits. Wekan's
oversized-response refusal was already established. Evalit failed HTTP 404 in the
first continued run. [Portable refusal evidence](github-coverage-refusals-16.json)
contains minimized fixtures, public response hashes/sizes and sanitized run evidence.
These captures explain current upstream data, not an exact replay of earlier
network bytes. No code fix is indicated by these reproductions; accepted conflict
and resource-bound behavior remains intact. Ticket 16 stays claimed.

## Approved rotation correction — November 9, 23:16 UTC

Marek approved pushing the prepared correction, repinning the schedule and one
bounded acquisition. Remote main, schedule, schema and published parents matched
the handoff before the ordinary fast-forward push. Source and schedule now pin
`47211b286188113e6111033e9f17f8a7315d16bd`; schema/runtime remains
`040614f86cbbf31fc19596c8d32225c82de77acf`.
[Run 42717775918](https://github.com/mareklangiewicz/AM/actions/runs/42717775918)
succeeded and published catalog `fae6affff829614525d8203a4fa65e4c5ae44835`
and status `3fc848289501fc00e4797b937fc467189007be9e`.

All 500 selected sources were attempted: **498 successful, two failed, zero
selected sources deferred**. Wekan remained refused as `source_validation`, while
BORIS immediately after it succeeded; Nuclear also failed `source_validation`.
The source failure no longer stops later acquisition. The snapshot gained 498
source documents, retaining the previous 618 unchanged, for **1,116 / 8,313**
enrolled sources with successful data; **7,197** still have none. The exact
published statistics report 1,115 under 24 hours old and one at least 48 hours old.
Collection remains partial; this proves progress beyond the blocker, not complete
GitHub coverage or usable payload coverage for every recipe.

This run used 502 HTTP requests and 373,699,196 charged response bytes against
the unchanged 750-request / 512 MiB / 900-second acquisition limits. The published
summary reports `source_validation`; the raw acquisition metric's `request_limit`
label does not mean that the 750-request allowance was exhausted. Final published
target counts own successful/failed coverage, including validation after receipt.
[Result and verification](github-rollout-rotation-success-16.json),
[exact published summary](github-rollout-rotation-summary-16.yaml), and
[compressed acquisition report](github-rollout-rotation-acquisition-16.json.gz)
preserve the evidence, including exact candidate/published hash matching.

Runtime redelivery was unnecessary and was not performed. Ticket 16 remains
claimed. The existing hourly schedule retains the approved source pin; inspect
later actual publications for continued coverage progress. No additional manual
run, source push, schema change, installed-app change or yadm operation was made.
The prior local-correction approval boundary below is historical and is satisfied
by this approved run. Capacity targets remain unqualified.

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
