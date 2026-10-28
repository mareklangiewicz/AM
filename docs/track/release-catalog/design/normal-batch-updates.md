# Normal batch updates

Ticket [44](../issues/44-normal-batch-catalog-updates.md), baseline `1ecd69251`.

Normal `am -u`, `am -u --apps`, and explicit mixed app lists share one sequential
command implementation. Each selected installed path prints unchanged, updated,
refused or failed. Refusal/failure does not stop later apps or undo earlier
successes; any unsuccessful target makes the command nonzero, including explicit
missing, hidden, locked and read-only apps. An unchanged version with a successful
checksum repair counts as updated. Results compare the existing version record;
they do not independently establish binary authenticity or correct a legacy
updater that silently reports success. Unsupported flags refuse before app work.

No-argument updates still synchronize AM after processing apps, retaining app
failure status and reporting a failing sync through nonzero status. `--apps`,
catalog options or explicit app names suppress that synchronization. `--debug`
controls legacy diagnostic output and never reaches the catalog reader.
`--launcher` alone, with optional `--debug`, retains its separate existing path;
combining it with app selections/catalog options refuses before work.

The manager enumerates updater files without calling `_determine_args`, whose
existing general discovery can remove incomplete app directories. Hidden apps
(`remove.old`) and locked apps (no `AM-updater`) are excluded from all-app scans.
Explicit names are resolved in both configured system/AppMan roots; both paths
are processed if present. Equivalent roots and duplicate explicit targets run
once. Quoted path arrays retain spaces in root paths. No automatic global cleanup
runs before or after apps. Migrated lifecycle cleanup continues only after each
app's metadata acceptance; failed/refused apps keep their interrupted work.

The command owns one private temporary catalog session and removes it on exit or
handled interruption. The reader lazily acquires one source-bound publication
pin and lookup. Explicit `--commit` skips ref resolution. Later apps reuse those
bytes, with no second ref resolution if acquisition failed. Acquisition failure
is latched for catalog apps only; legacy apps continue. The reader refuses a
changed source/pin within the session. Each call validates lookup framing and its
selected record again, measures current freshness, checks exact stale consent,
downloads the pinned body and validates length/hash, then rechecks freshness.
No acceptance result or body is cached. The temporary directory is a trusted
manager-owned implementation detail, not a new persistent user configuration.
Standalone updaters still operate independently without a session.

The existing `--commit SHA --accept-stale SHA REQUEST HASH` tuple applies only to
its exact request/body. Consenting to one stale app never consents to another;
other stale apps visibly refuse and may be retried separately. The lifecycle
returns 3 for reader/missing-reader/selector refusal and other nonzero values for
execution failure; existing installed marked updaters may report generic failure
until their runtime/recipe has been delivered. No direct-API fallback exists.

Legacy preparation is isolated per selected app in a subshell, retaining its
working directory, downloader patch, API token/quota handling, checksum repair
and optional digest verification. Migrated apps bypass these edits/probes.
Legacy child exit status is captured before proxy cleanup or verification can
mask it; verification runs only after successful execution and a recorded
checksum failure makes the result nonzero. A successful updater explicitly
returns zero in both debug and normal modes. Its timing message says the updater
completed; the command separately determines whether its version changed.
Optional verification remains distinct from required catalog integrity and
freshness; missing optional digest evidence alone is not an update failure.

Replaced background execution and the old success-only table with per-path
results, removing their unused reporting helpers while retaining the app-list
helper used by rollback. This reduces the manager implementation rather than
maintaining a parallel legacy batch path.

## Validation and delivery

`test_batch_updates.py` executes the actual update command dispatch, output filter
and manager functions in temporary roots, the real three-line installed launchers,
saved recipes, shared lifecycle and catalog reader. External metadata/binary
transfers, clock, optional verification, online checks and manager synchronization
are controlled fixtures. Tests cover no-argument/all-app/explicit/mixed/legacy-only
commands, selected AMREPO, aliases, duplicate targets/roots, both root locations,
hidden/locked/missing targets, shared acquisition counts, acquisition failure,
stale exact consent, freshness changing between apps, body refusal before app
mutation, download/checksum failure, continued processing, sync failure and private
session removal. Reader tests additionally verify source/pin binding and repeated
body/freshness checks with cached lookup bytes. Prior recipe/install/delivery tests
remain in the full suite.

These are repository changes only. No installed fleet/helper migration, app launch,
live metadata request, collection, schedule activation or source push is performed.
Pilot closure and the authorized daily activation remain tickets 37/41; recipe
inventory and substantial migration batches remain ticket 45.

Final checks: **149 catalog tests and 8 historical probe tests pass**. Bash/POSIX
syntax and warning-level ShellCheck pass for the reader, lifecycle and all three
recipes; whole-manager ShellCheck introduces no warning classes relative to the
baseline (existing unrelated warnings remain). `git diff --check` passes.

Production source cost against `1ecd69251`, including comments/blanks:

| File | Before lines | After lines | Before bytes | After bytes |
| --- | ---: | ---: | ---: | ---: |
| Manager | 3154 | 3066 | 123448 | 120100 |
| Reader | 102 | 129 | 5238 | 6427 |
| Lifecycle | 91 | 91 | 3958 | 3968 |
| Total | 3347 | 3286 | 132644 | 130495 |

Net **61 fewer production lines / 2149 fewer bytes**. Recipes, saved recipes and
three-line launchers are unchanged; shared installed reader grows by 27 lines.
New tests/docs are excluded from production cost, not from the reviewed change.
