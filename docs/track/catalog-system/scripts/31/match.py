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
