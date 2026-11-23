"""Per source: newest-first position of the first release with a Linux-looking asset, and of the first non-prerelease."""
import collections, pathlib, re, sys
KEY = re.compile(r'^( *)"?([^":]+)"?: ?(.*)$')
LINUX = re.compile(r'appimage|linux|\.deb"?$|\.rpm"?$|musl|gnu', re.I)
lin, stab = collections.Counter(), collections.Counter()
for path in pathlib.Path(sys.argv[1]).glob('*.yaml'):
    rels = []; cur = None; inrel = False
    for line in path.read_text().splitlines():
        m = KEY.match(line)
        if not m: continue
        ind, key, val = len(m.group(1)), m.group(2), m.group(3)
        if ind == 0: inrel = key == 'releases'; continue
        if not inrel: continue
        if ind == 2: cur = dict(id=int(key), when='', pre=False, linux=False); rels.append(cur)
        elif ind == 4 and key in ('published_at', 'created_at') and not cur['when']: cur['when'] = val
        elif ind == 4 and key == 'published_at': cur['when'] = val
        elif ind == 4 and key == 'prerelease': cur['pre'] = val == 'true'
        elif ind == 8 and key == 'name' and LINUX.search(val): cur['linux'] = True
    if not rels: continue
    rels.sort(key=lambda r: (r['when'], r['id']), reverse=True)
    def pos(pred):
        return next((i + 1 for i, r in enumerate(rels) if pred(r)), 'none')
    def bucket(p): return p if p == 'none' else '1' if p == 1 else '2-3' if p <= 3 else '4-8' if p <= 8 else '9-16' if p <= 16 else '17+'
    lin[bucket(pos(lambda r: r['linux']))] += 1
    stab[bucket(pos(lambda r: not r['pre']))] += 1
order = ['1', '2-3', '4-8', '9-16', '17+', 'none']
print('first Linux-looking asset at release #:', {k: lin[k] for k in order})
print('first non-prerelease at release #:     ', {k: stab[k] for k in order})

# Which deep-Linux sources have an AM recipe (any architecture present in provenance)?
deep = []
for path in pathlib.Path(sys.argv[1]).glob('*.yaml'):
    rels = []; cur = None; inrel = False
    for line in path.read_text().splitlines():
        m = KEY.match(line)
        if not m: continue
        ind, key, val = len(m.group(1)), m.group(2), m.group(3)
        if ind == 0: inrel = key == 'releases'; continue
        if inrel and ind == 2: cur = dict(id=int(key), when='', linux=False); rels.append(cur)
        elif inrel and ind == 4 and key == 'published_at': cur['when'] = val
        elif inrel and ind == 4 and key == 'created_at' and not cur['when']: cur['when'] = val
        elif inrel and ind == 8 and key == 'name' and LINUX.search(val): cur['linux'] = True
    rels.sort(key=lambda r: (r['when'], r['id']), reverse=True)
    p = next((i + 1 for i, r in enumerate(rels) if r['linux']), None)
    if p and p > 8:
        prov = (pathlib.Path(sys.argv[1]).parent / 'provenance' / path.name).read_text()
        deep.append((p, path.stem, 'recipe' if 'availability: "present"' in prov else 'catalog-only'))
deep.sort(reverse=True)
print(len(deep), 'sources deeper than 8;', sum(d[2] == 'recipe' for d in deep), 'have an AM recipe:')
print([f'{n}@{p}' for p, n, k in deep if k == 'recipe'])
