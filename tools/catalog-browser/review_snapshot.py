#!/usr/bin/env python3
"""Prepare a static browser-review snapshot from exact saved public observations.

Does not acquire releases or publish catalog refs. Reuses the accepted converter,
including source-isolated refusal of tied exact-tag evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/catalog-collector'))
import contracts as c
from incremental import decode
from rehearse_pipeline import seed_source
from publication import git


def build(repo, baseline, revision, destination):
    c.pin(baseline)
    c.pin(revision)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    names = json.loads((ROOT / 'tools/catalog-collector/source-names.json').read_text())['active']
    raw_apps = git(repo, 'show', baseline + ':apps.yaml')
    apps = decode('apps.yaml', raw_apps, 'format-2')[0]['apps']
    tree = {}
    refused = []
    for rid in sorted(set(apps.values()), key=int):
        path = f'repositories/{rid}.yaml'
        original = decode(path, git(repo, 'show', baseline + ':' + path), 'format-2')[0]
        try:
            converted = seed_source(original, revision)
        except ValueError as error:
            if str(error) != 'same_tag_conflict':
                raise
            refused.append(str(rid))
            continue
        tree['repositories/' + names[str(rid)] + '.yaml'] = c.encode(converted)
    mapped = {app: 'repositories/' + names[str(rid)] + '.yaml' for app, rid in apps.items()
              if 'repositories/' + names[str(rid)] + '.yaml' in tree}
    tree['apps.yaml'] = c.encode(dict(c.header('apps', revision), apps=mapped))
    tree.update(c.partition_provenance(mapped, {
        app: {arch: dict(repository_id=apps[app], availability='unknown', classification='unknown')
              for arch in ('aarch64', 'armv7l', 'i686', 'x86_64')} for app in mapped}, revision))
    tree['catalog.yaml'] = c.encode(dict(c.header('catalog', revision),
        inputs={key: revision for key in ('source', 'policy', 'recipes', 'rules', 'schemas')},
        producer=dict(id=1, attempt=1), retention='32-plus-stable-exact-tag-v1'))
    c.validate_tree(tree)
    hashes = {path: hashlib.sha256(raw).hexdigest() for path, raw in sorted(tree.items())}
    # A content identity, explicitly not a catalog Git commit.
    identity = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()[:40]
    for path, raw in tree.items():
        target = destination / identity / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    metadata = dict(pin=identity, baseline=baseline, source=revision,
                    sources=sum(path.startswith('repositories/') for path in tree), apps=len(mapped), refused=refused,
                    label='Review snapshot · saved observations', document_sha256=hashes)
    (destination / 'review.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps({k: v for k, v in metadata.items() if k != 'document_sha256'}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--source', required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    build(args.repo, args.baseline, args.source, args.destination)
