# Unify recipe declarations and selection independently of collection enrollment

Type: task
Status: resolved
Triage: ready-for-agent

## Direction and inspected evidence

Marek requested simplification after the completed rollout: one declaration
format and generic installer/selector for any recipe. The 21 installed apps are
the immediate validation scope, not a permanent recipe category. This ticket
records a proposed first source-only slice; it does not authorize deployment or
claim an accepted full migration design.

Inspected at 9c45a700b on November 5, 2026:

- There are 493 recipes with an exact `CATALOG_FORMAT=2` line under `programs/`.
  Only 21 have the complete, marked declaration headers read by
  `tools/catalog-collector/host_recipes.py`. For example, `aarch64/nvim` still
  declares old URL filters and `x86_64/7z` contains a `select_asset` function.
- `modules/appimage.am` already provides shared installation/update behavior
  and invokes `catalog-yaml.am` by recipe identity. Selection settings in the
  recipe are not passed to that helper; its trusted registry supplies them.
  Toolset same-publication/same-release checks live in the installer.
- `modules/catalog-yaml.am` checks policy before HTTP, resolves the app map,
  verifies repository identity and runs the maintained awk selector. Transport
  derives catalog ownership from configured AMREPO; preserve that contract.
- `host_policy_source.py` generates both declarations and `host_eligible`, then
  conditionally string-patches executable selector logic. The maintained awk
  file still has am-utils, AppImage and explicit Obsidian/Neovim branches.
  Those branches cannot all be called dead: non-host format-2 recipes exist.
- The actual scheduled workflow calls `host_catalog.py`, whose configuration
  derives collection enrollment from every row returned by `host_recipes.py`.
  `yaml_enrollment.py` is a separate older enrollment path, used by staging and
  rehearsal code; it is not the scheduled workflow entry point.
- `host_cutover.py` also consumes recipe rows and imports `managed_updater`
  from `yaml_installed_migration.py`. The shell installer writes the equivalent
  updater itself. This dependency is real; the old module is not safely deletable
  merely because its migration has finished.

## Proposed smallest common path

Keep the existing literal shell declaration header and shared installer. Make
the declaration reader accept recipe paths across supported architecture
directories without a host-only marker or hard-coded `x86_64/` identity.
Normalize identity, repository, channel, asset matching and toolset settings into
one declaration model. Validate required values and architecture policy explicitly;
do not generalize the present x86_64 exclusions to every architecture.

Compile those declarations into a data-only trusted selection registry. Keep
eligibility, ordering and freshness code maintained in source, outside generated
blocks. Both direct helper clients and installer clients continue crossing the
same recipe-identity interface. This retains pre-HTTP policy validation and avoids
a second runtime path that trusts ambient selection environment variables.

Use a separate explicit collection list of recipe identities, initially the same
21 recipes/19 repositories. The collector resolves that list through the common
declaration reader. Declaring another recipe must not enroll it automatically.
Reject unknown entries and conflicting app/repository identities. Keep existing
collection budgets and publication semantics.

Initially route the complete declarations through this generic path. Preserve
the older selector branches for the remaining format-2 recipes as an explicit
transition, with their scope inventoried. Do not rebrand those branches as the
final architecture. Replacing their policies needs reviewed declarations that
preserve their matching semantics; thousands of unused recipes are outside this
slice. Do not delete a branch merely because installed-host tests no longer use it.

## Acceptance for this proposed slice

- No host-only recipe category is needed to declare, compile or select a recipe.
  A synthetic non-enrolled recipe proves the generic interface without adding a
  real app or widening production collection.
- Generator output contains declarations only; running it twice is identical,
  and it never patches maintained executable logic or rewrites recipes.
- All 21 current recipes retain deterministic release/asset choices, repository
  checks, 48-hour freshness, exact stale-consent behavior and fresh-only toolsets.
  Same-publication/same-release and distinct-asset rules remain enforced.
- Collector configuration remains exactly 21 apps/19 repositories. A declaration
  outside the explicit collection list does not change publication inputs.
- Focused offline checks cover malformed declarations, architecture handling,
  no-HTTP refusal, configured AMREPO ownership, existing direct helper calls,
  representative older selector policies and inert manager/standalone updates.
- Document the remaining legacy policy scope and its eventual removal criterion.
  Update the current operating contract when behavior is implemented, not now.

## Deferred work and limits

Installed binding/snapshot/updater refresh is a separate maintenance slice after
the declaration seam is stable. Extract a small maintained refresh operation only
after tracing its real callers; no generic migration/rollback framework.
Dependency inventory must precede cleanup of historical collector files and tests.
This inspection did not establish which of those files can be deleted.

No implementation, architecture review, runtime tests, network fetch, live refresh,
workflow dispatch, publication, push or yadm change was performed for this ticket.
The source checkout was clean and one commit ahead of recorded origin at inspection;
the remote was not freshly fetched. Natural daily-trigger monitoring is optional
and does not block this work. The proposal preserves ADRs 0001 and 0002: clients
select releases and freshness belongs to release observations.

## Execution

Marek instructed proceeding with this source-only slice. Implementation claimed;
push and live deployment remain separate.

## Implementation result

`recipe_declarations.py` replaces the host-only reader and accepts all four
supported architecture directories. It validates required literal settings,
repository/app identities, channels and existing layout/toolset constraints.
All 21 source recipe changes are marker-only (`AM-RECIPE-DECLARATION 1`).
`recipe_policy_source.py` replaces the old generator: it emits only awk array
data inside a fixed registry seam and refuses missing/duplicate seams. It never
patches maintained logic. Architecture eligibility, repository checks and the
existing selection/freshness logic are maintained source. Direct helper calls
and installer calls still use the same trusted recipe-identity selection interface.

`collection-recipes.txt` independently lists the original 21 identities; the
scheduled collector resolves those through the common declarations and refuses
unknown/duplicate entries. Production remains 19 repositories. A synthetic,
non-enrolled recipe selects on all four architectures under awk/mawk/gawk/BusyBox
without changing collection inputs. Conflicting cross-architecture app identities
refuse. Remaining am-utils/AppImage/Neovim policies are retained and documented as
transitional, with reviewed replacement declarations as their removal criterion.

A focused AppImage test exposed an existing Sunshine legacy-body hash mismatch,
also present at starting commit 194a1ce2c. Complete declarations now use the
current declaration/lifecycle contract instead of asserting historical body hashes;
legacy recipes retain the hash checks. Historical policy evidence was not rewritten.

No installed files, binaries, collection scope, workflow, publication or yadm
pointers were changed. No push or live deployment was performed. Binding/snapshot/
updater refresh and dependency-based historical cleanup remain deferred as scoped.

## Validation / Answer

Delivered the scoped first common path above. Forty focused tests passed:
16 installed-app/cutover groups, 11 manager integrations, seven selection tests,
three AppImage registry/freshness/reassignment checks, two compiler/parser tests
and one multi-architecture/non-enrollment regression. The corrected registry check
was rerun and passed after fixing its pre-existing historical-body assumption.
The broad `test_yaml_*.py` run was interrupted during lengthy legacy AppImage
coverage; it is not a full-suite pass. Python compilation, shell syntax and
`git diff --check` pass. No independent agent review is claimed.

## Push follow-up

Marek requested push and continuation. `main-marek` was pushed from 635597fd0
through 01241d2d3. No live deployment or workflow dispatch accompanied that push.
