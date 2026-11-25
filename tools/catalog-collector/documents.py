"""catalog/ documents from what the collector read, and their exact bytes.

The schema (schemas/catalog.schema.yaml) gives field order, the derived
defaults this module leaves out, and the grammar encode() writes
(docs/catalog-format.md). Both readers accept everything encode() returns
for a document the schema accepts.
"""
from datetime import datetime
import json
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT/'tools/recipe-reconstruction') not in sys.path:
    sys.path.insert(0, str(ROOT/'tools/recipe-reconstruction'))
DEFS = yaml.safe_load((ROOT/'schemas/catalog.schema.yaml').read_text())['$defs']
PLATFORMS = json.loads((ROOT/'tools/catalog-contract/platforms.json').read_text())
NEWEST_TAGS = 8
ESCAPES = {'"': '\\"', '\\': '\\\\', '\n': '\\n', '\r': '\\r', '\t': '\\t',
           '\u0085': '\\N', ' ': '\\L', ' ': '\\P'}


def quote(text):
    return '"'+''.join(ESCAPES.get(c, c) for c in text)+'"'


def _resolve(rule):
    return DEFS[rule['$ref'].removeprefix('#/$defs/')] if '$ref' in rule else rule


def _key_order(pattern, key):
    if pattern == '^[1-9][0-9]*$':
        return (int(key),)
    if pattern == '^[1-9][0-9]*-[1-9][0-9]*$':
        return tuple(map(int, key.split('-')))
    return (key.encode(),)


def _lines(value, rule, depth, out):
    rule = _resolve(rule)
    pad = '  '*depth
    if rule.get('properties'):
        items = [(name, value[name], sub, False) for name, sub in rule['properties'].items() if name in value]
        unknown = set(value)-set(rule['properties'])
        if unknown:
            raise ValueError(f'fields outside the schema: {sorted(unknown)}')
    else:
        (pattern, sub), = rule['patternProperties'].items()
        items = [(key, value[key], sub, True) for key in sorted(value, key=lambda k: _key_order(pattern, k))]
    for name, item, sub, quoted in items:
        head = pad+(quote(name) if quoted else name)+':'
        if isinstance(item, dict):
            if item:
                out.append(head)
                _lines(item, sub, depth+1, out)
            else:
                out.append(head+' {}')
        elif isinstance(item, bool):
            out.append(head+(' true' if item else ' false'))
        elif isinstance(item, int):
            out.append(f'{head} {item}')
        elif isinstance(item, str):
            out.append(head+' '+quote(item))
        else:
            raise ValueError(f'{name}: not a catalog value')


def encode(kind, document):
    """The exact bytes of one document of this kind; $schema is added here."""
    document = dict(document, **{'$schema': DEFS[kind]['properties']['$schema']['const']})
    out = []
    _lines(document, DEFS[kind], 0, out)
    return ('\n'.join(out)+'\n').encode('utf-8')


def _release(record, repository):
    tag = record['tag']
    fact = dict(tag=tag)
    if record.get('title', tag) != tag:
        fact['title'] = record['title']
    if record['url'] != f'https://github.com/{repository}/releases/tag/{tag}':
        fact['url'] = record['url']
    fact['published_at'] = record['published_at']
    fact['prerelease'] = record['prerelease']
    for field, kind in (('source_zip_url', 'zipball'), ('source_tar_url', 'tarball')):
        if field in record and record[field] != f'https://api.github.com/repos/{repository}/{kind}/{tag}':
            fact[field] = record[field]
    fact['assets'] = {}
    for aid, asset in record['assets'].items():
        item = dict(name=asset['name'])
        if asset['url'] != f'https://github.com/{repository}/releases/download/{tag}/{asset["name"]}':
            item['url'] = asset['url']
        item['size'] = asset['size']
        digest = asset.get('digest', '')
        if digest.startswith('sha256:'):
            item['sha256pre'] = digest[len('sha256:'):][:16]
        fact['assets'][aid] = item
    return fact


def repository(previous, acquired, *, repository_id, repository):
    """The repository document after one successful read.

    A release of the previous document that this read did not return is kept
    with its last-seen time, unless the read reached the end of the release
    list: then GitHub deleted it, and only Git history keeps it.
    """
    releases = {rid: _release(record, repository) for rid, record in acquired['releases'].items()}
    if previous and not acquired['history_complete']:
        for rid, kept in previous['releases'].items():
            if rid not in releases:
                releases[rid] = dict(kept, observed_at=kept.get('observed_at', previous['observed_at']))
    document = dict(repository_id=repository_id, repository=repository,
                    observed_at=acquired['received_at'], history_complete=acquired['history_complete'],
                    releases=retained(releases))
    if 'git_refs' in acquired:
        document.update(git_scope=acquired['git_scope'], git_refs=acquired['git_refs'])
    return document


