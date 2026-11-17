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

Scripts were run from
`/tmp/claude-1000/-home-marek/0626f771-d36c-4bbe-9bad-c108ce3b8987/scratchpad/ticket31/`,
which does not survive a reboot; their full text is in the appendix. All read Git objects only; no checkout, no other worktree touched.

```sh
R=/home/marek/code/shell/AM U=ba061a639a50260b6be405b15b22be10be328264 O=36c087049957734cd10b0aa4c509e5520b46d93b
python3 -I versions.py $R $U versions.json          # 392 template versions
python3 -I -B match.py $R $U $O versions.json matches.json   # 11,782 rows, ~50 s
python3 -I table.py versions.json matches.json       # the main table
python3 -I report.py versions.json matches.json $R/tools/recipe-conversion/layouts.json  # tree forms, layout sanity check
git -C $R ls-tree -r --name-only 7b4f831e6 -- programs/x86_64 programs/aarch64 programs/i686 programs/armv7l > base_paths.txt
python3 -I origins.py versions.json matches.json base_paths.txt $R $U   # originals added since the merge base
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

### `versions.py`

```python
#!/usr/bin/env python3
"""Every distinct version of every upstream template, from Git history.

Usage: versions.py REPO UPSTREAM OUT.json

For each file under templates/ on UPSTREAM, walk `git log --follow` and keep
the blob at each commit, following renames (R) but stopping at the commit
where the file was created as a copy (C): --follow otherwise continues into
the copied file's history (AM-SAMPLE-AppBundle into AM-SAMPLE-AppImage, the
muliple-variants template into programs/x86_64/zapzap, ...).
Templates deleted before UPSTREAM are walked the same way from the parent of
their deleting commit, and flagged deleted=True.
Distinct bodies only (first, i.e. newest, commit that has that body kept, plus
the oldest commit having it).
"""
import json, subprocess, sys

repo, upstream, out = sys.argv[1:4]

def git(*a):
    return subprocess.check_output(['git', '-C', repo, *a], stderr=subprocess.DEVNULL).decode('utf-8', 'replace')

def walk(start, path):
    rows = []
    log = git('log', '--follow', '--name-status', '--format=C %H %ad', '--date=short', start, '--', path)
    commit = date = None
    for line in log.splitlines():
        if line.startswith('C '):
            _, commit, date = line.split(); continue
        if not line.strip(): continue
        parts = line.split('\t')
        status, newpath = parts[0], parts[-1]
        if status.startswith('D'): continue
        if not newpath.startswith('templates/'): break
        rows.append((commit, date, newpath))
        # A copy (C) starts this file: what --follow shows before it is the
        # history of the file it was copied from (another template, or a
        # recipe), not a version of this template. Renames (R) are followed.
        if status.startswith('C'): break
    return rows

current = git('ls-tree', '--name-only', upstream, 'templates/').split()
deleted = []
for line in git('log', '--diff-filter=D', '--name-only', '--format=C %H', upstream, '--', 'templates/').splitlines():
    if line.startswith('C '): commit = line.split()[1]
    elif line.strip() and line.strip() not in current: deleted.append((line.strip(), commit))

versions = []
gens = {}
def generator(commit):
    if commit not in gens:
        try: gens[commit] = git('show', commit + ':modules/template.am')
        except subprocess.CalledProcessError: gens[commit] = ''
    return gens[commit]

seen_names = set()
claimed = set()
for name, start, is_deleted in [(p, upstream, False) for p in current] + [(p, c + '^', True) for p, c in deleted]:
    if (name, is_deleted) in seen_names: continue
    seen_names.add((name, is_deleted))
    bodies = {}
    for commit, date, path in walk(start, name):
        try: body = git('show', commit + ':' + path)
        except subprocess.CalledProcessError: continue
        if body not in bodies:
            bodies[body] = dict(template=name, deleted=is_deleted, commit=commit, date=date, path=path,
                                oldest_commit=commit, oldest_date=date)
        else:
            bodies[body].update(oldest_commit=commit, oldest_date=date)
    for body, row in bodies.items():
        if body in claimed: continue  # a deleted name renamed into a current one
        claimed.add(body)
        row['body'] = body
        row['generator'] = generator(row['commit'])
        row['lines'] = body.count('\n')
        versions.append(row)

