"""Measure candidate size reductions over format-3 repository documents, line-based (no YAML parse)."""
import collections, pathlib, re, sys, urllib.parse

root = pathlib.Path(sys.argv[1])
c = collections.Counter()
kind_n, kind_b = collections.Counter(), collections.Counter()
keep = dict.fromkeys((1, 3, 8, 16, 32), 0)
total_rel = 0
KEY = re.compile(r'^( *)"?([^":]+)"?: ?(.*)$')

def unq(v):
    return v[1:-1].encode().decode('unicode_escape') if v.startswith('"') else v

def kind(name):
    n = name.lower()
    if re.search(r'\.(sha\d*|sha\d+sum|md5|asc|sig|minisig|sbom|spdx|intoto|jsonl?|txt|pem|cert|zsync|blockmap|yml|yaml)$|checksums?|sbom', n): return 'checksum/sig/meta'
    if re.search(r'\.(exe|msi|msix|appx|nupkg)$|windows|win32|win64|[-_.]win[-_.]', n): return 'windows'
    if re.search(r'\.(dmg|pkg)$|darwin|macos|osx|apple', n): return 'mac'
    if re.search(r'appimage|linux|\.deb$|\.rpm$|\.flatpak|\.snap$|musl|gnu', n): return 'linux'
    return 'other (incl. bare tarballs)'

for path in root.glob('*.yaml'):
    lines = path.read_bytes().decode().splitlines(True)
    repo = ''
    rels = []  # [when, rid, bytes, fields{}, assets[]]
    cur = asset = None
    in_rel = False
    for line in lines:
        m = KEY.match(line)
        if not m:
            if cur: cur[2] += len(line.encode())
            continue
        ind, key, val = len(m.group(1)), m.group(2), m.group(3)
        if ind == 0:
            in_rel = key == 'releases'; cur = None
            if key == 'repository': repo = unq(val)
            continue
        if not in_rel: continue
        if ind == 2:
            cur = ['', key, 0, {}, []]; rels.append(cur)
        elif ind == 4: cur[3][key] = unq(val) if val else ''
        elif ind == 6: asset = {}; cur[4].append(asset)
        elif ind == 8: asset[key] = unq(val)
        cur[2] += len(line.encode())
        if ind == 8:
            asset.setdefault('_bytes', 0)
        if ind >= 6 and asset is not None: asset['_bytes'] = asset.get('_bytes', 0) + len(line.encode())
    for r in rels:
        f = r[3]; r[0] = f.get('published_at') or f.get('created_at', '')
        tag = f.get('tag', ''); q = urllib.parse.quote(tag, safe='')
        c['releases'] += 1
        c['title_is_tag'] += f.get('title') == tag
        c['url_default'] += f.get('url') in (f'https://github.com/{repo}/releases/tag/{tag}', f'https://github.com/{repo}/releases/tag/{q}')
        c['zip_default'] += f.get('source_zip_url') == f'https://api.github.com/repos/{repo}/zipball/{tag}'
        c['tar_default'] += f.get('source_tar_url') == f'https://api.github.com/repos/{repo}/tarball/{tag}'
        c['has_base'] += 'download_base' in f
        c['base_default'] += f.get('download_base') in (f'https://github.com/{repo}/releases/download/{tag}/', f'https://github.com/{repo}/releases/download/{q}/')
        c['updated_differs'] += f.get('updated_at') not in (None, f.get('published_at'))
        for a in r[4]:
            c['assets'] += 1
            s = a.get('url_suffix')
            c['suffix_is_name'] += s == a.get('name')
            c['suffix_is_quoted_name'] += s is not None and s != a.get('name') and s == urllib.parse.quote(a.get('name', ''))
            c['no_digest'] += 'digest' not in a
            c['no_media_type'] += 'media_type' not in a
            k = kind(a.get('name', '')); kind_n[k] += 1; kind_b[k] += a.get('_bytes', 0)
    rels.sort(key=lambda r: (r[0], int(r[1])), reverse=True)
    sizes = [r[2] for r in rels]; total_rel += sum(sizes)
    for n in keep: keep[n] += sum(sizes[:n])

print(dict(c))
print('assets by kind (count, MB):')
for k, n in kind_n.most_common(): print(f'  {k:28} {n:8}  {kind_b[k]/1e6:6.1f} MB')
print(f'release bytes {total_rel/1e6:.1f} MB; keeping only N newest per source:')
for n, b in keep.items(): print(f'  N={n:2}: {b/1e6:6.1f} MB ({100*b/total_rel:4.0f}%)')
