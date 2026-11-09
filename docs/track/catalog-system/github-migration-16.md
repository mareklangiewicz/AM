# Full GitHub migration — local checkpoint

November 9, 2026. Marek reopened full GitHub-backed migration, prioritizing one
consistent v3 catalog over further freshness optimization. He subsequently
requested extending v3 for non-release GitHub observations too. Work remains
claimed; this checkpoint is not a complete migration or a remote rollout claim.

The initial recipe source is `90a9f01b09f8262b38710d01f7d2b7ee510af525`.
Tools are committed at `8d77a4390`; all source writes below are local. No push,
workflow dispatch, schedule repin, installed-host write or yadm operation occurred.

## Applied release-backed bulk

- One prepared enrollment: **8,607 app identities / 8,251 numeric sources**.
  Existing collection names/identities and source paths are retained. Fifty-one
  explicit aliases distinguish different repositories under one installed app
  name; installed APP names are unchanged. Seven bindings have an empty release
  probe, which is not usable release/asset coverage. A currently unavailable
  previously enrolled source retains its known identity and prior facts.
- **986** old shared wrappers become v3 declarations, preserving their literal
  positive/negative URL predicates and existing shared installation lifecycle.
- **8,770** long recipes retain their package/desktop bodies while release
  selection calls become native v3 lookups. Only the exact legacy native-update
  bypass is removed, so the catalog-selected asset controls acquisition.
- **10,285 / 10,716** recipe files now carry v3 bindings. There are **38** custom
  release-backed cases still to adapt and **49** unavailable-source recipe
  bindings without a current verifiable public identity. The other 344 files
  lack a release-source attribution; most are non-GitHub apps. JuNest, trans and
  watched require the separately authorized non-release extension. Exodus's
  incidental AUR dependency reference is not a GitHub release source for Exodus.

These are source/identity counts, not freshly collected catalog coverage.
Remote production still uses the earlier 500-source enrollment until a source
push is authorized. Expanded sources enter the public app map only when a source
document exists. The 9,000-source allowance does not increase per-run request,
transfer or elapsed budgets, or claim annual history capacity/12-hour refresh.

## Portable evidence

[Identity archive](github-migration-identities-16.tar.gz) contains the original and
attributed scans, exact enrollment/bindings and every successful checkpointed
GraphQL response/report. SHA-256:
`09cba9896fea97e61151c97873b96aec83f33e9b2706e364c07c07911ef40f5e`.

[Recipe receipt](github-migration-recipes-16.json.gz) records every converted
path/before/after hash, original selection expressions, policies, aliases,
unavailable bindings and remaining exceptions. SHA-256:
`6dd60e5511407d53301c5c368ade796e3317c07b35352cd2870d9fe9698d13d0`.
Before-images are available at the pinned source above. The long recipe policy
registry separately binds each current source hash; compilation refuses drift.

## Checks and operating boundary

Every changed long recipe passes shell syntax and the complete policy registry
compiles. Fifteen focused bulk tests include actual manager installation with an
authored inert extractor, persisted helper/source bindings, standalone updater,
stale refusal with installed-file preservation, source-variant dispatch and
unknown-source refusal. Eighteen contract tests, forty-four reconstruction tests,
eleven existing manager tests, five existing AppImage groups (including all saved
policies/installations), seven selection tests and three declaration groups pass
at the tooling checkpoint. Later contract/selector changes require affected checks.
No real app payloads were downloaded or executed for this migration.

The future push package must deliberately set `CATALOG_SCHEDULE_REVISION` to the
new published main tip, preserving the schedule gate. Re-read remote parents for
publication; do not reuse old expected heads. Keep failed-source and non-release
work explicit, rather than silently claiming complete fresh or usable coverage.

## Non-release extension checkpoint — unfinished

Marek explicitly chose “Extend v3 for non-release sources.”
[ADR 0004](../../adr/0004-include-git-reference-and-file-observations.md) records
the boundary. The new `git-sources.json` and saved public
[identity responses](git-source-identities-16/) add JuNest, trans and watched;
`host_catalog.configuration()` reports **8,610 app identities / 8,254 sources**.

WIP code adds optional `git_scope`/`git_refs`, commit-pinned file observations,
atomic shared-budget acquisition and release/Git native projections. It adds
native output/filter/list and selection-kind support, but the new selection
profiles and recipe adapters are NOT wired yet. The format documentation, browser
presentation, explicit schema-revision transition/rebinding and operational
package are unfinished. Do not deploy this checkpoint.

`test_git_observations.py` passes five tests (Python/browser/native schema parity,
scope/time refusal, pinned file/blob validation, shared request budget with no
partial acquisition, duplicate tags). `test_batch_collection.py` passes thirteen
legacy batch regressions after preserving its transport/time semantics. Native
projection/mode integration and the broader post-extension checks remain to run.
The previous broad runtime test counts above predate this WIP extension.

