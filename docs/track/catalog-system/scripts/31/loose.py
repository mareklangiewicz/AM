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
