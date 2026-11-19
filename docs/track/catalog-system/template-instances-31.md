# Recipes per upstream template

[Ticket 31](issues/31-count-recipes-per-upstream-template.md), November 17, 2026.
Research only: nothing in the repo changed except this file. No conversion, no
`am`, no test suite.

Measured at:

- `upstream/main` = `ba061a639a50260b6be405b15b22be10be328264` (the originals
  and every template version are read from here and its history)
- `main-marek` = `36c087049957734cd10b0aa4c509e5520b46d93b` (the forms in our tree)

Terms are the root `GLOSSARY.md` ones (Recipes section). A recipe's form in our
tree is decided by `form()` in `tools/upstream-merge/merge.py`, called as is:
a recipe declaration carries `# AM-RECIPE-DECLARATION 1`
(`MARKER` in `tools/catalog-collector/recipe_declarations.py`), a long recipe's
second line starts the long-recipe header (`HEADER` in
`tools/catalog-collector/bulk_recipe_urls.py`), anything else with
`# AM-CATALOG-` is "other converted" (the unnamed fifth form of
[ticket 24](issues/24-simplify-and-unify-catalog-process.md)), and the rest
are originals.

## Answer

Ranked by exact instances that are not yet recipe declarations. Each cell is
"instances / of which not declarations". "Near" is a near miss (1 to 5 edited
lines, defined below); a recipe counts in one row only.

| Template | x86_64 exact | x86_64 near | aarch64 exact | aarch64 near | i686 exact | i686 near | armv7l exact | Exact, not declaration | Exact, all | Exact: long / original / other conv. / declaration | Near, not declaration |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | ---: |
| AM-SAMPLE-AppImage-in-archive | 4,947 / 4,919 | 7 / 7 | 1,090 / 1,090 | 1 / 1 | 0 | 0 | 0 | **6,009** | 6,037 | 5,346 / 663 / 0 / 28 | 8 |
| AM-SAMPLE-AppImage, all versions | 4,185 / 3,449 | 194 / 190 | 709 / 460 | 9 / 9 | 8 / 7 | 9 / 9 | 2 / 2 | **3,918** | 4,904 | 2,778 / 1,036 / 104 / 986 | 208 |
| &nbsp;&nbsp;of which the two reviewed versions (`layouts.json`) | | | | | | | | 2,675 | 3,658 | 1,585 / 986 / 104 / 983 | |
| &nbsp;&nbsp;of which unreviewed `bb53f3180` (2025-07-21) | | | | | | | | 1,233 | 1,236 | 1,183 / 50 / 0 / 3 | |
| &nbsp;&nbsp;of which unreviewed `8b53a7656` (2026-07-06) | | | | | | | | 10 | 10 | 10 / 0 / 0 / 0 | |
| AM-SAMPLE-Archive | 215 / 213 | 78 / 77 | 16 / 16 | 7 / 7 | 1 / 1 | 1 / 1 | 0 | **230** | 232 | 228 / 2 / 0 / 2 | 85 |
| AM-SAMPLE-portable2appimage | 3 / 3 | 6 / 6 | 0 | 1 / 1 | 0 | 0 | 0 | **3** | 3 | 1 / 2 / 0 / 0 | 7 |
| AM-SAMPLE-AppImage-download_kde_org | 2 / 2 | 0 | 0 | 0 | 0 | 0 | 0 | **2** | 2 | 0 / 2 / 0 / 0 | 0 |
| AM-SAMPLE-AppBundle | 0 | 1 / 1 | 0 | 0 | 0 | 1 / 1 | 0 | 0 | 0 | | 2 |
| AM-SAMPLE-AppImage-muliple-variants-from-same-source | 0 | 1 / 1 | 0 | 1 / 1 | 0 | 0 | 0 | 0 | 0 | | 2 (both `zalo`, originals) |
| AM-SAMPLE-AppImage-muliple-choices | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | | 0 |
| AM-SAMPLE-AppImage-muliple-choices-Archive+AppImage | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | | 0 |
| AM-SAMPLE-AppImage-muliple-choices-if-SITE1-exists | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | | 0 |
| AM-SAMPLE-AppImage-libreoffice | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | | 0 |
| AM-SAMPLE-RunImage | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | | 0 |
| AM-SAMPLE-dbin | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | | 0 |
| AM-SAMPLE-soarpkg | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | | 0 |
| SAMPLE-rollback | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | | 0 |
| 33 templates deleted before `ba061a639` (all their versions) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | | 0 |
| No template within 5 edited lines | 242 / 238 | | 37 / 37 | | 8 / 8 | | 0 | 283 | 287 | 223 / 60 / 0 / 4 | |

