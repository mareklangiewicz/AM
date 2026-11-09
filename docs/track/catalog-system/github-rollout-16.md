# Full GitHub v3 rollout package — awaiting Marek's approval

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
