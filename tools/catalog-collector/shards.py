"""Bounded catalog shards with one atomic publication and unchanged shell paths.

Each shard uses the existing closed storage format and 52-source/50-MB limits.
The root contains only routing metadata; all bodies retain bodies/REQUEST.json.
No credentials, network or filesystem access in composition/validation.
"""
import re

from collector import require, timestamp
from storage import INDEX_CAP, TREE_CAP, canonical, decode, digest, validate
from shell_lookup import render

SHARD_CAP = 32


def root_index(raw):
    require(type(raw) is bytes and len(raw) <= INDEX_CAP, 'root_index_bound')
    value = decode(raw)
    require(type(value) is dict and set(value) == {
        'schema_version', 'generated_at', 'collector_revision', 'run',
        'workflow_repository_id', 'shards', 'aliases'}, 'root_fields')
    require(type(value['schema_version']) is int and value['schema_version'] == 2,
            'root_schema')
    timestamp(value['generated_at'])
    require(type(value['collector_revision']) is str and
            re.fullmatch('[0-9a-f]{40}', value['collector_revision']), 'root_revision')
    require(type(value['workflow_repository_id']) is int and
            value['workflow_repository_id'] == 1291019762, 'root_repository')
    require(type(value['run']) is dict and set(value['run']) == {'id', 'attempt'} and
            all(type(v) is str and re.fullmatch('[1-9][0-9]*', v)
                for v in value['run'].values()), 'root_run')
    require(type(value['shards']) is dict and 0 < len(value['shards']) <= SHARD_CAP and
            type(value['aliases']) is dict, 'root_shards')
    for name, row in value['shards'].items():
        require(type(name) is str and re.fullmatch('[0-9]{2}', name) and
                type(row) is dict and set(row) == {'path', 'bytes', 'sha256'} and
                row['path'] == f'shards/{name}/index.json' and
                type(row['bytes']) is int and 0 < row['bytes'] <= INDEX_CAP and
                type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']),
                'root_shard')
    for alias, name in value['aliases'].items():
        require(type(alias) is str and type(name) is str and name in value['shards'],
                'root_alias')
    return value


def selected_index(root_raw, alias, shard_raw):
    root = root_index(root_raw)
    name = root['aliases'].get(alias)
    require(name is not None, 'alias_unavailable')
    row = root['shards'][name]
    require(type(shard_raw) is bytes and len(shard_raw) == row['bytes'] and
            digest(shard_raw) == row['sha256'], 'shard_integrity')
    from storage import validate_index
    shard = validate_index(shard_raw)
    require(shard['workflow_repository_id'] == root['workflow_repository_id'] and
            timestamp(shard['generated_at']) <= timestamp(root['generated_at']) and
            set(a for a, target in shard['aliases'].items() if target['active']) ==
            set(a for a, owner in root['aliases'].items() if owner == name), 'shard_routes')
    return shard


def compose(trees, *, generated_at, revision, run):
    require(type(trees) is dict and 0 < len(trees) <= SHARD_CAP, 'shard_count')
    root = dict(schema_version=2, generated_at=generated_at, collector_revision=revision,
                run=run, workflow_repository_id=1291019762, shards={}, aliases={})
    merged = dict(generated_at=generated_at, collector_revision=revision, run=run,
                  entries={}, aliases={})
    tree, locators = {}, {}
    for name, candidate in sorted(trees.items()):
        require(type(name) is str and re.fullmatch('[0-9]{2}', name), 'shard_name')
        index = validate(candidate)
        require(index['workflow_repository_id'] == root['workflow_repository_id'] and
                timestamp(index['generated_at']) <= timestamp(generated_at), 'shard_provenance')
        raw = candidate['index.json']
        root['shards'][name] = dict(path=f'shards/{name}/index.json', bytes=len(raw), sha256=digest(raw))
        for path, body in candidate.items():
            destination = path if path.startswith('bodies/') else f'shards/{name}/{path}'
            require(destination not in tree, 'duplicate_shard_body')
            tree[destination] = body
        for rid, entry in index['entries'].items():
            require(rid not in merged['entries'], 'duplicate_shard_request')
            merged['entries'][rid] = entry
        for alias, target in index['aliases'].items():
            # Keep inactive alias records too, including retirement refusals.
            require(alias not in merged['aliases'], 'duplicate_shard_alias')
            locator = alias.split('/releases', 1)[0].lower()
            repository_id = index['entries'][target['request_id']]['repository_id']
            require(locators.get(locator, repository_id) == repository_id, 'repository_identity_conflict')
            locators[locator] = repository_id
            merged['aliases'][alias] = target
            if target['active']:
                root['aliases'][alias] = name
    raw = canonical(root)+b'\n'
    root_index(raw)
    tree['index.json'] = raw
    tree['lookup.tsv'] = render(merged, raw)
    # Explicit aggregate ceiling follows the reviewed number of individually
    # bounded shards; the legacy TREE_CAP is never changed.
    require(sum(map(len, tree.values())) <= len(trees)*TREE_CAP+2*INDEX_CAP, 'root_tree_bound')
    return tree


def split(tree):
    root = root_index(tree['index.json'])
    trees = {}
    expected = {'index.json', 'lookup.tsv'}
    for name, row in root['shards'].items():
        require(row['path'] in tree, 'missing_shard_index')
        raw = tree[row['path']]
        # Select any active alias to check the route partition and shard hash.
        alias = next((a for a, owner in root['aliases'].items() if owner == name), None)
        require(alias is not None, 'empty_shard')
        index = selected_index(tree['index.json'], alias, raw)
        candidate = {'index.json': raw}
        lookup = f'shards/{name}/lookup.tsv'
        if lookup in tree:
            candidate['lookup.tsv'] = tree[lookup]
            expected.add(lookup)
        expected.add(row['path'])
        for entry in index['entries'].values():
            obs = entry['observation']
            if obs:
                path = obs['path']
                require(path in tree, 'missing_shard_body')
                candidate[path] = tree[path]
                expected.add(path)
        validate(candidate)
        trees[name] = candidate
    require(set(tree) == expected, 'unexpected_root_file')
    rebuilt = compose(trees, generated_at=root['generated_at'],
                      revision=root['collector_revision'], run=root['run'])
    require(rebuilt == tree, 'root_recomputation')
    return trees
