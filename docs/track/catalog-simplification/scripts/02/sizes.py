"""Attribute catalog repository bytes to fields, by raw YAML line (indent = nesting level)."""
import collections, pathlib, re, sys, statistics

root = pathlib.Path(sys.argv[1])
by_field = collections.Counter()
releases_per_src, assets_per_rel, src_bytes = [], [], []
big = []
key_re = re.compile(r'^( *)("?)([^":]+)\2:')
for path in sorted(root.glob('*.yaml')):
    raw = path.read_text()
    src_bytes.append(len(raw.encode()))
    stack = []
    n_rel = 0; n_assets = 0
    for line in raw.splitlines(True):
        m = key_re.match(line)
        if not m:
            by_field['(other)'] += len(line.encode()); continue
        depth = len(m.group(1)) // 2
        key = m.group(3)
        stack = stack[:depth] + [key]
        # Normalise ids to placeholders.
        norm = ['<id>' if re.fullmatch(r'[0-9]+', k) else k for k in stack]
        if norm[:2] == ['releases', '<id>'] and len(norm) == 2: n_rel += 1
        if len(norm) == 4 and norm[2] == 'assets': n_assets += 1
        label = '/'.join(norm[:6])
        by_field[label] += len(line.encode())
    releases_per_src.append(n_rel)
    big.append((len(raw.encode()), path.name, n_rel, n_assets))

total = sum(by_field.values())
print(f'total {total/1e6:.1f} MB in {len(src_bytes)} files')
# Roll up: leaf fields only.
print('\n-- bytes by field (incl. key, indent, value) --')
for label, n in by_field.most_common(30):
    print(f'{n/1e6:8.1f} MB {100*n/total:5.1f}%  {label}')
print('\n-- releases per source --')
q = statistics.quantiles(releases_per_src, n=10)
print('median', statistics.median(releases_per_src), 'deciles', [round(x) for x in q], 'max', max(releases_per_src))
big.sort(reverse=True)
print('\n-- largest 10 sources (bytes, name, releases, assets) --')
for row in big[:10]: print(row)
top = sum(b for b, *_ in big[:100])
print(f'top 100 sources = {top/1e6:.1f} MB ({100*top/total:.0f}%)')
