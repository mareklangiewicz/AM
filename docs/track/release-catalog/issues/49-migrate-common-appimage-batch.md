# Migrate the scoped common AppImage batch

Type: task
Status: open
Triage: ready-for-agent
Blocked by: 47

## Scope

Migrate the 124 recipe paths in `proposed_enrollment_batch` of
[the frozen inventory](../research/recipe-family-inventory.json) after their exact
50 endpoint contracts have accepted retained/published observations. Scope is
80 x86_64, 38 aarch64, 4 i686 and 2 armv7l paths; preserve exact per-app/channel/
architecture selectors and original URLs. The two existing no-unpack source
frames identify a substantial concrete batch; they do not prove selected assets
or runtime compatibility. Enrollment is ticket 47, not an excuse to rewrite query,
pagination or API aliases inside a recipe.

Use the existing AppImage implementation and trusted saved recipe interface.
Remove duplicated lifecycle, generated update bodies and displaced alternate
updater branches. No speculative hooks, format adapters or giant configuration
schema. If actual retained evidence proves an exception, preserve/refuse and record
it with exact scope/cost instead of silently adapting it. Do not mark an endpoint
ready just because another query or channel in the same repository works.

Compare all original install/update filters and evaluate each unchanged selector
against accepted retained bytes. Prove representative install/generated-standalone/
actual mixed-manager behavior for both source frames and every architecture;
include stale/exact consent, unavailable assets, body integrity, refusal before
app mutation, failed binary transfer/retry and checksum repair. Continue batches
with visible per-app results/aggregate failure. Separate retained observations
from labeled synthetic mechanics and do not claim host app execution.

Baseline recipe source is 10,068 lines / 436,026 bytes. At 21 lines per recipe,
7,464 recipe lines could be removed before shared implementation changes. Report
actual total production/generated/installed cost, remaining legacy callers and
any excluded paths. Complete implementation/tests/docs in substantial commits.
No installed rollout, new collection or workflow/source activation is implied.
If ticket 47 progresses in stages, only unblock the precise evidence-backed
subset; record the remainder rather than silently shrinking a claimed full batch.
