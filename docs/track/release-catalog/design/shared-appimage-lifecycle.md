# Shared AppImage lifecycle

Ticket [42](../issues/42-shared-appimage-lifecycle.md), baseline `0de7c6400`.

`modules/appimage.am` owns install/update for the x86_64 Obsidian and SQLite
Browser recipes. Only `PACKAGE_KIND=appimage` is supported. Archive and plain
binary packages, other architectures and installed migration are outside this
implementation. Ticket [44](normal-batch-updates.md) subsequently adds manager
batch routing without changing the recipe interface.

The trusted recipe declares APP, exact CATALOG_ALIAS, PACKAGE_KIND and one
`select_asset` pipeline operating on stdin. Obsidian alone supplies the real
`appimage_desktop` exception that removes `--no-sandbox`. SQLite Browser retains
its release-tag, architecture, nightly/continuous/RC/dev filtering. Both pipelines
and selected original upstream URLs are preserved. The catalog remains inert
upstream response bytes; it neither supplies shell code nor resolves app assets.

The remaining recipe lines bind delivery paths and AMREPO, source the managed
module and call `am_appimage "$0" "$@"`. These are installation bindings, not a
configuration language. `install.am` embeds both managed helper locations and the
selected source with literal escaping before privilege environment clearing. Its
existing AppMan path rewrite binds APPS_DIR, BIN_DIR and DESKTOP_DIR. The ordinary
`--icons` option inserts a private `--am-icons` argument that persists with the
recipe. The manager inventories `appimage.am` through its normal module sync and
obsolete-module cleanup; updaters never download runtime code.

After accepted reader preflight and nonempty selection, the module compares URL
versions and honors recorded checksum failure. A fresh tmp download is made with
wget, or curl if wget is unavailable, before replacing the binary or version.
Failed transfer preserves a working app and its version; retry replaces partial
tmp contents only after new acceptance. Initial incomplete-install cleanup also
waits for acceptance, and does not invoke an old remover when a version file
identifies a working install. Notifications are nonfatal. Install then creates
quoted remover/launcher paths, saves the trusted recipe as `recipe.am`, sets the
binary link, extracts desktop/icon (including bounded symlink resolution and
7z/7zz fallback), and applies the genuine app exception. Updates retain existing
launchers/icons, as the prior updaters did.

Each installed `AM-updater` is exactly three lines: shebang, existing catalog
routing marker and `exec sh '<installed recipe>' --am-update "$@"`. The saved
recipe invokes the same managed implementation and selector as initial install.
It needs neither source checkout nor inherited manager configuration. Standalone
AMREPO uses the embedded source unless explicitly overridden; managed updates
pass the manager's current source. Explicit empty source still refuses. Optional
binary verification remains in the manager after successful execution, separate
from reader hash validation and inclusive 48-hour freshness/exact stale consent.

## Cost audit

Physical lines/bytes, including comments and blanks, before/after this ticket:

| Source | Before lines | After lines | Before bytes | After bytes |
| --- | ---: | ---: | ---: | ---: |
| Obsidian recipe | 96 | 23 | 4021 | 669 |
| SQLite Browser recipe | 96 | 21 | 4123 | 672 |
| Shared reader | 102 | 102 | 5238 | 5238 |
| Shared lifecycle | 0 | 91 | 0 | 3958 |
| Install module (whole file) | 1427 | 1433 | 60079 | 60404 |
| Manager (whole file) | 3153 | 3154 | 123418 | 123448 |
| Total | 4874 | 4824 | 196879 | 194389 |

Net: **50 fewer source lines, 2490 fewer bytes**, including all new runtime and
manager changes. The 192 recipe lines become 44 recipe lines plus 91 shared lines;
this removes the two lifecycle bodies and two separately generated update bodies,
not just their metadata calls. The reader is unchanged. Whole-file manager counts
make the denominator large, so the absolute delta is the useful measurement.

Installed shell code per app previously comprised a 27-line generated updater
plus a five-line remover. Now Obsidian has a 23-line saved recipe, three-line
updater and five-line remover (31 vs 32); SQLite Browser has 21+3+5 (29 vs 32).
The shared reader and lifecycle are delivered once per AM/AppMan installation,
not once per app. Per-app installed code barely shrinks. Including the once-per-manager runtime,
the two-app installed shell footprint grows from 166 lines (102 reader + 64
per-app) to 253 (102 reader + 91 lifecycle + 60 per-app), **87 additional lines**.
This is the explicit delivery cost of retaining trusted recipes while centralizing
mechanics; it is not an installed-size reduction. The benefit is one maintained
lifecycle and one selector per app. Binary assets and generated desktop
entries are excluded from shell-code counts. Installed source embedding changes
byte lengths with actual host paths, so no universal installed byte claim is made.

## Verification

