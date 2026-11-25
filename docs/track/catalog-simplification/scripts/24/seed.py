"""Seed catalog/ once from the tip of release-catalog-v3 (ticket 24 part 4).

    python3 -B docs/track/catalog-simplification/scripts/24/seed.py [--ref REF] --output DIR

Run once for the cutover commit; never maintained. Reads the v3 repository
documents with a plain YAML loader (the v3 modules are deleted in part 5) and
writes them through the collector's own documents.py, so seeded files are
byte-for-byte what a collection would write:

- releases keep their facts; derived URLs, titles equal to the tag,
  media types, updated_at and created_at go; digests become sha256pre;
- a release's own observed_at (last seen) is kept; collected_at goes;
- retention becomes the tag-counted rule (8 newest, newest stable, newest
  with Linux);
- failure fields are kept, except same_tag_conflict, which the new contract
  does not have: those repositories (never collected in v3, all twins) are
  left out, so the first collection reads them fresh;
- Git refs are keyed by name.

apps.yaml and status/statistics.yaml are built from the current enrollment,
as the collector builds them; status/runs.yaml starts empty.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

import yaml

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT/'tools/catalog-collector'))
import documents  # noqa: E402
import host_catalog  # noqa: E402

LOADER = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)
RETIRED_FAILURE = 'same_tag_conflict'


def expanded_release(release):
    """A v3 release as bounded.normalize returns it: full URLs, the digest."""
    record = dict(tag=release['tag'], title=release.get('title', release['tag']), url=release['url'],
                  published_at=release.get('published_at', release.get('created_at')), prerelease=release['prerelease'])
    for field in ('source_zip_url', 'source_tar_url'):
        if field in release:
            record[field] = release[field]
    record['assets'] = {}
    for aid, asset in release['assets'].items():
        url = asset['url'] if 'url' in asset else release['download_base']+asset['url_suffix']
        item = dict(name=asset['name'], url=url, size=asset['size'])
        if 'digest' in asset:
            item['digest'] = asset['digest']
        record['assets'][aid] = item
    return record


def convert(v3):
    """The new repository document for one v3 repository document; None to leave it out."""
    if v3.get('failed_with') == RETIRED_FAILURE:
        return None
    rid, repository = v3['repository_id'], v3['repository']
    if 'observed_at' not in v3:
        return documents.failed(None, failed_at=v3['failed_at'], failed_with=v3['failed_with'],
                                repository_id=rid, repository=repository)
    releases = {}
    for key, release in v3['releases'].items():
        fact = documents._release(expanded_release(release), repository)
        if 'observed_at' in release:
            fact['observed_at'] = release['observed_at']
        releases[key] = fact
    document = dict(repository_id=rid, repository=repository, observed_at=v3['observed_at'],
                    history_complete=v3['scope']['history_complete'], releases=documents.retained(releases))
    if 'git_refs' in v3:
        document.update(documents._git(v3))
    if 'failed_at' in v3:
        document.update(failed_at=v3['failed_at'], failed_with=v3['failed_with'])
    return document


def v3_documents(ref):
    """repositories/*.yaml at ref, as loaded YAML, by file name."""
    archive = subprocess.run(['git', '-C', str(ROOT), 'archive', ref, 'repositories'], check=True, capture_output=True).stdout
    result = {}
    with tempfile.TemporaryFile() as raw:
        raw.write(archive)
        raw.seek(0)
        with tarfile.open(fileobj=raw) as tar:
            for member in tar.getmembers():
                if member.isfile() and member.name.endswith('.yaml'):
                    result[Path(member.name).name] = yaml.load(tar.extractfile(member).read(), Loader=LOADER)
    return result


def seed(ref, output, *, root=ROOT, measured_at=None):
    output = Path(output)
    counts = dict(converted=0, never_collected=0, left_out=0, releases_before=0, releases_after=0)
    tree = {}
    for name, v3 in sorted(v3_documents(ref).items()):
        document = convert(v3)
        if document is None:
            counts['left_out'] += 1
            continue
        counts['converted'] += 1
        counts['never_collected'] += 'observed_at' not in document
        counts['releases_before'] += len(v3['releases'])
        counts['releases_after'] += len(document['releases'])
        tree[f'repositories/{name}'] = documents.encode('repository', document)
    rows, _ = host_catalog.configuration(root=root)
    names = json.loads((Path(root)/'tools/catalog-collector/source-names.json').read_text())['active']
    tree['apps.yaml'] = documents.encode('apps', documents.apps(rows, names, root=root))
    scanned = [yaml.load(raw, Loader=LOADER) for path, raw in tree.items() if path.startswith('repositories/')]
    now = measured_at or datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    tree['status/statistics.yaml'] = documents.encode('statistics', documents.statistics(scanned, measured_at=now))
    tree['status/runs.yaml'] = documents.encode('runs', dict(runs={}))
    for path, raw in tree.items():
        target = output/path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    counts['bytes'] = sum(map(len, tree.values()))
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--ref', default='origin/release-catalog-v3')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        raise SystemExit(f'{args.output} is not empty')
    print(json.dumps(seed(args.ref, args.output), indent=1))


if __name__ == '__main__':
    main()