Totals: 11,782 upstream recipes (x86_64 9,881, aarch64 1,871, i686 28,
armv7l 2); 11,178 exact instances, 317 near misses, 287 neither. No recipe is
an exact instance of two different templates. armv7l has no near misses.

Top three by exact instances that are not yet declarations:

1. **AM-SAMPLE-AppImage-in-archive: 6,009** (5,346 long, 663 original).
   5,980 of the 6,037 instances are one version, `cf50304fc` (2026-07-17,
   SHA-256 `d1ae5ae7…`, the same body `originals.py` already pins as
   `AIA_TEMPLATE_SHA256`); 57 are `9599f1206` (2026-04-06). One reviewed
   version would cover almost all of them. It differs from the reviewed
   AppImage 3.6 body only in the download step: three
   `[ -e ./*7z|tar.*|zip ] && extract` lines and a `mv` that accepts a
   directory, in both installer and updater.
2. **AM-SAMPLE-AppImage: 3,918**, but this template is already reviewed in two
   versions. Of the 3,918, 2,675 are instances of a reviewed version and are
   blocked by something other than the template (below); 1,233 are instances
   of the unreviewed version `bb53f3180` (2025-07-21), which differs from the
   reviewed 3.5 body (`b7c72a974`) by one line: the desktop-file `sed` gained
   `s# --no-sandbox##g`. The recipe declaration already has
   `DESKTOP_STRIP_NO_SANDBOX=true` (seen in `programs/x86_64/20x`), so this
   looks like the cheapest review of all (inference: the shared installer was
   not read for this).
3. **AM-SAMPLE-Archive: 230** (228 long), plus 85 near misses and 103 more
   (101 not declarations) within 6 to 20 edited lines. 226 of the instances are version `4a4e43104`
   (2024-07-03). The edits seen in a sample are an uncommented `.desktop`
   remover line plus an appended `# ICON` / `# LAUNCHER` block, or a binary
   name other than `$APP` (inference from three diffs, not counted).

Everything else is tiny. The three edited multiple-choice templates have **no
exact instance and no near miss**, and the new
`muliple-variants-from-same-source` has no exact instance and two near misses,
`x86_64/zalo` and `aarch64/zalo` (2 edited lines, both originals). 85 upstream
recipes carry the choice prompt (`Which version you choose`); apart from the
two `zalo`, their nearest template is 6 to 42 edited lines away (30 of them at
exactly 20), or none within 60 (14: firefox*, thunderbird*, kdenlive), because
each recipe writes its own choice list.
Line-for-line declaration matching does not fit them; they would need a
different kind of declaration (a list of variants), not one more layout.

## Why reviewed-template instances are not declarations

Of the 3,658 instances of a reviewed AppImage version, only 983 are
declarations. The rest:

- **Originals: 986.** At the family level, 914 of the AppImage originals and
  661 of the AppImage-in-archive originals are recipes absent at the merge
  base `7b4f831e6`, that is, added upstream since. `merge.py plan` takes such
  a recipe unconverted (`o is None` → "taken from upstream"; 1,591 such rows
  in `upstream-merge-20261116.json`). 927 of the 986 have a GitHub-shaped
  `SITE`. Converting them needs a verified catalog identity first, which is a
  collection step, not a template review (inference from `convert.py`, which
  refuses without identities).
- **Long recipes: 1,585.** Refused as declarations at bulk conversion; the
  README lists the reasons (selector beyond `sed`/`grep`/`head`, installer
  and updater disagree, a second release read, no identity). Not broken down
  further here.
- **Other converted: 104.** See the fifth form below.

## Sanity check against `layouts.json` and the README

- The matcher finds both reviewed layouts in its version list, by body
  SHA-256 (`326f8517…` at `b7c72a974`, `5353962f…` at `cf50304fc`).
- It finds 983 declarations that are exact instances of a reviewed layout.
  The README's bulk count is 984, of which `odicto` was adapted by hand; the
  matcher puts `odicto` one edited line from the 3.5 layout, a near miss,
  which is that hand adaptation. `pdf4qt` matches the 3.5 layout exactly.
- Recount of our tree (`main-marek`, `programs/{x86_64,aarch64,i686,armv7l}/*`,
  11,790 files): **1,029 recipe declarations, 8,767 long recipes**, 106 other
  converted, 1,888 originals. The README says 984 and 8,770. The 1,029
  declarations are 983 exact reviewed-layout instances, 4 fork-only recipes
  (`x86_64/emmylua`, `logseq-app-db-nightly`, `logseq-app-og`, `zmx`) and 42
  whose upstream original is not an instance of a reviewed layout: 28
  AppImage-in-archive, 3 AppImage `bb53f3180`, 2 Archive, 5 near misses
  (`odicto` among them) and 4 matching nothing within 5 lines (`btop`,
  `fzf`, `kitty`, `yt-dlp`). Examples: `20x` and `2fac`, converted by hand in
  `c2beede26` before the bulk conversion. The long-recipe count moved through the merge's
  deletions, additions and fallbacks; it was not reconciled recipe by recipe.

