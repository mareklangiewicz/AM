"""Ticket 25: which facts in the JSON files under tools/ exist nowhere else.

    python3 -B docs/track/catalog-simplification/scripts/25/measure.py   (from the repository root)
"""
import ast
import json
from pathlib import Path
import re
import subprocess

COLLECTOR = Path('tools/catalog-collector')


def collector_modules(name='catalog_run', seen=None):
    """The collector modules catalog_run.py imports, transitively."""
    seen = set() if seen is None else seen
    path = COLLECTOR/(name+'.py')
    if name in seen or not path.exists():
        return seen
    seen.add(name)
    for node in ast.walk(ast.parse(path.read_text())):
        names = [a.name for a in node.names] if isinstance(node, ast.Import) else \
            [node.module] if isinstance(node, ast.ImportFrom) and node.module else []
        for each in names:
            collector_modules(each.split('.')[0], seen)
    return seen


def main():
    files = subprocess.run(['git', 'ls-files', '*.json'], capture_output=True, text=True, check=True).stdout.split()
    files = [f for f in files if not f.startswith('docs/')]
    print('JSON files outside docs/:')
    for f in sorted(files, key=lambda f: Path(f).stat().st_size):
        print(f'  {Path(f).stat().st_size:>8}  {f}')

    modules = sorted(collector_modules())
    loaded = set()
    for m in modules:
        loaded |= set(re.findall(r'[a-z_-]+\.json', (COLLECTOR/(m+'.py')).read_text()))
    print('collector modules:', ' '.join(modules))
    print('JSON names they mention:', ' '.join(sorted(loaded)))

    repos = {}
    for path in Path('catalog/repositories').glob('*.yaml'):
        found = re.search(r'^repository_id: (\d+)$', path.read_text(), re.M)
        repos[path.stem] = found.group(1) if found else None
    names = json.loads((COLLECTOR/'source-names.json').read_text())
    active = names['active']
    print(f"source-names.json: {len(active)} active, {len(names['retired'])} retired;",
          sum(repos.get(name) == rid for rid, name in active.items()), 'active rows equal a catalog file\'s name and id')

    apps = set(re.findall(r'^  "([^"]+)":$', Path('catalog/apps.yaml').read_text(), re.M))
    rows = json.loads((COLLECTOR/'collection-apps.json').read_text())
    by_id = {rid: name for rid, name in active.items()}
    print(f'collection-apps.json: {len(rows)} rows,', sum(r['app'] in apps for r in rows), 'apps in catalog/apps.yaml,',
          sum(str(r['repository_id']) in by_id for r in rows), 'repositories named in source-names.json')

    for name in ('recipe-url-policies.json', 'appimage-policies.json'):
        rows = json.loads((COLLECTOR/name).read_text())
        print(f'{name}: {len(rows)} rows, {sum("source_sha256" in r for r in rows)} carry their recipe\'s sha256')
    print('git-sources.json:', len(json.loads((COLLECTOR/'git-sources.json').read_text())), 'repositories')

    programs = Path('programs/x86_64')
    inline = sum('catalog-yaml.am' in p.read_text(errors='replace') for p in programs.iterdir() if p.is_file())
    print('programs/x86_64 scripts calling catalog-yaml.am (inline form):', inline)


if __name__ == '__main__':
    main()
