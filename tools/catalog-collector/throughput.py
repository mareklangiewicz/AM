"""Offline acquisition queue and capacity audit; never enrolls or fetches sources.

Cohorts are evidence work units, NOT replacement publication manifests. Repository
identity groups stay together so a later evidence runner can reuse one identity
response for both releases and releases/latest without broadening aliases.
"""
import argparse
import hashlib
import json
from pathlib import Path

from collector import BODY_CAP, SOURCE_CAP, Descriptor, require
from storage import TREE_CAP, canonical


def audit(payload_raw, manifest_raw, read_recipe):
    """Bind a complete queue to exact payload, manifest and current recipe bytes."""
    payload = json.loads(payload_raw)
    manifest = json.loads(manifest_raw)
    rows = payload['rows']
    identities, aliases, paths = {}, set(), set()
    for row in rows:
        alias, identity = row['alias'], row['identity_request']
        require(alias not in aliases and alias in (identity+'/releases',
                                                   identity+'/releases/latest'), 'queue_alias')
        Descriptor(alias).validate(1)  # lexical validation only, no identity claim
        aliases.add(alias)
        identities.setdefault(identity, []).append(row)
        for recipe in row['recipes']:
            path = recipe['path']
            require(path not in paths and path.startswith('programs/') and
                    len(path.split('/')) == 3 and '..' not in path.split('/'), 'queue_path')
            paths.add(path)
            require(hashlib.sha256(read_recipe(path)).hexdigest() == recipe['sha256'],
                    'recipe_changed')
    require(len(rows) == payload['candidate_endpoints'] and
            len(paths) == payload['candidate_recipes'] and
            sorted(identities) == payload['identity_requests'], 'queue_counts')
    require(not aliases.intersection(a for row in manifest['sources']
                                    for a in (row['url'], *row['aliases'])), 'already_enrolled')

    cohorts, current = [], []
    # Preserve frozen shared-caller-first priority and never split an identity.
    for group in identities.values():
        require(len(group) <= SOURCE_CAP, 'identity_group_too_large')
        if len(current) + len(group) > SOURCE_CAP:
            cohorts.append(current)
            current = []
        current.extend(group)
    if current:
        cohorts.append(current)

    # Placeholder numeric IDs are deliberately not enrollment evidence. This
    # measures a serialized representation, not actual metadata or publication.
    synthetic = json.loads(manifest_raw)
    for number, row in enumerate(rows, 9_000_000_000):
        url = row['alias'].replace(row['identity_request'],
                                  f'https://api.github.com/repositories/{number}', 1)
        synthetic['sources'].append(dict(repository_id=number, url=url,
            request_id=Descriptor(url).request_id, aliases=[row['alias']],
            identity_evidence='docs/track/release-catalog/issues/67-expand-appimage-migration-throughput.md#synthetic'))
    count = len(synthetic['sources'])
    return dict(schema=1, payload_sha256=hashlib.sha256(payload_raw).hexdigest(),
        operational_manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),
        metadata_verified=False, production_applied=False,
        candidate_recipes=len(paths), candidate_endpoints=len(rows),
        identity_requests=len(identities), current_sources=len(manifest['sources']),
        union_sources=count, source_cap=SOURCE_CAP,
        synthetic_union_manifest_bytes=len(canonical(synthetic)), manifest_cap=64_000,
        tree_cap=TREE_CAP, per_body_cap=BODY_CAP,
        worst_case_union_body_bytes=count*BODY_CAP,
        body_only_average_budget=TREE_CAP//count,
        interpretation='Cohorts acquire evidence only; replacing the publication manifest retires omitted sources. '
                       'Synthetic IDs and sizes do not prove enrollment, compatibility or capacity. '
                       'Average body budget excludes index/lookup overhead. A cohort may exceed time/byte limits.',
        cohorts=[dict(number=i, endpoints=len(group),
            identity_requests=list(dict.fromkeys(row['identity_request'] for row in group)),
            aliases=[row['alias'] for row in group],
            recipes=[recipe['path'] for row in group for recipe in row['recipes']])
            for i, group in enumerate(cohorts, 1)])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    raw = (root/'docs/track/release-catalog/research/appimage-next-large-batch-20261102/payload.json').read_bytes()
    manifest = (root/'docs/track/release-catalog/design/staged-manifest.json').read_bytes()
    result = audit(raw, manifest, lambda path: (root/path).read_bytes())
    args.output.write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
