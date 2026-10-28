# Make normal batch updates work with migrated recipes

Type: task
Status: resolved
Triage: ready-for-agent
Blocked by: 42

## Scope

Remove the current explicit-single-app restriction for migrated recipes and make
normal `am -u`/explicit batches work with both catalog and remaining legacy apps.
Build on the common lifecycle interface rather than executing duplicated app
update implementations. Design visible per-app unchanged/updated/refused/failed
results and aggregate nonzero failure status; preserve legacy support still used.

Resolve/pin catalog consistently for the command and avoid unnecessary repeated
lookup transfer where a small shared implementation suffices. No token/proxy/quota
patching or app mutation before accepted metadata for migrated apps. Refusal of
one app must be visible and must not turn into an unconditional direct-API fallback.
Decide/document continuation behavior across failures before implementation.

Exercise actual manager dispatch and both app categories in temporary roots with
controlled operations, including no-argument updates, explicit/mixed batches,
nonzero status propagation, freshness/refusal and current AMREPO handoff. No host
fleet migration, app execution, new collection or schedule work is authorized by
this ticket. Ticket 43 is independent once 42 is complete; it is not a batch-work
prerequisite.

## Continuation decision (2026-10-28)

Process selected apps sequentially and continue after individual refusal/failure.
Show each installed path and unchanged/updated/refused/failed result; return nonzero
if any selected app cannot complete, including missing/locked explicit targets.
Do not roll back successful apps. Launcher-only updates retain their existing path.
Normal no-argument updates still synchronize AM after app processing, preserving
aggregate app failure. Catalog options apply only to migrated apps; unsupported
options refuse before work. A command owns a private temporary catalog session:
one source-bound publication pin and lookup, validated again by the reader for
each app, with individual freshness/consent/body checks. Failed shared acquisition
refuses later catalog apps without resolving a different publication. Legacy apps
keep their updater preparation and optional verification; migrated apps bypass
legacy token/quota edits and global temporary-directory cleanup entirely.

## Answer

Implemented [normal batch updates](../design/normal-batch-updates.md) in the actual
manager: all-app, explicit and mixed selections, sequential continued processing,
per-path unchanged/updated/refused/failed results and aggregate failure preserved
through color filtering and no-argument sync. Migrated apps share one command pin
and lookup, with independent acceptance/body checks and no legacy preprocessing
or global app cleanup. Hidden/locked exclusions and both configured roots remain
supported. Removed obsolete background execution and success-only reporting;
fixed legacy exit-status masking, normal-mode false failure and checksum status.

149 catalog tests + 8 historical probe tests, syntax, reader/runtime/recipe warning
ShellCheck, baseline comparison for manager warnings and diff checks pass. The
production delta is -61 lines / -2149 bytes across manager and shared modules;
reader installed cost grows 27 lines. New tests execute real dispatch/functions
and installed lifecycle against retained bytes with isolated controlled operations.
No host migration, live request/collection, source push or workflow change.
Tickets 37/41 retain timed operational obligations; 45 is the next coding frontier.