`test_appimage_lifecycle.py` replaces the former two recipe test files. It invokes
the real shared interface, actual install dispatch/patch/privilege handoff, module
sync/cleanup and manager foreground update routing. Retained metadata and stubbed
binary/network operations exercise both apps, original URLs, install/update/no-change,
AppMan/system layouts, standalone source persistence, missing helpers, integrity
and empty-filter refusal before mutation, exact stale consent, failed transfer and
retry, working-binary preservation, recorded checksum repair, literal path quoting,
icon-theme delivery and optional manager verification failures. It executes no
host app and makes no live requests. Historical evidence is unchanged.

Final checks: 124 tests from `python -m unittest discover -s tools/catalog-collector`
and 8 from `python -m unittest discover -s tools/catalog-probe`; POSIX recipe/runtime
and Bash manager/install syntax; `shellcheck -x -S warning` on reader, runtime and
both recipes; `git diff --check`. All pass. No deployment or host migration.

## Third caller: nvim (ticket 43)

At baseline `c2bcd8f82`, the x86_64 nvim recipe also installs AppImage, so it
requires neither a new format nor an additional shared hook. It now uses the
already-enrolled `https://api.github.com/repos/neovim/neovim/releases` alias and
retains one exact copy of its original selector: release-list URLs containing
`releases`/`nvim`, ending in `mage`, excluding nightly and the other architectures.
The two original install/update filters select the same retained upstream URL:
`https://github.com/neovim/neovim/releases/download/v0.12.6/nvim-linux-x86_64.appimage`.
This describes retained observation bytes, not a fresh release check.

The recipe shrinks from 77 lines / 3167 bytes to 21 lines / 607 bytes: **56 lines
and 2560 bytes removed**, including its duplicated lifecycle and 25-line generated
updater. The shared reader, lifecycle and manager require no changes or new code.
Its appimageupdatetool bypass is removed so update and repair consistently use the
same accepted metadata and selector as installation. No app-specific hook is needed.

nvim's installed shell code changes from a 25-line updater + five-line remover
(30) to a 21-line saved recipe + three-line updater + five-line remover (29).
For a host already carrying the ticket 42 runtime, this is one fewer installed
line; the three-app total including the once-per-manager reader/lifecycle is
282 lines (253 from the previous two-app audit + 29). The prior two-app audit
above is retained at its original baseline.

The shared recipe test cases are reused by both SQLite Browser and nvim, with
app identity, alias, recipe path and expected URL supplied by each test class.
This exercises the same real interface and actual manager delivery for nvim:
install/update/no-change, transfer failure/retry/checksum repair, preflight refusal
and exact stale consent, managed source override, standalone source persistence
through privilege environment clearing, and AppMan/system paths. A separate
retained-byte comparison verifies that both original selectors equal the one
remaining in the recipe. No runtime hook expansion, source enrollment, collection,
host migration or app execution is involved.

Ticket 43 validation: all 132 catalog tests pass, including eight nvim cases;
warning-level ShellCheck on reader/runtime/all three recipes, shell syntax and
`git diff --check` pass. All operations used retained bytes and temporary roots.


## Remaining Neovim recipes (ticket 46)

All three remaining recipes now use the same lifecycle and their original exact
selectors. Retained observations contain matching AppImages for stable/nightly on
both x86_64 and aarch64. No source enrollment or fresh upstream request is needed.
ARM coverage executes shell selection/lifecycle with inert binaries on x86_64;
it is not ARM machine-code execution.

The unchanged-interface constraint needed one justified exception: nightly assets
change at the same URL. A red regression demonstrated that removing the optional
appimageupdatetool bypass would leave nightly permanently skipped by URL equality.
Trusted nightly recipes now declare `REFRESH_ALWAYS=true`. After normal catalog
acceptance, each requested update downloads the full original binary URL, even if
unchanged; no implicit polling, delta tool, new endpoint or asset parsing is added.
Stable recipes retain URL comparison. This can redownload identical nightly bytes.
Catalog acceptance does not freeze bytes behind a mutable upstream download URL.

Batch reporting also checks the binary's device/inode/mtime, so successful
same-URL replacement reports updated instead of unchanged. This is an operation
result, not proof of different binary contents or software authenticity.

Against e38e8b844 the three recipes shrink from 231 lines / 9537 bytes to 67 /
1979: 164 lines / 7558 bytes removed. Runtime adds 41 bytes (no lines); manager
adds one line / 158 bytes. Total production reduction: **163 lines / 7359 bytes**.
Installed per-app shell is 31/29/31 lines (saved recipe + three-line updater +
five-line remover), versus 30 each before: **one additional line across three
apps**, plus one shared lifecycle delivery for installations lacking it. Existing
shared module costs remain as documented above; no per-host byte claim is made.

Optional existing-binary startup checks passed on both distributions in isolated
containers. Host-specific logs are retained privately, outside publishable Git
history. These checks load no user configuration and make no future-binary claim.

Before live delivery, ticket 51 requires a concrete backup/rollback payload,
container rehearsal of legacy-to-shared delivery, and isolated copied-config
compatibility checks. Current tests do not claim that installed transition.
