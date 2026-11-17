# Review template 3.6's multiple launchers against the shared installer

Type: grilling
Label: wayfinder:grilling
Status: open
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