## Fifth form ("other converted")

**106 remain** in our tree: x86_64 64, aarch64 36, i686 4, armv7l 2. All 106
start `# AM-CATALOG-RECIPE 1` + `CATALOG_FORMAT=3` and call
`modules/appimage.am` through a `select_asset()` shell function, with no
`# AM-RECIPE-DECLARATION 1` marker (example: `programs/aarch64/abracadabra`).
104 of them are exact instances of a reviewed AppImage layout upstream (48 of
3.5, 56 of 3.6), so `convert.py --form declaration` should accept most of them
given their identities (inference; not run). Counted with `merge.form()`, not
a grep.

## Recipes matching no template

287 recipes have no template version within 5 edited lines (223 long, 60
original, 4 declarations: `btop`, `fzf`, `kitty`, `yt-dlp`, all fork
declarations made by hand). By nearest template:

| Group | Recipes | Nearest template, distance |
| --- | ---: | --- |
| Archive with extra steps (launcher/icon block, renamed binary) | 126 | Archive, 6 to 60 lines |
| Multiple-choice recipes (choice prompt present) | 83 | multiple-choices family 6 to 42 lines; 14 none within 60 (firefox*, thunderbird*, kdenlive) |
| AppImage tools without a launcher | 31 | AppBundle `5fe8e5009`, 6 to 60 lines (busybox, appimagelint, linuxdeploy, ...) |
| AppImage with extra steps | 28 | AppImage, 6 to 27 lines (google-chrome*, apidog, briar, ...) |
| Large custom installers | 13 | deleted `neodb` template at 28 to 49 lines (libfuse2 on three architectures, tor-browser*, i686 firefox-esr, zotero), or nothing within 60 (clamtk, libreoffice, pinta-dev, reaper) |
| Other | 6 | portable2appimage or in-archive, 6 to 11 lines |

The grouping is by nearest template and distance (measured); the labels in the
first column come from reading a sample (inference).

## Definitions

**Template versions.** For each of the 15 files under `templates/` on
`upstream/main`, every distinct body the file had in `upstream/main`'s
history: `git log --follow --name-status`, following renames (`R`) and
stopping at the commit where the file was created as a copy (`C`). Without
that stop `--follow` walks into the copied file: AppBundle, RunImage,
download_kde_org, libreoffice, portable2appimage and muliple-variants would
inherit AM-SAMPLE-AppImage's 52 versions, and muliple-variants would inherit
`programs/x86_64/zapzap`'s history. The 33 templates deleted before
`ba061a639` are walked the same way from the parent of the deleting commit.
That gives 392 distinct bodies; per current template: AppBundle 7, AppImage
52, download_kde_org 4, in-archive 3, libreoffice 8, muliple-choices 7,
muliple-choices-Archive+AppImage 6, muliple-choices-if-SITE1-exists 4,
muliple-variants-from-same-source 2, Archive 15, RunImage 3, dbin 3 (one
through the rename from `AM-SAMPLE-bincache-soarpkg-dbin`), portable2appimage
7, soarpkg 4, SAMPLE-rollback 2.

Upstream has 14 `AM-SAMPLE-*` files plus `SAMPLE-rollback`, 15 in all; the
ticket's "15 `AM-SAMPLE-*`" counts `SAMPLE-rollback` among them.

**Exact instance.** `Template.match()` from
`tools/recipe-reconstruction/originals.py`, called as is, returns a result
for the recipe against some version (either of its statuses, `instance` or
`parameter_review`). That is: the same number of lines; each line equal to
the template line with each upstream placeholder (`SAMPLE`, `REPLACETHIS`,
`FUNCTION`, `USER/REPO`, `KEYWORD1`, ... the `SLOTS` list) replaced by some
single-line text; re-rendering gives the recipe byte for byte; and one
`SAMPLE` value that is a valid app name. Before matching, the recipe gets
`convert.QUOTING`, the normalisation the declaration converter applies
(`APP='x'` → `APP=x`, `SITE='x'` → `SITE="x"`); it changed 208 recipes, 201
of which match exactly. Nothing else is normalised: URLs, selectors and the
placeholder values are free text inside their line, and installer and
updater values are not required to agree (`convert.py` checks that later;
this count does not). `parameter_review` only means the `FUNCTION` value is
not the generator's default expression or a placeholder is non-literal; it
does not stop a declaration, which accepts literal filter pipelines.
Status split: AppImage 2,323 `instance` / 2,581 `parameter_review`;
in-archive 431 / 5,606; Archive, portable2appimage: all `parameter_review`;
download_kde_org: both `instance`.

