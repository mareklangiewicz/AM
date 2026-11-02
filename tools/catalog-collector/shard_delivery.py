"""Reviewed-inventory shard collection and exact-prior atomic root publication."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import tempfile

from collector import require
from delivery import (REPOSITORY, URL, REMOTE_REF, fetch_prior, read_git_tree,
                      download_artifact, verify_artifact, remote_git, bounded, environment)
from manifest import load_manifest
from publication import REF, HISTORY_CAP, blob, git
from shards import SHARD_CAP, compose, root_index, selected_index
from storage import BODY_CAP, INDEX_CAP, TREE_CAP, decode, digest, validate, validate_index
from workflow_adapter import preflight, run


def inventory(context, raw, revision, root):
    # Validate approved revision/context using a real manifest before any token.
    require(type(raw) is bytes and len(raw) <= 64_000 and
            digest(raw) == context.get('inventory_sha256'), 'unapproved_inventory')
    value = decode(raw)
    require(type(value) is dict and set(value) == {'schema', 'shards'} and
            type(value['schema']) is int and value['schema'] == 1 and
            type(value['shards']) is dict and 0 < len(value['shards']) <= SHARD_CAP,
            'inventory_fields')
    result, aliases, requests, locators = {}, set(), set(), {}
    for name, row in value['shards'].items():
        require(type(name) is str and re.fullmatch('[0-9]{2}', name) and
                type(row) is dict and set(row) == {'path', 'sha256'} and
                type(row['path']) is str and re.fullmatch(
                    r'docs/track/release-catalog/research/appimage-next-large-batch-20261102/prepared/manifest-[0-9]{2}\.json', row['path']) and
                row['path'].endswith(f'manifest-{name}.json'), 'inventory_path')
        path = Path(root)/row['path']
        require(not path.is_symlink() and path.stat().st_size <= 64_000, 'manifest_bound')
        manifest = path.read_bytes()
        require(digest(manifest) == row['sha256'], 'inventory_manifest_digest')
        ctx = dict(context, manifest_sha256=row['sha256'])
        plan = preflight(ctx, manifest, revision)
        for request in plan.requests:
            source = request.source
            rid = source.descriptor.request_id
            require(rid not in requests, 'inventory_duplicate_request')
            requests.add(rid)
            for alias in (source.descriptor.url, *source.aliases):
                require(alias not in aliases, 'inventory_duplicate_alias')
                locator = alias.split('/releases', 1)[0].lower()
                require(locators.get(locator, source.repository_id) == source.repository_id,
                        'repository_identity_conflict')
                locators[locator] = source.repository_id
                aliases.add(alias)
        result[name] = manifest
    require('00' in result, 'missing_legacy_shard')
    return result


def read_shard(repo, pin, name):
    raw = blob(repo, pin, 'index.json', INDEX_CAP)
    if decode(raw).get('schema_version') == 1:
        return read_git_tree(repo, pin) if name == '00' else None
    root = root_index(raw)
    from collector import timestamp
    require(timestamp(root['generated_at']) <= datetime.now(timezone.utc), 'future_prior')
    if name not in root['shards']:
        return None
    row = root['shards'][name]
    shard_raw = blob(repo, pin, row['path'], row['bytes'])
    alias = next((a for a, owner in root['aliases'].items() if owner == name), None)
    require(alias is not None, 'empty_shard')
    index = selected_index(raw, alias, shard_raw)
    tree = {'index.json':shard_raw}
    # Derived per-shard lookup is optional in legacy storage and unnecessary for
    # conditional planning; apply() always regenerates it for the new candidate.
    total = len(shard_raw)
    for entry in index['entries'].values():
        obs = entry['observation']
        if obs:
            total += obs['bytes']
            require(total <= TREE_CAP, 'shard_tree_bound')
            tree[obs['path']] = blob(repo, pin, obs['path'], obs['bytes'])
    validate(tree)
    return tree


def list_artifacts(context, names, token):
    """Discover only exact same-run shard artifacts; downloader rechecks provenance."""
    with tempfile.TemporaryDirectory(prefix='catalog-shard-api-') as scratch:
        raw = bounded(['gh', 'api', '--hostname', 'github.com',
            f'repos/{REPOSITORY}/actions/runs/{context["run_id"]}/artifacts?per_page=100'],
            env=environment(token, scratch, github=True), cap=1_000_000)
    value = decode(raw)
    require(value['total_count'] == len(value['artifacts']) and
            len(value['artifacts']) <= SHARD_CAP, 'artifact_listing_bound')
    result = {}
    prefix = f'restricted-catalog-{context["run_id"]}-{context["run_attempt"]}-'
    for row in value['artifacts']:
        require(row['name'].startswith(prefix), 'unexpected_run_artifact')
        name = row['name'][len(prefix):]
        require(name in names and name not in result and
                type(row['digest']) is str and re.fullmatch('sha256:[0-9a-f]{64}', row['digest']),
                'artifact_shard_identity')
        result[name] = dict(id=str(row['id']), digest=row['digest'][7:])
    require(set(result) == set(names), 'missing_shard_artifact')
    return result


def collect_shard(context, inventory_raw, revision, root, name, token, output, scratch):
    manifests = inventory(context, inventory_raw, revision, root)
    require(name in manifests, 'unknown_shard')
    prior = fetch_prior(context, token, scratch,
                        reader=lambda repo, pin: read_shard(repo, pin, name))
    ctx = dict(context, manifest_sha256=digest(manifests[name]))
    if prior is None:
        ctx['previous_publication'] = ''
    return run(ctx, manifests[name], revision, token, output, previous_tree=prior)


def publish_root_local(repo, tree, expected_parent, *, shard_count):
    """Write validated recomputed shards to one CAS commit, without raw-size inflation.

    Every tree comes from compose(); recheck closure before Git writes. Aggregate
    objects remain subject to the existing 128-MB compressed Git history limit.
    """
    from shards import split
    require(len(split(tree)) == shard_count, 'publication_shard_count')
    current = git(repo, 'for-each-ref', '--format=%(objectname)', REF).decode().strip() or None
    require(current == expected_parent, 'stale_parent')
    objects = Path(git(repo, 'rev-parse', '--path-format=absolute', '--git-path', 'objects').decode().strip())
    def check_objects():
        require(sum(p.stat().st_size for p in objects.rglob('*') if p.is_file()) <= HISTORY_CAP,
                'history_bound')
    check_objects()
    with tempfile.TemporaryDirectory(prefix='catalog-root-index-') as scratch:
        index = Path(scratch)/'index'
        git(repo, 'read-tree', '--empty', index=index)
        # One bounded update-index stream avoids thousands of Git processes.
        records = []
        for path, raw in sorted(tree.items()):
            oid = git(repo, 'hash-object', '-w', '--stdin', data=raw).decode().strip()
            records.append(f'100644 {oid}\t{path}\0'.encode())
            check_objects()
        git(repo, 'update-index', '-z', '--index-info', data=b''.join(records), index=index)
        oid = git(repo, 'write-tree', index=index).decode().strip()
        parent = ['-p', current] if current else []
        commit = git(repo, 'commit-tree', oid, *parent,
                     data=b'Validated bounded catalog shards\n').decode().strip()
        check_objects()
        git(repo, 'update-ref', REF, commit, current or '0'*40)
        return commit


def publish(context, inventory_raw, revision, root, artifacts, token, directory):
    manifests = inventory(context, inventory_raw, revision, root)
    require(type(artifacts) is dict and set(artifacts) == set(manifests), 'artifact_shards')
    directory = Path(directory)
    directory.mkdir(exist_ok=False)
    # Fetch the exact parent once. Reader returns a bounded legacy shard solely
    # to reuse the existing parent/future/provenance checks.
    fetch_prior(context, token, directory/'git', reader=lambda repo, pin: read_shard(repo, pin, '00'))
    repo, trees = directory/'git', {}
    for name, raw in sorted(manifests.items()):
        prior = read_shard(repo, context['previous_publication'], name) if context['previous_publication'] else None
        ctx = dict(context, manifest_sha256=digest(raw))
        if prior is None:
            ctx['previous_publication'] = ''
        row = artifacts[name]
        require(type(row) is dict and set(row) == {'id', 'digest'}, 'artifact_descriptor')
        files = download_artifact(context, row['id'], row['digest'], token,
            artifact_name=f'restricted-catalog-{context["run_id"]}-{context["run_attempt"]}-{name}')
        trees[name] = verify_artifact(files, ctx, raw, revision, prior)
    generated = datetime.now(timezone.utc).isoformat()
    tree = compose(trees, generated_at=generated, revision=revision,
                   run={'id':context['run_id'], 'attempt':context['run_attempt']})
    parent = context['previous_publication'] or None
    commit = publish_root_local(repo, tree, parent, shard_count=len(trees))
    actual = remote_git(repo, token, 'ls-remote', '--refs', URL, REMOTE_REF).decode().strip()
    require(actual == (f'{parent}\t{REMOTE_REF}' if parent else ''), 'publication_parent_changed')
    remote_git(repo, token, 'push', '--quiet', URL, f'{commit}:{REMOTE_REF}')
    result = dict(commit=commit, parent=parent, source_revision=revision,
        inventory_sha256=digest(inventory_raw), shards=len(trees), tree_bytes=sum(map(len,tree.values())),
        index_sha256=digest(tree['index.json']), run_id=context['run_id'], run_attempt=context['run_attempt'])
    (directory/'publication.json').write_text(json.dumps(result, indent=2)+'\n')
    return result
