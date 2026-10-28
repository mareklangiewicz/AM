# Inventory recipe families and plan substantial migration batches

Type: task
Status: resolved
Triage: ready-for-agent
Blocked by: 42

## Scope

Inventory existing recipes locally and group actual lifecycle/metadata patterns:
common AppImages, archive executables, and custom installation needs. Identify
which exact endpoints already have retained observations and which would need
separate reviewed enrollment. Do not execute recipes, collect releases to test
filters or silently map different query/pagination aliases together.

Use ticket 42's measured interface/code savings to choose practical next batches.
Record exceptions, expected duplicated code deletion and remaining callers of
proxy rewriting, quota/token patching and alternate update paths. Delete support
only when the actual caller audit proves it unused; do not claim whole-subsystem
removal after migrating a few apps. Do not create speculative format adapters or
large hook/configuration schemes before real callers need them.

Deliver a scoped inventory and next actionable migration tickets, distinguishing
repository implementation from installed rollout and any new collection. This is
how broader coverage and total simplification progress after the two-app proof.

## Answer

Delivered a reproducible [10,716-recipe inventory](../research/recipe-family-inventory.md)
with [machine evidence](../research/recipe-family-inventory.json),
[verification](../research/recipe-inventory-checks.json) and an independent
[exceptions/remaining-callers audit](../research/recipe-exceptions-and-callers.md).
Four architecture directories partition into actual AppImage/extraction,
unpack, plain-executable and custom source-marker groups, with 397 normalized
frames and explicit lexical limitations. Exact manifest aliases cover three
already migrated recipes plus three remaining Neovim AppImages; nightly WezTerm
is partial-only, and stable WezTerm's plain releases query is not enrolled.

Opened concrete continuation tickets: [46](46-migrate-remaining-neovim-appimages.md)
for the three existing-source Neovim variants;
[47](47-enroll-scoped-migration-sources.md) for separate bounded, reviewed enrollment;
[48](48-shared-executable-am-utils-batch.md) for 356 actual plain-executable recipes
behind one endpoint; and [49](49-migrate-common-appimage-batch.md) for 124 AppImages
behind 50 exact endpoints. Full path sets and current source sizes are retained.
Expected recipe deletions (168; 10,324–11,748 before new runtime; 7,464 respectively)
are projections, not implemented savings or installed delivery claims.

Current six-source/body/time/tree guards preclude simply activating all proposed
sources; ticket 47 starts with the high-yield single endpoint and requires measured
capacity and explicit approval before new live operations. No speculative format
implementation was added. Global token/quota/proxy-repair and alternate-updater
support still has real callers; only displaced per-recipe code can be removed.

Inventory repeats byte-identically, agrees with the independent prior AWK lexer
on all 20,928 x86_64/aarch64 code tokens, and reconciles partition/path/size/token
references and disjoint batch membership. Python compilation and diff checks pass.
No recipes/filters, network, installed state, runtime modules or workflows changed.
No source push. Ticket 46 is the next implementation frontier; timed 37/41 remain.
