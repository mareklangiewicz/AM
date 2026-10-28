# Migrate the three remaining Neovim AppImages together

Type: task
Status: resolved
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

## Answer — 2026-10-28

All three original selectors and binary URLs are preserved; retained observations
contain matching stable/nightly AppImages for both architectures. Shared tests
exercise real recipes/install dispatch/standalone updater/AppMan/source persistence,
stale/exact consent, integrity/empty-selection refusal, retry and checksum repair.
ARM machine code is not executed; fixture executables are inert x86-host shell.

Host delivery is separate. [51](51-prepare-neovim-host-delivery.md) records the
legacy-delivery rehearsal, isolated configuration checks and backup/rollback gates.

One demonstrated scope correction to the unchanged interface: nightly requires
`REFRESH_ALWAYS=true`, since its binary URL is mutable. Red regression failed
with “mutable URL was incorrectly skipped”; with the small trusted recipe policy,
explicit updates download the full original nightly URL after acceptance. Stable
retains URL comparison. Optional appimageupdatetool bypass is removed. Downloading
identical bytes again is the deliberate simplicity/cost tradeoff. Catalog integrity
and measured freshness do not freeze future bytes at that mutable binary URL.
Manager result reporting detects binary replacement as well as URL/repair state.

The [cost/interface audit](../design/shared-appimage-lifecycle.md#remaining-neovim-recipes-ticket-46)
records total production -163 lines / -7359 bytes, including runtime/manager
changes, versus e38e8b844. Installed per-app code across the three grows one line;
a host without the shared runtime must also receive that once-per-manager module.

Container matrix final successful run: 20261028T165408Z-480067, nine scenarios /
28 commands per target (18 / 56 total), Debian/dash and Fedora/bash. The Neovim
scenario uses actual retained metadata and inert binary fixtures; preserves user
symlink/config sentinels while covering nightly refresh/failure/retry/stale refusal.
The source tree was frozen for that successful run. Earlier failures are retained
in ignored run dirs: initial adapter lacked the real retained nightly URL; a second
run detected an edit made during execution via its source hash guard. Neither is
counted as successful evidence.

Optional existing-binary smoke checks passed on both distributions with disposable
homes and no user configuration. Host-specific evidence is retained privately.
No host migration, source push, collection, workflow or publication change occurred.
Pilot 37 and authorized switch 41 remain independent.

Final validation: **182 catalog tests + 8 historical probe tests pass**; shell
syntax, warning ShellCheck and unchanged manager warning-code baseline pass.
[Checks](../research/neovim-migration-46-checks.txt) and
[actual successful archive](../research/neovim-migration-46-evidence.tar.gz)
retain the fixture run, per-command logs, transport traces and source hashes.