for i, v in enumerate(versions): v['id'] = i
json.dump(versions, open(out, 'w'))
from collections import Counter
c = Counter((v['template'], v['deleted']) for v in versions)
for (t, d), n in sorted(c.items()): print(n, t, '(deleted)' if d else '')
print('total distinct versions', len(versions))
```

### `match.py`

```python
#!/usr/bin/env python3
"""Match every upstream original against every version of every template.

Usage: match.py REPO UPSTREAM OURS versions.json OUT.json

Reuses the repo's own code, read from REPO (trusted):
  - tools/recipe-reconstruction/originals.py  Template (whole-file, line-for-line
    matcher with SLOTS placeholders) -> exact instances
  - tools/recipe-conversion/convert.py         QUOTING (APP='x' / SITE='x'
    normalisation the declaration converter applies before matching)
  - tools/upstream-merge/merge.py              recipes() (programs/<arch>/* at a
    revision) and form() (declaration / long / other converted / original)
"""
import difflib, json, sys
from collections import defaultdict

repo, upstream, ours, versions_path, out = sys.argv[1:6]
sys.path[:0] = [repo + '/tools/upstream-merge', repo + '/tools/recipe-conversion',
                repo + '/tools/recipe-reconstruction', repo + '/tools/catalog-collector']
import merge, convert
from originals import Template

NEAR = 5        # a near miss has 1..NEAR edited lines against its closest version
REPORT = 60     # closest-version distance is recorded up to this many edited lines

versions = json.load(open(versions_path))
templates = []
for v in versions:
    t = Template(v['commit'], v['path'], v['body'], v['generator'])
    lits = {}; slotlines = {}
    tokens = []
    for line, (pattern, names) in zip(t.lines, t.patterns):
        if names:
            slotlines.setdefault(line, pattern); tokens.append('T:' + line)
        else:
            lits[line] = True; tokens.append(line)
    templates.append(dict(v=v, t=t, lits=set(lits), slots=list(slotlines.items()), tokens=tokens, n=len(t.lines)))

def normalise(source):
    for pattern, plain in convert.QUOTING: source = pattern.sub(plain, source)
    return source

def distance(entry, lines, lineset):
    """Edited lines between a template version and a recipe, or None if > REPORT.

    A recipe line equals a template line when it is the same literal line, or
    when it fully matches that template line with its placeholders (SAMPLE,
    REPLACETHIS, FUNCTION, ...) standing for any single-line text. Placeholder
    values are not required to agree between lines (unlike the exact test).
    A replaced block of a removed and b added lines counts max(a, b).
    """
    if abs(len(lines) - entry['n']) > REPORT: return None
    if len(entry['lits'] - lineset) > REPORT: return None
    rtokens = []
    for i, line in enumerate(lines):
        if line in entry['lits']: rtokens.append(line); continue
        for raw, pattern in entry['slots']:
            if pattern.fullmatch(line): rtokens.append('T:' + raw); break
        else: rtokens.append(('X', i))
    edits = 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, entry['tokens'], rtokens, autojunk=False).get_opcodes():
        if op != 'equal': edits += max(i2 - i1, j2 - j1)
        if edits > REPORT: return None
    return edits

up = merge.recipes(repo, upstream)
mine = merge.recipes(repo, ours)
rows = []
for path in sorted(up):
    raw = up[path].decode('utf-8', errors='replace')
    source = normalise(raw)
    exact = []
    for e in templates:
        m = e['t'].match(source)
        if m: exact.append(dict(version=e['v']['id'], status=m['status']))
    best = None
    if not exact:
        lines = source.splitlines(keepends=True); lineset = set(lines)
        for e in templates:
            d = distance(e, lines, lineset)
            if d is not None and (best is None or d < best[0]): best = (d, e['v']['id'])
    rows.append(dict(recipe=path, arch=path.split('/')[1], requoted=(source != raw),
                     exact=exact, closest=None if best is None else dict(edits=best[0], version=best[1]),
                     ours=merge.form(mine[path]) if path in mine else 'absent'))
