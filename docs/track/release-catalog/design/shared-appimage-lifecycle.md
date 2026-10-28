# Shared AppImage lifecycle

Ticket [42](../issues/42-shared-appimage-lifecycle.md), baseline `0de7c6400`.

`modules/appimage.am` owns install/update for the x86_64 Obsidian and SQLite
Browser recipes. Only `PACKAGE_KIND=appimage` is supported. Archive and plain
binary packages, other architectures, batch routing and installed migration are
outside this implementation.

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
