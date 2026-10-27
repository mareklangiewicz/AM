# Obsidian opt-in catalog filter

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Add an explicit read-only --catalog-version mode to programs/x86_64/obsidian,
before installer setup. Use the existing pinned consumer and the existing release
list asset filter. Forward consumer pin/metadata/exact stale consent arguments.
Refusal must exit without upstream fallback or installer activity. Normal install
and generated updater behavior remain as before. Verify offline, without executing
an installer, changing installed state, dispatching workflows or publishing.

## Answer

Implemented --catalog-version before installer setup in the actual x86_64 Obsidian
script. It calls the pinned consumer for the enrolled release-list alias, captures
success before filtering, preserves the existing text selection policy and exits
without installer activity. Consumer arguments provide pin/metadata/exact stale
consent; missing consumer, refusal or empty selection fails without fallback.
Usage and full-checkout dependency are in tools/catalog-collector/README.md.

76 collector tests (72 existing plus four integration checks) and eight historical
churn tests pass; sh -n and git diff --check pass. The new checks run real
consumer.lookup against retained measured baseline bytes with injected fetch/time,
then pass its verified response through the actual shell opt-in branch using a
local Python-command shim. Both original installer/updater pipelines are extracted
as data and independently compared. Checks cover argument forwarding, failure with
partial output, empty/wrong-architecture selection and guarded installer commands.
The shim does not exercise a live network or real Python CLI subprocess end to end;
consumer CLI/transport contracts remain covered by ticket 19. Freshness in this
replay uses the recorded fixture time, not a claim about current publication age.

No installer body was executed, installed app state changed, upstream/catalog HTTP
request made, workflow dispatched, publication created or updater migrated. This
read-only query requires a full checkout; normal installer and generated updater
still use their original upstream paths. Broader updater adoption remains future
work. No push authorization was carried forward from the prior session.