extra = sorted(set(mine) - set(up))
json.dump(dict(rows=rows, ours_only=[dict(recipe=p, ours=merge.form(mine[p])) for p in extra]), open(out, 'w'))
print('upstream recipes', len(rows), 'ours-only', len(extra))
```

### `table.py`

```python
#!/usr/bin/env python3
"""Markdown table per template x arch. Usage: table.py versions.json matches.json"""
import json, sys
from collections import Counter, defaultdict
V = json.load(open(sys.argv[1])); M = json.load(open(sys.argv[2]))
rows = M['rows']
ARCH = ('x86_64', 'aarch64', 'i686', 'armv7l')
fam = {v['id']: v['template'] for v in V}
current = sorted({v['template'] for v in V if not v['deleted']})

def assign(r):
    fs = sorted({fam[x['version']] for x in r['exact']})
    assert len(fs) <= 1, r
    if fs: return 'exact', fs[0]
    if r['closest'] and r['closest']['edits'] <= 5: return 'near', fam[r['closest']['version']]
    return 'none', None

cell = defaultdict(Counter)   # (template, kind, arch) -> forms
for r in rows:
    k, f = assign(r)
    if f is not None and f not in current: f = 'deleted'
    cell[(f, k, r['arch'])][r['ours']] += 1

def fmt(c):
    n = sum(c.values()); nd = n - c['declaration']
    return n, nd

def line(name, f):
    out = [name]; tot = Counter(); totn = Counter()
    for a in ARCH:
        e = cell[(f, 'exact', a)]; n = cell[(f, 'near', a)]
        en, end = fmt(e); nn, nnd = fmt(n)
        out.append(f'{en} / {end}' if en else '0'); out.append(f'{nn} / {nnd}' if nn else '0')
        tot += e; totn += n
    en, end = fmt(tot); nn, nnd = fmt(totn)
    out += [f'**{end}**', str(en), f'{tot["long"]} / {tot["original"]} / {tot["other converted"]} / {tot["declaration"]}', f'{nnd}', str(nn)]
    return end, '| ' + ' | '.join(out) + ' |'

print('| Template | x86_64 exact | x86_64 near | aarch64 exact | aarch64 near | i686 exact | i686 near | armv7l exact | armv7l near | Exact, not declaration | Exact, all | Exact: long / original / other conv. / declaration | Near, not declaration | Near, all |')
print('|' + ' --- |' * 15)
lines = [line(f.removeprefix('templates/'), f) for f in current]
for _, l in sorted(lines, key=lambda x: -x[0]): print(l)
print(line('(templates deleted before ba061a639)', 'deleted')[1])
# no match
out = ['(no template, nearest > 5 edited lines)']; tot = Counter()
for a in ARCH:
    c = cell[(None, 'none', a)]; n, nd = fmt(c); out += [f'{n} / {nd}', '']; tot += c
n, nd = fmt(tot)
out += [f'**{nd}**', str(n), f'{tot["long"]} / {tot["original"]} / {tot["other converted"]} / {tot["declaration"]}', '', '']
print('| ' + ' | '.join(out) + ' |')
print('total upstream recipes', len(rows), Counter(r['arch'] for r in rows))
```

### `report.py`

```python
#!/usr/bin/env python3
"""Summaries from matches.json + versions.json. Usage: report.py versions.json matches.json [layouts.json]"""
import json, sys
from collections import Counter, defaultdict
V = json.load(open(sys.argv[1])); M = json.load(open(sys.argv[2]))
layouts = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else []
rows = M['rows']
ARCH = ('x86_64', 'aarch64', 'i686', 'armv7l')
fam = {v['id']: v['template'] for v in V}
dele = {v['id']: v['deleted'] for v in V}

print('== our tree forms (all recipes on main-marek)')
c = Counter(r['ours'] for r in rows) + Counter(r['ours'] for r in M['ours_only'])
print(dict(c))
print('ours-only', M['ours_only'])
print('== forms per arch');
for a in ARCH: print(a, dict(Counter(r['ours'] for r in rows if r['arch'] == a)), 'upstream', sum(r['arch'] == a for r in rows))

