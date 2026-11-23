"""How well does an asset's file extension predict its stored media type?"""
import collections, pathlib, re, sys
KEY = re.compile(r'^( *)"?([^":]+)"?: ?"?(.*?)"?$')
pairs = []
for path in pathlib.Path(sys.argv[1]).glob('*.yaml'):
    name = None; asset = False; inrel = False
    for line in path.read_text().splitlines():
        m = KEY.match(line)
        if not m: continue
        ind, key, val = len(m.group(1)), m.group(2), m.group(3)
        if ind == 0: inrel = key == 'releases'
        if not inrel: continue
        if ind == 6: 
            if asset: pairs.append((name, mt))
            asset = True; name = None; mt = '(octet-stream)'
        elif ind == 8 and key == 'name': name = val
        elif ind == 8 and key == 'media_type': mt = val
        elif ind < 6 and asset: pairs.append((name, mt)); asset = False
    if asset: pairs.append((name, mt))
def ext(n):
    n = n.lower()
    m = re.search(r'(\.tar\.(gz|xz|zst|bz2)|\.[a-z0-9]{1,10})$', n)
    return m.group(1) if m else '(none)'
by = collections.defaultdict(collections.Counter)
for n, mt in pairs:
    if n is None: continue
    by[ext(n)][mt] += 1
total = len(pairs); hit = sum(c.most_common(1)[0][1] for c in by.values())
print(f'{total} assets, {len(by)} extensions; per-extension most common type matches {hit} ({100*hit/total:.1f}%)')
# Table size needed: extensions covering 99% of assets
rows = sorted(by.items(), key=lambda kv: -sum(kv[1].values()))
acc = 0
for i, (e, c) in enumerate(rows, 1):
    acc += sum(c.values())
    if acc >= 0.99 * total: print(f'{i} extensions cover 99% of assets'); break
print('top extensions: ext count -> most common type (share), runner-up')
for e, c in rows[:22]:
    n = sum(c.values()); (t1, n1), *rest = c.most_common(2)
    print(f'  {e:12} {n:8}  {t1} ({100*n1/n:.0f}%)' + (f', {rest[0][0]} ({100*rest[0][1]/n:.0f}%)' if rest else ''))
