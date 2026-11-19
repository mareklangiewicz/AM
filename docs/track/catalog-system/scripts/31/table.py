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