def families(r):
    return sorted({fam[x['version']] for x in r['exact']})

print('== exact family-set overlaps')
print(Counter(len(families(r)) for r in rows))
print(Counter(tuple(families(r)) for r in rows if len(families(r)) > 1).most_common(10))

# Primary family: exact -> the family (ties: current over deleted, then the
# family with the most exact instances overall); else near miss by closest.
tot = Counter(f for r in rows for f in families(r))
def primary(r):
    fs = families(r)
    if fs:
        cur = [f for f in fs if not any(dele[x['version']] for x in r['exact'] if fam[x['version']] == f)]
        return 'exact', max(cur or fs, key=lambda f: tot[f])
    if r['closest'] and r['closest']['edits'] <= 5: return 'near', fam[r['closest']['version']]
    return 'none', None

table = defaultdict(Counter)
for r in rows:
    kind, f = primary(r)
    table[(f, kind)][(r['arch'], r['ours'])] += 1
json.dump({f'{k[0]}|{k[1]}': {f'{a}|{o}': n for (a, o), n in v.items()} for k, v in table.items()},
          open('table.json', 'w'), indent=1)

print('== layouts sanity')
lay = {(l['commit'], l['path']) for l in layouts}
lay_ids = {v['id'] for v in V if (v['commit'], v['path']) in lay}
# a layout commit may not be the newest commit with that body; match by body hash instead
import hashlib
lay_sha = {l['sha256'] for l in layouts}
lay_ids |= {v['id'] for v in V if hashlib.sha256(v['body'].encode()).hexdigest() in lay_sha}
print('layout version ids', lay_ids, [ (V[i]['commit'][:9], V[i]['oldest_commit'][:9], V[i]['date']) for i in lay_ids])
inst = [r for r in rows if any(x['version'] in lay_ids for x in r['exact'])]
print('exact instances of a reviewed layout:', len(inst), dict(Counter(r['ours'] for r in inst)))
print('  by status', Counter(x['status'] for r in inst for x in r['exact'] if x['version'] in lay_ids))
decl = [r for r in rows if r['ours'] == 'declaration']
print('declarations:', len(decl), 'of which exact reviewed-layout instance upstream:',
      sum(any(x['version'] in lay_ids for x in r['exact']) for r in decl))
print('declarations not reviewed-layout instance:', [ (r['recipe'], families(r), r['closest']) for r in decl if not any(x['version'] in lay_ids for x in r['exact'])][:20])

print('== per family, kind, ours-form (all arches)')
for (f, kind), cnt in sorted(table.items(), key=lambda kv: (str(kv[0][0]), kv[0][1])):
    forms = Counter()
    for (a, o), n in cnt.items(): forms[o] += n
    print(f, kind, sum(cnt.values()), dict(forms))
