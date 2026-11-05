# Allow ordinary sync to refresh the shared installer module

Type: task
Status: resolved
Triage: ready-for-agent

Observed after 109: ordinary am -s leaves the old appimage.am installed because
_sync_modules accepts content only when it contains AMCLI. Add the missing module
marker and exercise refresh of an existing stale module through real sync code.
No live copy workaround; push/deployment remain separate.

## Answer

The shared installer lacked the AMCLI content marker required by _sync_modules;
existing copies were retained silently. Added the same marker convention used
by the YAML catalog modules. The real sync integration test now seeds a stale
appimage.am and asserts exact replacement, alongside existing catalog module
checks and standalone updater execution without Git/Python/jq client dependencies.
It fails before the fix and passes afterward (one focused test, 4.8 seconds).
Shell syntax and diff checks pass. No live copy, manager execution, push or yadm
operation was used; ordinary am -s deployment follows source publication.

Independent parallel Standards and Spec reviews: zero actionable findings.