**Near miss.** Not an exact instance of any version, and at most 5 edited
lines from the closest version. Edited lines: the template and the recipe
are compared line by line (`difflib.SequenceMatcher`, no autojunk), where a
recipe line equals a template line when it is the same text or fully matches
that template line with its placeholders standing for any single-line text;
a block of a removed and b added lines counts max(a, b). Unlike the exact
test, placeholder values need not be consistent across lines. One recipe
(`aarch64/bruno-nightly`) is at distance 0 without being exact (its values
fail the exact test's re-render or single-`SAMPLE` check); it counts as a near miss. The
recipe is assigned to the family of its closest version. Distances 6 to 20
are reported as "loose" above, as context only.

Distribution of the distance for the 604 recipes that are not exact: 0: 1,
1: 70, 2: 168, 3: 18, 4: 49, 5: 11, then 6–10: 82, 11–20: 131, 21–60: 56,
none within 60: 18.

## How each number was produced

Scripts were first run from a session scratchpad; since ticket 39 they are
in [`scripts/31/`](scripts/31/), and `run.sh OUT_DIR` there reruns every step
below into `OUT_DIR`, with `layouts.json` as of `539ccac8d` (the two layouts
this ticket reviewed against). All read Git objects only; no checkout, no
other worktree touched. `origins.py` takes `layouts.json` and finds the layout
versions by body hash, as `report.py` does (they were ids 7 and 10).

```sh
R=/home/marek/code/shell/AM U=ba061a639a50260b6be405b15b22be10be328264 O=36c087049957734cd10b0aa4c509e5520b46d93b
python3 -I versions.py $R $U versions.json          # 392 template versions
python3 -I -B match.py $R $U $O versions.json matches.json   # 11,782 rows, ~50 s
python3 -I table.py versions.json matches.json       # the main table
python3 -I report.py versions.json matches.json layouts.json  # tree forms, layout sanity check; writes table.json
git -C $R ls-tree -r --name-only 7b4f831e6 -- programs/x86_64 programs/aarch64 programs/i686 programs/armv7l > base_paths.txt
python3 -I origins.py versions.json matches.json base_paths.txt $R $U layouts.json   # originals added since the merge base
git -C $R grep -l -e 'Which version you choose' $U -- 'programs/x86_64/*' 'programs/aarch64/*' 'programs/i686/*' 'programs/armv7l/*' | sed "s|^$U:||" > choice.txt   # 85
python3 -I loose.py versions.json matches.json choice.txt   # loose families, choice group, per-version counts, statuses
```

The per-version split of the AppImage row is `queries.py versions.json
matches.json`; the "other converted" header check is the last snippet in the
appendix. The
template diffs quoted above are `git diff bb53f3180:templates/AM-SAMPLE-AppImage
b7c72a974:…` and `git diff cf50304fc:templates/AM-SAMPLE-AppImage
cf50304fc:templates/AM-SAMPLE-AppImage-in-archive`.

Earlier related research: release-catalog
[ticket 124](../release-catalog/research/selector-review-groups.md) grouped
selectors at `bbffd15c1` (R36) with first-match counting; its 4,483
in-archive review recipes are consistent with the in-archive lead here.

## Not verified

- Whether the in-archive `cf50304fc` and AppImage `bb53f3180` bodies can share
  `modules/appimage.am` unchanged: install steps were diffed against the
  reviewed templates, not against the shared installer.
- How many of the 6,009 in-archive or 1,233 `bb53f3180` instances
  `convert.py` would actually accept (literal selector, installer and
  updater agreement, a verified identity). The exact test here is looser than
  the converter.
- Why each of the 1,585 long instances of a reviewed layout refused the
  declaration form.
- That the 104 fifth-form recipes re-convert to declarations; `convert.py`
  was not run on them.
- The README's 8,770 long recipes against today's 8,767 was not reconciled
  recipe by recipe.
- The near-miss threshold (5 lines) is a choice; counts at other thresholds
  are in the distance distribution above.
- Group labels in "Recipes matching no template" and the Archive edit pattern
  are read from samples (marked as inference).

## Appendix: scripts

The scripts are in [`scripts/31/`](scripts/31/) (moved there from this
appendix on November 19, 2026, ticket 39, byte for byte).
`scripts/31/run.sh OUT_DIR` reruns the main table and the per-version split
at the commits above; rerun then, it gave the same numbers in every cell.

Fifth-form header check, from the repo, with `other.txt` the 106 paths whose `ours` is "other converted" in `matches.json`:

```sh
for p in $(cat other.txt); do git show main-marek:$p | grep -m3 '^# AM-CATALOG-\|^CATALOG_FORMAT' | tr '\n' ' '; echo; done | sort | uniq -c
# 106 # AM-CATALOG-RECIPE 1 CATALOG_FORMAT=3
```
