# Direct v3 myxps cutover

Prepared November 9, 2026. **No push, remote publication/deployment, workflow
activation or installed-host write has been performed.** This is the concrete
package for final authorization. Marek's direct-v3 instruction supersedes the
earlier dual-output/date/waiting and extra rollback requirements. Only myxps is
affected; there are no external consumers. Do not touch mylenovo, mypi or yadm.

## Exact prepared state

| Item | Identity |
| --- | --- |
| Pipeline code | `8b8d578036037be551c950c3c9d6f28f29724aab` |
| Installed runtime/recipes and seed schema/source | `5429e09d97486cbdf9681f329bee7ed850cdd250` |
| Observed remote main parent | `03582e8e44c42e11bbd5992bc23646532778cb69` |
| Frozen historical v2 ref | `release-catalog` at `f98e2285e9348541cd00df74eb9ab570aa96b11e` |
| Prepared initial v3 commit | `e481f033692f589c7230fd655e66a3a180e2e01a` |
| Expected initial v3/status refs | both absent |
| Local package root | `/home/marek/Documents/Codex/am-myxps-v3-cutover-20261109` |

The runtime pin is an ancestor of the pipeline pin; its client/module/recipe and
schema bytes are identical. The later pipeline change restricts the source cap
to the existing 500-source enrollment. The final package commit is a documentation
descendant of the pipeline pin; before pushing, verify no implementation files
differ from that pin. Dispatch on `main-marek` only after verifying its exact
reviewed tip. GitHub's repository default branch is `main-marek`.

[Remote before-state](myxps-remote-before-15.json) records read-only API results.
`catalog.yml` and `catalog-pages.yml` are active; the prototype workflow is already
disabled manually. V3/browser activation variables are absent. The schedule pin
still names the old revision. These are observations, not authority to act; re-read
refs/settings and check for queued/running old collection jobs immediately before
the authorized cutover. Wait for any old writer to finish before freezing v2;
do not automatically cancel jobs or merge conflicting publication.

## What is ready

- All **529** maintained YAML recipe declarations use format 3: 57 complete
  declarations and 472 transitional selectors. The policies and package layouts
  are preserved. The shell wrapper uses `release-catalog-v3`, pinned descriptor /
  map / readable source paths and native compact-fact expansion. Manager module
  sync retains the v3 parser, reader and tables. No Python/jq/Git runtime is added
  to installed clients.
- The sole active CLI/Action/workflow path reads a v3 parent, emits only a v3
  artifact, independently validates it, writes v3 and attempts final status.
  V2 artifacts are rejected. There is no v2 parent, output, publication fallback
  or implicit legacy production command. The old branch and its snapshots stay
  untouched. Status's retained `compatibility_publication` field is always
  `not_attempted`, without a compatibility writer.
- [The prepared seed](myxps-seed-15.json) imports valid retained observations from
  the exact published v2 snapshot once, without collecting or producing v2.
  It contains **508 app identities / 499 sources / 1,000 documents / 31,705,806
  YAML bytes**. Full maintained domain validation passed; local publication used
  6,298,358 object bytes against a 268,435,456-byte staging guard. The seed is a
  new local root, not an activated ref or a fresh observation. Its actual Git
  commit is the v3 commit above; `seed/review.json`'s content identity is not a
  Git commit. The commit object/tree identity are recorded in the receipt.
- Source **1245849062 (`agent-console`)** still has tied conflicting IDs for one
  tag. It is refused rather than arbitrarily selected. It remains in the unchanged
  500-source enrollment and is retried/reported by normal collection. The seed
  is explicitly partial; this is not an exclusion or a 500-source conversion pass.
  It is not one of myxps's 21 installed recipe dependencies.
- [Host manifest](myxps-host-manifest-15.json): **21 installed recipes, 50 file
  replacements/creations**: `APP-MANAGER`, seven runtime/manager modules, and each
  app's `recipe.am` plus `.am-installer/<app>` source snapshot. The existing 21
  managed updater files remain byte-identical and are hash-guarded. No app
  binary, version, download URL, launcher, config or application data is replaced.
  Staged before/after bytes and the simple delivery script are under `host/` in
  the local package. This is exclusive manual metadata delivery, not a transaction
  or an automatic rollback system. Its script SHA-256 is
  `f00b76954f5d2737d80795a20260fd689cb28cbcd4cb6d334d5de75cba8912b9`.
- [Pages manifest](myxps-pages-manifest-15.json) records the ten allowlisted
  live-channel browser files under local `pages/`. Website code is unchanged by
  this consumer migration; reuse the completed browser evidence. Main-owned
  deployment is explicit; automatic review-branch deployment is removed, and the
  disabled prototype must remain disabled.

The local package is required for the prepared seed/host payload. The committed
receipts are portable evidence, not a claim that those local files exist elsewhere.

## Focused verification

The 32 contract/publication tests passed together, covering schemas, exact IDs,
URL reconstruction, malformed-suffix/no-output refusal, schema binding, exact
parents, frozen old refs and independent status. The additional native-only
created-time/no-publication-time collection case passed in a focused rerun.
Three final publication cases passed after tightening the 500-source defaults.

The 11 manager integration cases passed across the initial run and two corrected
focused reruns. Those fixture corrections account for v3's additional descriptor
fetch and clock check. They cover install, standalone updater, same-pin batches,
freshness consent, transport failure, source override and real module sync without
Git/Python/jq on clients. Four metadata-refresh and three declaration tests passed;
the metadata tests explicitly migrate a v2 installed declaration to v3. Three
archive/toolset/failure cases passed, as did the transitional executable lifecycle
and AppImage inventory cases. The shared-source fixture was corrected to convert
each numeric source once instead of once per app alias; the affected two cases
were rerun successfully. These are disposable/inert tests, not installed writes.

