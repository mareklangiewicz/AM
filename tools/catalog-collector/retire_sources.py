"""Retire catalog sources: the explicit step that takes a source out of collection (ticket 21).

    python3 -B tools/catalog-collector/retire_sources.py RID ...           print what would change
    python3 -B tools/catalog-collector/retire_sources.py --write RID ...   rewrite the enrollment files

Each source's catalog-only rows leave collection-apps.json and its name moves
from `active` to `retired` in source-names.json, so it is never reused. The
next collection drops its documents from the published catalog; earlier
snapshots keep them. A source missing from enrollment without this step still
refuses there. A source a recipe still selects from refuses here: a
declaration, a recipe URL policy or an AppImage policy. A recipe that only
names its repository in a GitHub URL is a warning: the source retires, and
the warning says which recipe to look at (upstream renames apps, so a
catalog-only row may just need its app renamed instead). The files change;
nothing is committed.
"""
import argparse
import json
from pathlib import Path
import re
import sys

from recipe_declarations import recipe_rows, rows_json

ROOT = Path(__file__).resolve().parents[2]
FOLDER = 'tools/catalog-collector/'
APPS = FOLDER+'collection-apps.json'
NAMES = FOLDER+'source-names.json'
SELECTORS = (FOLDER+'recipe-url-policies.json', FOLDER+'appimage-policies.json')
ARCHES = ('x86_64', 'aarch64', 'i686', 'armv7l')


class Refused(ValueError):
    pass


def names_json(registry):
    return json.dumps(registry, indent=2)+'\n'


def read(root, path):
    return json.loads((root/path).read_text(encoding='utf-8'))


def retire(root, rids):
    """{path: new text} of the enrollment files with these sources retired."""
    rids = [str(rid) for rid in rids]
    registry = read(root, NAMES)
    for rid in rids:
        if rids.count(rid) > 1:
            raise Refused('named twice: '+rid)
        if rid not in registry['active']:
            raise Refused('not an active source: '+rid)
    selectors = [row for path in SELECTORS for row in read(root, path)]+recipe_rows(root)
    for row in selectors:
        if str(row['repository_id']) in rids:
            raise Refused('source '+str(row['repository_id'])+' is still selected by '+row['recipe'])
    before = read(root, APPS)
    apps = [row for row in before if str(row['repository_id']) not in rids]
    retired = registry['retired']+[registry['active'][rid] for rid in rids]
    active = {rid: name for rid, name in registry['active'].items() if rid not in rids}
    return {APPS: rows_json(apps), NAMES: names_json(dict(active=active, retired=retired))}


def still_named(root, rids):
    """Warnings for retiring sources a recipe still names in a GitHub URL."""
    rids = [str(rid) for rid in rids]
    repositories = {row['repository'].lower(): str(row['repository_id']) for row in read(root, APPS)
                    if str(row['repository_id']) in rids}
    if not repositories:
        return []
    named = re.compile(r'github\.com/(?:repos/)?('+'|'.join(map(re.escape, repositories))+r')(?![A-Za-z0-9_.-])')
    warnings = []
    for path in sorted(path for arch in ARCHES for path in (root/'programs'/arch).glob('*') if path.is_file()):
        found = named.search(path.read_text(encoding='utf-8', errors='replace').lower())
        if found:
            warnings.append('source '+repositories[found[1]]+' '+found[1]+' is still named by '
                            + str(path.relative_to(root)))
    return warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('rids', nargs='+', type=int, metavar='RID')
    parser.add_argument('--write', action='store_true', help='rewrite the files (default: only print)')
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        files = retire(args.root, args.rids)
    except Refused as refusal:
        print('refused: '+str(refusal), file=sys.stderr)
        return 2
    for warning in still_named(args.root, args.rids):
        print('warning: '+warning, file=sys.stderr)
    registry = read(args.root, NAMES)
    before = read(args.root, APPS)
    for rid in map(str, args.rids):
        apps = [row['app'] for row in before if str(row['repository_id']) == rid]
        print(rid+' '+registry['active'][rid]+': '+str(len(apps))+' catalog-only rows ('+', '.join(apps[:5])
              + (', ...' if len(apps) > 5 else '')+')')
    if args.write:
        for path, text in files.items():
            (args.root/path).write_text(text, encoding='utf-8')
    print(('wrote ' if args.write else 'would write ')+', '.join(sorted(files)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
