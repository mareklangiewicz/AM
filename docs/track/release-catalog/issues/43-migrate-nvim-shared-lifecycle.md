# Migrate nvim through the proven shared AppImage implementation

Type: task
Status: resolved
Triage: ready-for-agent
Blocked by: 42

## Scope

Use ticket 42's actual small recipe interface for x86_64 nvim. Its release-list
endpoint is already enrolled. Preserve existing stable/architecture selection and
original binary URL; share selector between install/update, keep real app-specific
adjustments explicit. Do not repeat the earlier large recipe/read-call-only step.

Verify against retained Neovim observations and isolated lifecycle integration
checks. Measure the additional duplicated code removed. No source enrollment,
fresh collection, installed migration or host app execution. Expand shared hooks
only if this third real caller demonstrates a necessary difference.

## Answer — 2026-10-28

Converted x86_64 nvim to ticket 42's actual small AppImage recipe interface.
Its existing release-list alias is already enrolled; the original stable/arch
selector appears once and is shared by install/update. Both former selector
pipelines match the remaining one exactly and select the same retained upstream
`v0.12.6/nvim-linux-x86_64.appimage` URL. No new format or hook is needed; the
shared reader/lifecycle and manager are unchanged. Removed nvim's duplicated
lifecycle/generated updater and alternate appimageupdatetool bypass.

[Third-caller interface and cost audit](../design/shared-appimage-lifecycle.md#third-caller-nvim-ticket-43):
recipe 77 to 21 lines, 3167 to 607 bytes — **56 lines / 2560 bytes removed**,
including all additional production code (none outside the recipe). Installed
shell code is 29 vs 30 lines, reusing the existing once-per-manager runtime.

Reused the real shared integration cases through a common test mixin, with nvim
and SQLite Browser supplying their actual recipe/alias/identity/expected URL.
**132 catalog tests pass**, including eight nvim cases covering actual install
module/manager execution, AppMan/system delivery, install/update/no-change,
refusal and exact stale consent, transfer failure/retry, checksum repair,
standalone source persistence after privilege environment loss and managed source
override. Selector comparison uses retained bytes and the prior committed recipe.
Shell syntax, warning-level ShellCheck on all three recipes/reader/runtime and
`git diff --check` pass. No fresh collection, source enrollment, network request,
source push, installed migration or host app execution. Tickets 37/41 retain their
independent pilot-expiry/daily-activation obligations; 44 is the next coding task.