## Git consumers — local continuation

JuNest now selects VERSION and its archive commit through one `--git-snapshot`
read. Both installer and updater download the commit archive, so a branch move
cannot combine different versions and payloads. trans and watched obtain their
existing tag-based version checks from Git observations; their independent vendor
payload endpoints remain unchanged. These three exact recipe hashes have trusted
selection profiles in the policy registry.

Three new `test_git_consumers.py` groups exercise actual shell acquisition against
local Git publications, tag filtering/order, scalar outputs, a moving publication
ref during acquisition, stale refusal without output/download and projections
under mawk/gawk/BusyBox awk. All pass; the five Git observation groups pass too.
The multi-tag fixture exposed a native lexical comparison of position against
100; the validator now compares numerically. This remains a local checkpoint,
with custom selectors, schema transition and rollout still unfinished.

## Schema transition and Git presentation — local continuation

Collection accepts an explicit reviewed schema revision, revalidates retained
source documents and changes only their schema headers when needed. Failed or
budget-deferred acquisitions retain every fact and time. Ordinary source changes
continue to retain the previous schema pin and exact unchanged source bytes.
The workflow reads `CATALOG_SCHEMA_REVISION`, fetches that object in collection
and publication checkouts, and passes the same authority through both operations.
Candidate artifacts cannot choose that authority. Set this variable to the
reviewed contract commit as part of rollout; keep it stable until the next
contract change. No live variable was changed here.

The format documents Git scope/reference/file identities, bounds, times, atomic
acquisition and native outputs. The glossary follows ADR 0004. The browser shows
Git references, immutable commit links, exact escaped file content and separate
observation times, including a source with zero releases.

All 18 contract groups pass, including failed/deferred retained-source schema
transitions and unchanged-source reuse. Fifteen browser transport/projection
groups pass. The added browser test passes in desktop and narrow Chromium,
including script-like content escaping and layout bounds. The positive template
classification fixture now uses its original recipe revision because the live
recipe was converted by the bulk migration. Custom selectors and operational
acquisition/publication remain outstanding; no deployment occurred.

## Real Git acquisition and append tooling

[Portable Git acquisition evidence](git-acquisition-16.tar.gz) records successful
live acquisition of JuNest, trans and watched at source `49409dbb4`: seven shared
budget requests / 84,811 response bytes, all three successful. Saved API responses,
per-response times/hashes, canonical sources and native selections are included.
All three selections agree under mawk, gawk and BusyBox awk. No application
payload was downloaded or executed, and no catalog was published.

The bulk URL tool now has an explicit `--append-policies-sha256` path. It checks
the existing registry and exact before/after hashes, shell syntax and the complete
proposed merged policy compilation in a staging tree before source writes. A
changed registry, duplicate policy, ambiguous dispatch or hash drift refuses.
Six bulk URL groups pass, including actual manager integration and an append
regression verifying refusal leaves both recipe and registry unchanged.
Fifteen publication groups also pass after the schema workflow change.

## Completed recipe preparation — November 9 continuation

The local recipe inventory now has **10,392 v3 recipes**, **49 explicit
unverified-source refusals**, and **275 other recipes**. Enrollment is **8,670
app identities / 8,313 numeric sources**. These are prepared source bindings,
not newly published source coverage or proof of usable assets for every app.

All 38 originally listed custom selectors are adapted. Release-only metadata
keeps tag/URL/publication/update identities separate from download URLs; mutable
releases use observed update/asset identities where the old checks used page
text or unrelated events. Runtime source/build choices remain explicit policies
and filters; standalone multi-read adapters share one catalog session. Wine's
menu lists retained eligible choices and revalidates the selected URL's freshness
before downloading. Version-sorted selectors choose their URL first and validate
that exact winner. The old Voicevox updater's inconsistent primary segment,
WezTerm's duplicated wget and Gale's malformed substitution were corrected while
adapting their selectors.

The old attribution scan missed literal SITE-backed API reads. The follow-up
finds and converts **65 additional recipes**, with **58 newly queried public
repository identities verified**. The scanner now recognizes literal SITE
assignments, including multiple assignments on one line. LibreOffice keeps its
source/edition choice; xdg-ninja consumes an actual release source-archive fact;
aarch64 EmmyLua retains its fixed common release archive suffix. The official
portable UAD source was independently verified and enrolled with a source alias.
There are **zero remaining recipe curl/wget reads of the GitHub API**.