print('== closest distance distribution for non-exact')
print(sorted(Counter(r['closest']['edits'] if r['closest'] else 99 for r in rows if not r['exact']).items()))
```

### `origins.py`

```python
#!/usr/bin/env python3
"""Why do template instances stay originals/long? Usage: origins.py versions.json matches.json base_paths.txt REPO UPSTREAM"""
import json, sys, subprocess, re
from collections import Counter
V = json.load(open(sys.argv[1])); M = json.load(open(sys.argv[2])); base = set(open(sys.argv[3]).read().split())
repo, up = sys.argv[4], sys.argv[5]
fam = lambda r: V[r['exact'][0]['version']]['template'][10:] if r['exact'] else None
rows = [r for r in M['rows'] if r['exact']]
print('exact instances by (family, ours form, present at merge base 7b4f831e6):')
c = Counter((fam(r), r['ours'], r['recipe'] in base) for r in rows)
for k, n in sorted(c.items(), key=str): print(n, k)
# selection host of originals that are reviewed-layout instances
lay = {7, 10}
orig = [r for r in rows if r['ours'] == 'original' and r['exact'][0]['version'] in lay]
hosts = Counter()
for r in orig:
    src = subprocess.check_output(['git', '-C', repo, 'show', up + ':' + r['recipe']]).decode('utf-8', 'replace')
    m = re.search(r'^SITE="?([^"\n]*)', src, re.M)
    s = m[1] if m else ''
    hosts['github-like OWNER/REPO' if re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', s) else 'other: ' + s.split('/')[0][:30]] += 1
print('reviewed-layout originals by SITE shape:', hosts.most_common(12))
```

### `loose.py`

```python
#!/usr/bin/env python3
"""Loose families (6..20 edited lines) and the multiple-choice group. Usage: loose.py versions.json matches.json choice.txt"""
import json, sys
from collections import Counter, defaultdict
V = json.load(open(sys.argv[1])); M = json.load(open(sys.argv[2]))
choice = set(open(sys.argv[3]).read().split())
rows = M['rows']
fam = lambda r: V[r['closest']['version']]['template'].removeprefix('templates/') if r['closest'] else None
print('== loose (6..20 edited lines), per family: n, not-declaration, arches, forms')
g = defaultdict(list)
for r in rows:
    if not r['exact'] and r['closest'] and 6 <= r['closest']['edits'] <= 20: g[fam(r)].append(r)
for f, rs in sorted(g.items(), key=lambda kv: -len(kv[1])):
    print(f, len(rs), sum(r['ours'] != 'declaration' for r in rs), dict(Counter(r['arch'] for r in rs)), dict(Counter(r['ours'] for r in rs)))
print('== recipes with the choice prompt:', len(choice))
cr = [r for r in rows if r['recipe'] in choice]
print('exact:', Counter(V[r['exact'][0]['version']]['template'] for r in cr if r['exact']))
print('closest:', Counter((fam(r), (r['closest']['edits'] if r['closest'] else None)) for r in cr if not r['exact']).most_common(40))
print('forms:', Counter(r['ours'] for r in cr), 'arch', Counter(r['arch'] for r in cr))
print('== versions hit by exact instances (family, version date, newest commit, count)')
c = Counter((V[x['version']]['template'], V[x['version']]['date'], V[x['version']]['commit'][:9], V[x['version']]['oldest_commit'][:9]) for r in rows for x in r['exact'])
for k, n in sorted(c.items()): print(n, *k)
print('== exact status (instance vs parameter_review) per family')
print(Counter((V[r['exact'][0]['version']]['template'], r['exact'][0]['status']) for r in rows if r['exact']))
print('requoted rows', sum(r['requoted'] for r in rows), 'of which exact', sum(r['requoted'] and bool(r['exact']) for r in rows))
print('== near (<=5) list sample per family')
for r in rows:
    if not r['exact'] and r['closest'] and r['closest']['edits'] <= 5 and fam(r) not in ('AM-SAMPLE-AppImage', 'AM-SAMPLE-Archive'):
        print(' ', r['recipe'], fam(r), r['closest']['edits'], r['ours'])
print('== no family within 20 lines:', [ (r['recipe'], r['ours'], fam(r), r['closest'] and r['closest']['edits']) for r in rows if not r['exact'] and not (r['closest'] and r['closest']['edits'] <= 20)][:80])
```

### `queries.py`

```python
#!/usr/bin/env python3
"""Per-version split of exact instances by (arch, our form). Usage: queries.py versions.json matches.json"""
import json, sys
from collections import Counter, defaultdict
V = json.load(open(sys.argv[1])); M = json.load(open(sys.argv[2]))
c = defaultdict(Counter)
for r in M['rows']:
    for x in r['exact']:
        v = V[x['version']]; c[(v['template'][10:], v['commit'][:9], v['date'])][(r['arch'], r['ours'])] += 1
for k, v in sorted(c.items()): print(k, dict(v))
```

Fifth-form header check, from the repo, with `other.txt` the 106 paths whose `ours` is "other converted" in `matches.json`:

```sh
for p in $(cat other.txt); do git show main-marek:$p | grep -m3 '^# AM-CATALOG-\|^CATALOG_FORMAT' | tr '\n' ' '; echo; done | sort | uniq -c
# 106 # AM-CATALOG-RECIPE 1 CATALOG_FORMAT=3
```
