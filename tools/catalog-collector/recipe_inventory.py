"""Static recipe-family/enrollment discovery. Never evaluates shell or uses HTTP.

Run from any directory: python3 /path/to/recipe_inventory.py [--output REPORT.json].
Markers and normalized text fingerprints are review aids, not migration approval.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
ARCHES = ('x86_64', 'aarch64', 'i686', 'armv7l')
MANIFEST = 'docs/track/release-catalog/design/staged-manifest.json'
API = re.compile(r'https://api[.]github[.]com[^\s|<>;]*')
UNPACK = re.compile(r'(?:^|[;&|]\s*|\$\(\s*|(?:then|do)\s+)(?:tar|unzip|7z|7zz)\s+', re.M)


def requests(lines):
    """Same conservative token rules as catalog-probe/inventory.awk."""
    found = []
    for number, line in enumerate(lines, 1):
        if line.lstrip().startswith('#'):
            continue
        for match in API.finditer(line):
            url = match.group().replace('"', '').replace("'", '').rstrip(')')
            kind = 'other'
            if re.search(r'[$`\\]', url):
                kind = 'dynamic'
            elif '/REPLACETHIS/' in url:
                kind = 'placeholder'
            elif re.fullmatch(r'https://api[.]github[.]com/(?:repos/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+|repositories/[0-9]+)/releases(?:\?[^\s]*)?', url):
                kind = 'release-list'
            elif re.fullmatch(r'https://api[.]github[.]com/(?:repos/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+|repositories/[0-9]+)/releases/latest(?:\?[^\s]*)?', url):
                kind = 'release-latest'
            elif '/releases/tags/' in url:
                kind = 'release-tag'
            found.append({'line': number, 'url': url, 'kind': kind})
    return found


def recipe(path):
    raw = path.read_bytes()
    lines = raw.decode().splitlines()
    code = [line.strip() for line in lines if line.strip() and not line.lstrip().startswith('#')]
    text = '\n'.join(code)
    appimage = '--appimage-extract' in text
    unpack = bool(UNPACK.search(text))
    plain = 'mv ./tmp/* ./"$APP"' in text and 'chmod a+x' in text
    shared = '# AM-CATALOG-RECIPE 1' in lines
    family = ('shared-appimage' if shared else
              'appimage-with-unpack-marker' if appimage and unpack else
              'appimage' if appimage else
              'archive-unpack' if unpack else
              'plain-executable' if plain else 'other-custom')
    versions = [line for line in code if line.startswith('version=')]
    normalized = '\n'.join(
        'APP=<identity>' if line.startswith('APP=') else
        'SITE=<repository>' if line.startswith('SITE=') else
        'version=<selector>' if line.startswith('version=') else line
        for line in code)
    return {'path': str(path.relative_to(ROOT)), 'arch': path.parent.name,
            'lines': len(lines), 'bytes': len(raw), 'family': family,
            'fingerprint': hashlib.sha256(normalized.encode()).hexdigest(),
            'requests': requests(lines), 'version_lines': len(versions),
            'version_lines_differ': len(set(versions)) > 1,
            'alternate_updater': 'appimageupdatetool' in text,
            'literal_proxy': 'api.gh.pkgforge.dev' in text}, raw


def build():
    manifest = (ROOT/MANIFEST).read_bytes()
    sources = json.loads(manifest)['sources']
    aliases = {alias: source['name'] for source in sources
               for alias in [source['url'], *source['aliases']]}
    rows = []
    digest = hashlib.sha256()
    for arch in ARCHES:
        for path in sorted((ROOT/'programs'/arch).iterdir()):
            if not path.is_file():
                continue
            row, raw = recipe(path)
            digest.update(row['path'].encode()+b'\0'+raw+b'\0')
            urls = {r['url'] for r in row['requests']}
            row['coverage'] = ('no-api-token' if not urls else
                               'exact-covered' if urls <= aliases.keys() else
                               'partial' if urls & aliases.keys() else 'unenrolled-or-unresolved')
            rows.append(row)
    groups = defaultdict(list)
    for row in rows:
        groups[row['fingerprint']].append(row)
    top = sorted(groups.items(), key=lambda item: (-len(item[1]), item[0]))
    top_appimage = {key for key, group in top if group[0]['family'] == 'appimage'}
    # Largest two common AppImage fingerprints, not every extraction marker.
    largest = [key for key, group in top if key in top_appimage][:2]
    utilities = [row for row in rows if row['family'] == 'plain-executable'
                 and {req['url'] for req in row['requests']} ==
                 {'https://api.github.com/repos/ivan-hc/am-utils/releases'}]
    exact = [row for row in rows if row['coverage'] in ('exact-covered', 'partial')]
    # A concrete review queue: 50 literal endpoints from the largest common
    # x86_64 AppImage families. Include every matching architecture member.
    candidates = defaultdict(list)
    for row in rows:
        urls = {r['url'] for r in row['requests']}
        if (row['family'] == 'appimage' and row['fingerprint'] in largest
                and len(urls) == 1 and row['version_lines'] == 2
                and not row['version_lines_differ']
                and all(r['kind'] in ('release-list', 'release-latest') for r in row['requests'])
                and row['coverage'] == 'unenrolled-or-unresolved'):
            candidates[next(iter(urls))].append(row)
    selected = sorted(((url, group) for url, group in candidates.items()
                       if any(r['arch'] == 'x86_64' for r in group)),
                      key=lambda item: (-len(item[1]), item[0]))[:50]
    def counts(items, field):
        return dict(sorted(Counter(row[field] for row in items).items()))
    def compact(row):
        return {k: v for k, v in row.items() if k != 'requests'} | {
            'requests': row['requests']}
    return {
        'source_revision': subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,
            check=True,capture_output=True,text=True).stdout.strip(),
        'recipe_input_sha256': digest.hexdigest(),
        'manifest': MANIFEST, 'manifest_sha256': hashlib.sha256(manifest).hexdigest(),
        'inventory_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'method': 'static markers/text normalization; no shell expansion, recipe execution or HTTP',
        'normalization': 'strip blank/full-comment lines; replace APP=, SITE= and whole version= lines only',
        'recipes': len(rows), 'by_arch': {
            arch: {'recipes': len(items := [r for r in rows if r['arch'] == arch]),
                   'families': counts(items, 'family'), 'coverage': counts(items, 'coverage'),
                   'alternate_updater_files': sum(r['alternate_updater'] for r in items),
                   'literal_proxy_files': sum(r['literal_proxy'] for r in items),
                   'version_lines_differ_files': sum(r['version_lines_differ'] for r in items)}
            for arch in ARCHES},
        'families': counts(rows, 'family'), 'coverage': counts(rows, 'coverage'),
        'family_examples': {family: [r['path'] for r in rows if r['family'] == family][:8]
                            for family in sorted({r['family'] for r in rows})},
        'mixed_marker_fingerprints': [key for key, group in top
            if len({r['family'] for r in group}) > 1],
        'api_occurrences': len(occurrences := [req for r in rows for req in r['requests']]),
        'api_kinds': dict(sorted(Counter(r['kind'] for r in occurrences).items())),
        'distinct_literal_release_urls': len({r['url'] for r in occurrences
            if r['kind'] in ('release-list', 'release-latest', 'release-tag')}),
        'fingerprints': len(groups), 'largest_families': [
            {'fingerprint': key, 'recipes': len(group),
             'family': group[0]['family'], 'by_arch': counts(group, 'arch'),
             'examples': [r['path'] for r in group[:5]],
             'source_lines': sum(r['lines'] for r in group)} for key, group in top[:12]],
        'enrolled_aliases': [{ 'source': source['name'], 'fetch_url': source['url'],
            'aliases': source['aliases'], 'callers': [r['path'] for r in rows
                if any(req['url'] in [source['url'], *source['aliases']] for req in r['requests'])]}
            for source in sources],
        'covered_or_partial_recipes': [compact(r) for r in exact],
        'plain_utility_batch': [compact(r) for r in utilities],
        'batch_selection': '50 literal endpoints from largest two no-unpack AppImage fingerprints; most shared callers first then exact URL',
        'batch_family_fingerprints': largest,
        'candidate_pool': {'endpoints': len(candidates),
                           'recipes': sum(len(group) for group in candidates.values())},
        'proposed_enrollment_batch': [{'url': url,
            'recipes': [compact(r) for r in group]} for url, group in selected],
        'limitations': [
            'Lexical tokens include generated updater heredocs, conditional and dead code.',
            'Markers do not prove runtime format, selector correctness or shared lifecycle compatibility.',
            'Distinct exact URL strings remain distinct; no query, case or repository identity merging.',
            'Dynamic expressions and non-GitHub metadata are unresolved, not inferred.',
            'Proposed batch is an offline review queue, not an enrolled/approved collection list.',
            'Primary corpus is direct regular files in the four named architecture directories.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args=parser.parse_args()
    rendered=json.dumps(build(),indent=2,sort_keys=True)+'\n'
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered,end='')


if __name__ == '__main__':
    main()