Cursor adds a commit-pinned manifest observation. Its current 607,223-byte file
requires a 1 MiB decoded file-content bound. Only repository-file content can
exceed the ordinary 65,536-byte line bound, within the unchanged 2 MiB document
cap and shared request/byte/time budgets. Native decoding works in small input
chunks: validation of this saved manifest took 0.166 s mawk / 0.198 s gawk /
1.401 s BusyBox awk after removing repeated scans of long operands. Chunk-boundary
escape/output and file/ordinary-line bounds are covered by seven passing Git
observation test groups.

The same **38 repository names / 49 recipe bindings** still return 404 on an
independent identity recheck. This establishes unavailable public verification,
not deletion. Their recipes now refuse explicitly before network or installation
writes, without invented IDs or a live API fallback. Their original bodies remain
at the recorded pre-migration commit. All 49 refusal scripts pass the family
check. AUR/Nix metadata for non-GitHub app sources remains outside this app-source
migration boundary, including Exodus as established at handoff.

Portable supplementary evidence:

- [Custom receipt](github-custom-recipes-16.json.gz): 38 recipe hashes/policy keys.
- [SITE receipt](github-site-recipes-16.json.gz): 65 recipe hashes and identity bindings.
- [Cursor receipt](github-cursor-recipe-16.json.gz): manifest adapter hashes.
- [SITE identity responses](github-site-identities-16.json): 58 public repository responses.
- [Identity recheck](github-identity-recheck-16.json): the unverified names and official UAD identity.
- [Cursor identity](cursor-source-identity-16.json).
- [Unverified recipe registry](../../../tools/catalog-collector/unavailable-github-recipes.json): exact old/new hashes and original source revision.

All 153 recipes changed in this continuation and their 104 quoted updater bodies
pass shell syntax. Fifteen browser checks pass after the larger-file reader
change. The broader runtime/collector validation and final rollout package are
being completed; this source checkpoint is not permission to push or publish.

## Validation follow-up

[Saved live file acquisition](git-file-acquisition-16.tar.gz) includes AnythingLLM
and Cursor responses, receipt times/hashes and an offline replay at clean source
`d75927434859a2100c161f728ad8a60bb5c2a590`. The original six-request / 1,344,696-byte
acquisition ran in the in-flight worktree; its report names that base honestly.
Both sources replay successfully without network. Release-tag and exact file
outputs agree under all three awks; the saved files are 6,759 and 607,223 bytes.

The actual shell helper also reads both saved files byte-for-byte under mawk,
gawk and BusyBox awk, with no payload download. A follow-up extends the Git
projection with each file's own time and refuses a future file observation even
when the branch observation is already in the past. Twenty focused Git/custom/
file consumer groups pass, including that temporal regression.

The broader validation exposed and fixed optional metadata decoding for ordinary
eight-column asset rows. All 23 affected bulk/declaration/policy/custom groups
then pass. The policy compilation fixture now preserves all architectures and
the complete source-bound registry. All 15 browser transport groups and all 14
desktop/narrow Chromium smoke checks pass.

## Ready for rollout approval

The [rollout package](github-rollout-16.md) is prepared. Its final contract/runtime
authority is `040614f86cbbf31fc19596c8d32225c82de77acf`; keep that schema authority
stable when the final evidence/package commit becomes the pushed schedule tip.

The affected 81-case collector/selector set is covered by the main run and passing
regression reruns. All 20 focused Git/custom/file consumer groups pass. All 29
shared manager/AppImage/AM-Utils/selection groups pass, including actual inert
installers/updaters, saved AppImage matches and the 356-policy utility registry.
Fifteen browser checks and all 14 desktop/narrow Chromium smoke checks pass.
These sets overlap; they are not a summed coverage count.

[Real transition evidence](schema-transition-evidence-16.json.gz) verifies all
499 sources / 1,000 documents (32,392,538 bytes) from exact public parent
`263ee9e67ffbc11c66edd0f502981942b7e3e87d` against the final schema authority.
Every retained source differs only in its schema header. No fact, observation or
collection time changes. Whole-parent and candidate validation pass; nothing was
published. The final pass took 197.8 seconds, not a capacity qualification for the
8,313-source enrollment.

[Installed selection comparison](installed-policy-comparison-16.json) verifies
identical old/new choices for 21 managed apps / 24 asset/tool selections against
that same exact snapshot. [Runtime delivery manifest](runtime-delivery-16.json)
records the five required shared-module before/after hashes. Exact staged bytes
are under `/home/marek/Documents/Codex/am-full-github-rollout-20261109/`; current
live before-hashes were rechecked. APP-MANAGER and appimage.am match live and need
no delivery. No installed files or yadm state were written.

The final read-only remote survey still found main/schedule at `90a9f01b09`, v3
parent `263ee9e67f`, status parent `6d63147e07`, v3 enabled and no explicit schema
variable. The workflow must resolve parents again at execution. Initial bounded
acquisition/publication, expanded successful coverage, schedule/schema variable
writes and five-module runtime delivery remain pending Marek's approval.
