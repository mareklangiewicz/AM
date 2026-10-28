# Inventory recipe families and plan substantial migration batches

Type: task
Status: open
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
