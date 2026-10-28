# Migrate the three remaining Neovim AppImages together

Type: task
Status: open
Triage: ready-for-agent
Blocked by: 45

## Scope

Migrate `programs/x86_64/nvim-nightly`, `programs/aarch64/nvim` and
`programs/aarch64/nvim-nightly` to the unchanged shared AppImage lifecycle and
small trusted saved recipes. Their exact `/repos/neovim/neovim/releases` alias
is already enrolled. Preserve the three original stable/nightly/architecture
selectors and upstream binary URLs, with one selector per recipe and no new hook,
format, API fallback or endpoint. Remove their displaced lifecycle/generated
updater bodies and alternate appimageupdatetool bypass.

Exercise the actual installer/generated standalone updater/manager batch delivery
using retained observation bytes and temporary roots. Include both architecture
selectors, stale/integrity/empty-selection refusal before mutation, current and
embedded AMREPO, download failure/retry and same-version checksum repair. If a
retained response lacks a matching asset, record that limitation and exercise
refusal; do not collect releases or alter a selector to manufacture success.
Use clearly identified synthetic data only for otherwise unavailable mechanics,
without claiming retained upstream compatibility for it.

Report total source and installed code cost, not only recipe length. Baseline
231 source lines across three recipes; about 168 recipe lines can be removed if
each fits the existing 21-line shape. This is a projection. Finish implementation,
meaningful verification and docs together, committing locally. No source enrollment,
collection, installed fleet delivery or workflow/source push is implied.

Evidence: [inventory](../research/recipe-family-inventory.md),
[exact exceptions](../research/recipe-exceptions-and-callers.md).