def failed(previous, *, failed_at, failed_with, repository_id, repository):
    """The repository document after a read that failed: the previous facts
    stay as they were, with this failure added; a never-collected repository
    gets only its failure."""
    document = dict(previous or dict(releases={}), repository_id=repository_id, repository=repository)
    document.update(failed_at=failed_at, failed_with=failed_with)
    return document


def appimages(release):
    """The processor types (architecture() guesses, None for none) of a release's .AppImage files."""
    return {architecture(a['name']) for a in release['assets'].values() if a['name'].lower().endswith('.appimage')}


def retained(releases):
    """The releases retention keeps, counted as tags: the 8 newest tags, the
    newest stable tag, the newest tag with a Linux download and, for each
    guessed processor type, the newest tag with an AppImage of it (Marek,
    November 25, 2026: AppImages are what AM installs), with every release
    under a kept tag (twins stay together). Newest is by published_at, then
    release ID."""
    newest = sorted(releases, key=lambda rid: (releases[rid]['published_at'], int(rid)), reverse=True)
    tags = list(dict.fromkeys(releases[rid]['tag'] for rid in newest))
    kept = set(tags[:NEWEST_TAGS])
    arches = {arch for rid in newest for arch in appimages(releases[rid])}
    wants = [lambda r: not r['prerelease'], lambda r: any(linux(a['name']) for a in r['assets'].values())]
    wants += [lambda r, arch=arch: arch in appimages(r) for arch in arches]
    for wanted in wants:
        first = next((releases[rid]['tag'] for rid in newest if wanted(releases[rid])), None)
        if first is not None:
            kept.add(first)
    return {rid: release for rid, release in releases.items() if release['tag'] in kept}



def linux(name):
    """The page's guess (platforms.json): does this file name look like a Linux download?"""
    lowered = name.lower()
    return any(word in lowered for word in PLATFORMS['linux'])


def architecture(name):
    """The page's guess (platforms.json): the processor a file name names, or None."""
    lowered = name.lower()
    for arch, words in PLATFORMS['architectures'].items():
        if any(word in lowered for word in words):
            return arch
    return None


ARCHITECTURES = ('x86_64', 'aarch64', 'i686', 'armv7l')


def recipe_label(text, app, repository_id):
    """declaration: the recipe is a short declaration of this app installing
    from this repository, which AM's reviewed installer runs. script: any
    other recipe, to read before installing. Never evaluates shell."""
    from reconstruct import from_short, TEMPLATE
    try:
        declaration = from_short(text, TEMPLATE)
    except (ValueError, KeyError):
        return 'script'
    declared = re.search(r'^CATALOG_REPOSITORY_ID=([1-9][0-9]*)$', text, re.M)
    if declaration['app'] == app and declared and int(declared[1]) == repository_id:
        return 'declaration'
    return 'script'


def apps(rows, names, *, root=ROOT):
    """apps.yaml: each enrolled app's repository file, by the source name the
    registry allocated, and a label for each architecture AM has a recipe for."""
    entries = {}
    for row in rows:
        app = row['app']
        entry = dict(repository=f'repositories/{names[str(row["repository_id"])]}.yaml')
        for arch in ARCHITECTURES:
            path = Path(root)/'programs'/arch/app
            if path.is_file():
                try:
                    text = path.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    entry[arch] = 'script'
                    continue
                entry[arch] = recipe_label(text, app, row['repository_id'])
        entries[app] = entry
    return dict(apps=entries)


RUNS_KEPT = 64


def runs(previous, *, run_id, attempt, summary):
    """status/runs.yaml with this run's summary added, the oldest dropped past 64."""
    entries = dict(previous['runs']) if previous else {}
    entries[f'{run_id}-{attempt}'] = summary
    order = sorted(entries, key=lambda key: tuple(map(int, key.split('-'))))
    return dict(runs={key: entries[key] for key in order[-RUNS_KEPT:]})


def statistics(repositories, *, measured_at):
    """status/statistics.yaml: repositories by the age of their observed_at."""
    parse = lambda t: datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ')
    now = parse(measured_at)
    counts = dict(under_24h=0, from_24_to_48h=0, from_48h_to_14d=0, over_14d=0, never_collected=0)
    for repository in repositories:
        if 'observed_at' not in repository:
            counts['never_collected'] += 1
            continue
        hours = (now-parse(repository['observed_at'])).total_seconds()/3600
        bucket = 'under_24h' if hours < 24 else 'from_24_to_48h' if hours <= 48 else 'from_48h_to_14d' if hours <= 14*24 else 'over_14d'
        counts[bucket] += 1
    return dict(measured_at=measured_at, **counts)
