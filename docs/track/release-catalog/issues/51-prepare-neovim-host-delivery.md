# Prepare Neovim host delivery behind container gates

Type: task
Status: resolved
Triage: ready-for-agent
Blocked by: 46

## Scope

Prepare an offline guarded delivery and rollback without applying it. Rehearse
legacy-to-shared delivery in disposable containers, preserving launchers,
configuration, binaries and versions on refusal/failure. Exercise standalone and
managed updates after delivery, automatic recovery and safe rollback refusal on
drift. Avoid uninstalling a working editor before catalog acceptance.

Test disposable copies of configuration/plugin code with separate XDG state and
networking disabled. Never load live user configuration on the host as a test.
Keep host-specific payloads, inventories, configuration paths/hashes, plugin lists
and diagnostic artifacts private and outside publishable Git history. Publish only
aggregate verification and generic tooling. New downloads and installed delivery
remain separate; preserve pilot closure/source-push and daily-switch constraints.

## Answer — 2026-10-28

Private delivery/rollback preparation and exact-payload rehearsal completed on
Debian and Fedora, including pre-write drift refusal, injected partial-replacement
failure/recovery, delivery-only rollback, subsequent manager/standalone updates,
stale/download refusal, checksum repair and refusal after later app-state drift.
Isolated configuration startup checks passed with existing binaries on both
distributions. These are bounded startup checks, not exhaustive GUI/LSP/tool testing
or compatibility of a future upstream binary. No host delivery occurred.

Added Git to both test images so plugin checks exercise Git-dependent setup.
The ordinary public fixture matrix passes 18 scenarios / 56 CLI commands.
Production runtime is unchanged from ticket 46. Host-specific scripts, payloads
and evidence remain local and ignored. Their original inclusion in unpublished
commits was removed by rewriting those commits before publication.

Timed 37/41 remain separate. Recheck private baseline guards before eventual
delivery; any future binary update needs candidate testing and a retained backup.