[Native selection parity](native-v3-selections-14.json) exercises the real v3 shell
`asset_facts` projection: all 57 declaration selections across 55 saved sources
match the maintained v2 baseline. [Exact seed selections](myxps-seed-selections-15.json)
check all 21 installed recipes, including each toolset member, against the actual
prepared seed. Both use original source completion clocks; neither establishes
current freshness. Verify fresh selections after live collection, before delivery.

Workflow YAML and every run block passed syntax checks. Installed-before and
staged-after hashes passed, as did shell syntax for all 47 staged shell files;
the remaining three files are awk tables/parser/policy exercised by the reader
and policy checks. No expanded dual-output test, unrelated browser suite or new
rollback qualification was run. Larger v3 annual capacity remains deferred.

## Final authorized operations, in order

1. **Freeze old production and push reviewed source.** Re-read the exact main/v2
   refs and absent v3/status refs. Disable `catalog.yml` while the old source is
   still deployed; wait for old active/queued writes to finish and confirm the
   v2 ref is still the recorded pin. Push the reviewed local `main-marek` tip by
   ordinary fast-forward only. A changed remote parent stops the operation for
   reconciliation; do not force-update main or the historical catalog.

   ```sh
   gh workflow disable catalog.yml -R mareklangiewicz/AM
   git push origin main-marek:main-marek
   ```

2. **Publish the reviewed initial v3 seed, requiring an absent target.** Recheck
   that the local commit/tree matches the receipt and fully validate the seed if
   its bytes or validator changed. This is one new ref creation, with the empty
   expected-parent lease enforcing absence; it is not permission to rewind a ref.
   Leave `release-catalog` frozen at its recorded historical pin.

   ```sh
   git -C /home/marek/Documents/Codex/am-myxps-v3-cutover-20261109/v3-seed.git \
     push --force-with-lease=refs/heads/release-catalog-v3: \
     git@github.com:mareklangiewicz/AM.git \
     e481f033692f589c7230fd655e66a3a180e2e01a:refs/heads/release-catalog-v3
   ```

3. **Run one current-scope v3 collection/publication and read it back.** Enable
   `CATALOG_V3_ENABLED=true`, re-enable the catalog workflow and manually dispatch
   the exact reviewed main tip. Keep the schedule revision old for this first
   verification. The prepared source's schedule gate requires an exact revision
   match, so enabling v3 does not yet resume cron. This authorizes at most 500
   enrolled sources, within 750 requests, the live primary reserve, 512 MiB body
   charge and 900-second acquisition allowance. It writes only v3/status. Read
   back their confirmed pins, truthful source failures/counts and publication
   outcomes; verify v2 stayed frozen. `agent-console` may still fail without
   invalidating healthy-source publication; do not call that full coverage.

   ```sh
   gh variable set CATALOG_V3_ENABLED --body true -R mareklangiewicz/AM
   gh workflow enable catalog.yml -R mareklangiewicz/AM
   gh workflow run catalog.yml --ref main-marek -R mareklangiewicz/AM
   ```

4. **Verify myxps's 21 fresh selections, then deliver exactly the staged files.**
   Use the staged native wrapper with the confirmed catalog commit and existing
   recipe identities/tool members, without executing installers or updaters.
   Validate their expected numeric sources and ordinary 48-hour freshness; no
   stale waiver is implied. Missing/stale/refused installed selections stop host
   delivery. During an exclusive AM maintenance window, verify the committed
   manifest/script hashes and run:

   ```sh
   sh /home/marek/Documents/Codex/am-myxps-v3-cutover-20261109/host/apply-myxps.sh
   ```

   This writes the 50 manifest paths only; all existing file/updater hashes and
   new-module absence are checked before any write. It neither downloads nor
   runs app payloads. Re-read installed hashes and perform metadata-only selection
   checks with the delivered runtime. No `am -u`, reinstall or other-host operation
   is included. Filesystem escalation for `/opt` belongs to this final authorized
   installed-host action, not preparation.

5. **Deploy the main-owned v3 browser and resume the reviewed hourly scope.**
   Set `CATALOG_BROWSER_ENABLED=true` and dispatch `catalog-pages.yml` with
   `deploy=true` on the exact reviewed main tip. Check the deployed allowlist and
   one anonymous native browser journey fetching the confirmed v3/status pins;
   reuse the unaffected completed interaction/layout checks. Keep prototype
   deployment disabled. After the live path/host selections pass, set
   `CATALOG_SCHEDULE_REVISION` to the exact reviewed remote main commit to resume
   the existing hourly, 500-source scope. Do not increase enrollment.

   ```sh
   gh variable set CATALOG_BROWSER_ENABLED --body true -R mareklangiewicz/AM
   gh workflow run catalog-pages.yml --ref main-marek -f deploy=true -R mareklangiewicz/AM
   gh variable set CATALOG_SCHEDULE_REVISION --body EXACT_REVIEWED_MAIN_TIP -R mareklangiewicz/AM
   ```

Manual recovery is sufficient: keep old Git refs/commits and inspect/correct the
specific failed stage or restore named metadata manually from reviewed history /
local before bytes. Do not introduce an automatic restore system, resume v2
publication for recovery, force-rewind refs or treat metadata recovery as binary
rollback. Any unknown write outcome must first be resolved by readback. Record
actual results here after authorization; none of the live results is claimed now.
