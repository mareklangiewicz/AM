# Migrate SQLite Browser recipe to the shared catalog reader

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Marek requested faster progress and authorized the next repository implementation
step. SQLite Browser already has its exact releases?per_page=100 alias enrolled;
move the x86_64 recipe and generated updater to the existing shared shell reader.
Keep existing selection filter and original binary URLs. Reuse Obsidian's preflight,
source delivery, retry and checksum-repair behavior; remove this recipe's alternate
updater bypass. Verify against retained bytes with temporary app roots and stubbed
app/network operations. No new enrollment/collection, publication, source push,
installed migration or host app execution. Ticket 37 awaits its future expiry,
so independent implementation can proceed while the pilot remains pinned.

## Answer

Migrated x86_64 SQLite Browser installer and generated updater to existing shared
catalog reader/manager routing. Exact enrolled alias and both original selection
pipelines preserved byte for byte. Retained data selects original GitHub
DB.Browser.for.SQLite-v3.13.1-x86.64-v2.AppImage. Removed alternate updater bypass;
preflight now precedes app mutation, source handoff persists across privilege
clearing/standalone execution, interrupted downloads retry, checksum failure
triggers repair and notification failures are nonfatal. +19 net recipe lines;
no shared manager/reader runtime changes. No general proxy subsystem deletion
because unmigrated callers remain.

Validation: full **116-test suite passed** in 52.062s with the initial five new
SQLite tests. Added real install-dispatch/source-persistence coverage afterward
and parameterized the existing fixture without changing its defaults; all **six
current SQLite integration tests passed** in 6.478s. Recipe sh syntax, warning-level
ShellCheck, exact original-filter comparison and diff checks pass. Tests use
retained response bytes, temporary roots and stub app/network operations only.
[Current behavior and limits](../design/shell-consumer.md#sqlite-browser-migration-ticket-38).

No fresh collection, workflow change, host install/update or source push. Committed
locally so main-marek remains at the scheduler's approved activation revision.
Ticket 37's elapsed-time shutdown/assessment continues independently.
