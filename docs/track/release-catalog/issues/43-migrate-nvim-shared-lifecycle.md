# Migrate nvim through the proven shared AppImage implementation

Type: task
Status: open
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
