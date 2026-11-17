# Review template 3.6's multiple launchers against the shared installer

Type: grilling
Label: wayfinder:grilling
Status: resolved
Blocked by: none

## Question

Template 3.6 (`cf50304fc`) installs every launcher an AppImage ships; the
shared installer (`modules/appimage.am`) installs one. Should declarations
from 3.6 instances get 3.6's launcher behavior (a new declaration setting), or
is one launcher the accepted policy?

## What differs

Recorded line by line as `dropped` in `tools/recipe-conversion/layouts.json`
(ticket 36). 3.6, for each top-level `*.desktop` in the AppImage:

- follows a symlink to its target;
- a `NoDisplay=true` entry becomes `$APP-handler-AM.desktop` (typically a URL
  or MIME handler), the first other entry `$APP-AM.desktop`, the rest
  `$APP-$COUNT-AM.desktop`; each extra one adds its `rm -f` to `./remove`;
- removes extras whose sorted content equals `$APP-AM.desktop`;
- applies the `Exec`/`Icon` sed and the `--no-sandbox` strip to all of them.

The shared installer runs 3.5's line
`mv ./squashfs-root/*.desktop ./"$APP".desktop`.

## Found while writing ticket 36 (read, one probe)

With two or more top-level `.desktop` files that `mv` has several sources
and a non-directory target: it exits 1 and moves nothing (probed with
coreutils `mv` in a scratch directory, November 17, 2026). Read, not run:
the shared installer then has no `./"$APP".desktop`, so the following `sed`
and the final `mv` fail too and no launcher is installed at all. 3.5 behaves
the same, so this is not a regression of the conversion, but it means 3.6's
change fixed a real failure, not only added extras.

## Not verified

- How many of the 3.6 instances' AppImages ship more than one top-level
  `.desktop` (needs payloads; not fetched).
- Whether `--appimage-extract '*.desktop'` and the 7z fallbacks extract the
  same set.
- Whether the shared installer's desktop subshell stops at the first failure
  (no `set -e` seen in the lines read) and what it then reports.

## Options

1. A declaration setting (e.g. `DESKTOP_LAUNCHERS=all`) that reproduces 3.6;
   3.6's `layouts.json` entries move from `dropped` to that setting and its
   instances are re-converted (ticket 35's command).
2. Make the shared installer handle several desktop files for every
   declaration (no setting), at least not failing on the second one.
3. Accept one launcher and document it as policy.

## Comments

## Answer — November 17, 2026

Marek chose option 2 in the session: a proper shared-installer fix, every
declaration, no setting.

- Confirmed through the real install path (the first red test): with two
  top-level desktop files the old `mv` aborted the whole install with exit 1,
  after the AppImage, the command link and `remove` were already in place
  (`am_package` runs under `set -eu`; the `mv` was the last command of an `&&`
  list).
- `modules/appimage.am`: every top-level `*.desktop` is a launcher, its
  symlink chain resolved like the icon's (against the AppImage root, at most
  10 hops; a copy, so two links to one entry work). The first visible one in
  byte order is `$APP-AM.desktop`, further ones `$APP-2-AM.desktop` and on,
  `NoDisplay=true` ones `$APP-handler-AM.desktop`, `-handler-2-` and on. A
  copy of the main launcher (same sorted lines, as 3.6 compares) is skipped.
  The existing `Exec`/`Icon` sed, strip, `DESKTOP_EXEC` and `appimage_desktop`
  hook run per launcher, unchanged. An existing `$APP-AM.desktop` still skips
  the step; an existing extra is preserved and left out of `remove`; each new
  extra adds its `rm -f`. No desktop file now installs without a launcher.
  The section sets `LC_ALL=C`: bash as `sh` sorts globs by locale.
- Not copied from 3.6: its `$COUNT` is 0 for every extra in the first pass
  (a third launcher overwrote the second), its `A && B || C && D` appended an
  `rm` for `$APP-0-AM.desktop` even without one, and two handlers overwrote
  each other.
- Tests: `tools/catalog-collector/test_appimage_desktops.py` (8, fast tier)
  installs a declaration with an authored AppImage. Each rule was mutated away
  in turn (8 mutations) and a test failed each time; the locale test fails
  without the `LC_ALL=C` line and skips without bash or `en_US.UTF-8`.
- `layouts.json`: 3.6's 22 launcher lines move from `dropped` to `neutral`;
  nothing is dropped now.
- `docs/catalog-operating-policy.md`, Recipe launcher settings: the rule.

Applies to installs only: an update (`AM-updater`, `--am-update`) exits
before the desktop step, so installed apps get extra launchers on their next
reinstall. 3.5-template declarations get the same behavior. For a single
desktop file it is unchanged unless that entry is `NoDisplay=true`: it now
installs as `$APP-handler-AM.desktop` (with its `rm -f`), as in 3.6.

November 17, 2026: pushed with Marek's approval as `38a2ea488` after Long
tests run 44145434756 passed on `ci/desktop-launchers` (fast, with the locale
test run, not skipped; tree; Debian and Fedora e2e). `CATALOG_SCHEDULE_REVISION`
repinned to it; dispatched catalog run 44147378216 (acquire, publish) and
Fast tests 44147374110 passed. Branch `ci/desktop-launchers` deleted.
