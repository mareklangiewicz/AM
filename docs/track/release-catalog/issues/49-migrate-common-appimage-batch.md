# Migrate the scoped common AppImage batch

Type: task
Status: claimed
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

## November 2 staged continuation

User approved progressing promptly toward migration after Brave rollout acceptance.
Only the six Brave stable/beta/nightly recipes on x86_64/aarch64 are being prepared;
the remaining 118 paths across 49 endpoints retain their enrollment dependency.
Ticket remains partial; no host delivery is included.

### Brave subset implementation

[Six-recipe implementation and costs](../design/brave-six-recipe-migration.md):
all six original selectors preserved; 462 lines / 19,164 bytes become
84 lines / 2,187 bytes, no shared-module additions. Generated updater stays
three lines. Accepted live metadata and inert mechanics are explicitly separated.
This is six completed local recipes, not resolution of all 124 paths. Remaining
118 recipes across 49 endpoints retain dependency 47. No host delivery or source
push of this migration has occurred.

### November 2 source publication

User approved publishing the completed Brave subset. Fast-forward pushed exact
`cc2ba588d5446df5a9fdb5366ad689e672986a2a` and coordinated the daily source pin.
Final read-only verification confirms source/pin equality, default main-marek,
only collector/dispatcher active, no queued/in-progress/waiting/pending/requested
runs and unchanged publication `4c6000aea8704d6585325146b85ebdf21cf0a628`.
Operational manifest/controller/workflows are unchanged by recipe publication.
No manual collection or host synchronization occurred. Six paths are published;
the remaining 118 paths across 49 endpoints remain blocked by enrollment.

## Substantial local batch — 2026-11-02

User authorized preparing compatible migrations from bounded live metadata before
separate enrollment activation. [Consolidated result](../research/appimage-batch-20261102.md)
records 107 local recipe migrations, all original selectors preserved, and total
production reduction of 7,196 lines / 334,946 bytes including supporting changes.
Together with published Brave, implementations cover 113/124 paths. Eleven paths
remain unchanged for four redirected repositories and one 404. This supersedes
the earlier preparation blocker for these 107 paths, not their activation dependency.
Status remains claimed/partial; no source push, daily repin or host delivery.

## Approved 52-source rollout accepted — 2026-11-02

[Live result and retained evidence](../research/appimage-52-live-20261102.md):
one approved run, 52 HTTP 200 responses, full artifact/Git recomputation,
214 actual original selectors and both pinned readers pass. Catalog publication
29e37bd9 accepted before publishing the 107-recipe candidate d6e742157 and
repinning daily to that exact SHA. No rollback, host sync or installed-updater
migration. Status remains claimed/partial for the eleven legacy paths excluded
by four redirected identities and one 404; their exception handling needs separate
scope. Prior pending-approval and unpublished statements above are historical.
