"""Local Git publication and pinned reads. Refuses repositories with remotes.

This module never fetches, pushes, clones, resolves network refs or runs artifacts.
"""
import os
from pathlib import Path
import re
import subprocess
import tempfile

from collector import require, timestamp
from storage import decode, digest, validate, INDEX_CAP
from manifest import load_manifest
from collector import Descriptor, BODY_CAP

REF = 'refs/heads/catalog'
HISTORY_CAP = 128_000_000


def git(repo, *args, data=None, index=None):
    env = dict(os.environ)
    # Do not inherit a caller-selected index/worktree/repository or injected config.
    for key in tuple(env):
        if key.startswith('GIT_'):
            env.pop(key)
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
               GIT_AUTHOR_NAME='Catalog staging', GIT_AUTHOR_EMAIL='catalog@invalid',
               GIT_COMMITTER_NAME='Catalog staging', GIT_COMMITTER_EMAIL='catalog@invalid')
    if index is not None:
        env['GIT_INDEX_FILE'] = str(index)
    return subprocess.run(['git', '-C', str(repo), '-c', 'core.hooksPath=/dev/null', *args],
                          input=data, env=env, check=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE).stdout


def publish_local(repo, tree, expected_parent):
    validate(tree)
    require(not git(repo, 'remote').strip(), 'remote_publication_not_supported')
    require(expected_parent is None or type(expected_parent) is str and
            re.fullmatch('[0-9a-f]{40}', expected_parent), 'invalid_parent')
    # Refuse unbounded local history before advancing the ref. No GC/rewrites.
    objects = Path(git(repo, 'rev-parse', '--path-format=absolute', '--git-path', 'objects').decode().strip())
    require(sum(p.stat().st_size for p in objects.rglob('*') if p.is_file()) +
            sum(map(len, tree.values())) <= HISTORY_CAP, 'history_bound')
    current = git(repo, 'for-each-ref', '--format=%(objectname)', REF).decode().strip() or None
    require(current == expected_parent, 'stale_parent')
    with tempfile.TemporaryDirectory(prefix='catalog-index-') as scratch:
        index = Path(scratch) / 'index'
        git(repo, 'read-tree', '--empty', index=index)
        for path, raw in sorted(tree.items()):
            oid = git(repo, 'hash-object', '-w', '--stdin', data=raw).decode().strip()
            git(repo, 'update-index', '--add', '--cacheinfo', '100644', oid, path, index=index)
        oid = git(repo, 'write-tree', index=index).decode().strip()
        parent = ['-p', current] if current else []
        commit = git(repo, 'commit-tree', oid, *parent,
                     data=b'Validated local catalog candidate\n').decode().strip()
        git(repo, 'update-ref', REF, commit, current or '0' * 40)
        return commit


def blob(repo, commit, path, cap):
    size = int(git(repo, 'cat-file', '-s', f'{commit}:{path}').strip())
    require(0 <= size <= cap, 'blob_bound')
    return git(repo, 'show', f'{commit}:{path}')


def lookup_local(repo, alias, commit, *, now, stale_acceptance=None):
    require(type(commit) is str and re.fullmatch('[0-9a-f]{40}', commit), 'commit_pin_required')
    # Do not resolve a branch during either read: both objects use this full commit.
    index_raw = blob(repo, commit, 'index.json', INDEX_CAP)
    require(len(index_raw) <= INDEX_CAP, 'index_bound')
    index = decode(index_raw)
    require(index['schema_version'] == 1 and
            digest(index['manifest_json'].encode()) == index['manifest_sha256'], 'invalid_index')
    plan = load_manifest(index['manifest_json'].encode(), index['workflow_repository_id'])
    require(timestamp(index['generated_at']) <= timestamp(now), 'future_publication')
    target = index['aliases'].get(alias)
    require(target is not None and target['active'] is True, 'alias_unavailable')
    rid = target['request_id']; entry = index['entries'][rid]
    source = next((r.source for r in plan.requests if r.source.descriptor.request_id == rid), None)
    require(source is not None and alias in (source.descriptor.url, *source.aliases) and
            Descriptor(**entry['descriptor']) == source.descriptor and
            entry['repository_id'] == source.repository_id, 'lookup_identity')
    require(entry['availability'] == 'available' and entry['observation'] is not None,
            'observation_unavailable')
    obs = entry['observation']
    require(obs['path'] == f'bodies/{rid}.json' and obs['received_time_basis'] ==
            obs['validation_time_basis'] == 'response-completed', 'invalid_observation')
    require(timestamp(obs['received_at']) <= timestamp(obs['validated_at']) <=
            timestamp(index['generated_at']) and obs['validation_status'] in {200, 304} and
            obs['scope'] == 'single-response', 'observation_chronology')
    age = (timestamp(now) - timestamp(obs['validated_at'])).total_seconds()
    require(age >= 0, 'future_observation')
    require(age <= 86400 or stale_acceptance == {
        'commit': commit, 'request_id': rid, 'sha256': obs['sha256']}, 'stale_acceptance_required')
    raw = blob(repo, commit, obs['path'], BODY_CAP)
    require(len(raw) == obs['bytes'] and digest(raw) == obs['sha256'], 'body_integrity')
    return raw, entry
