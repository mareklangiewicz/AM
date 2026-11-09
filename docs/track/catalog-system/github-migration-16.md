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
