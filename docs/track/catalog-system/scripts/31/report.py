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
