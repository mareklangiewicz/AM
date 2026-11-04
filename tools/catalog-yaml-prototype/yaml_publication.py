"""Offline format-2 publication candidate. No network or operational integration."""
import os
import pathlib
import re
import subprocess
import sys
import tempfile

import yaml
from writer import document

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'catalog-collector'))
from publication import git  # Reuse existing isolated local Git invocation.

REF = 'refs/heads/catalog'


def candidate_tree(apps, repositories, *, schema, max_file_bytes):
    """Assemble a complete snapshot; trial file allowance is explicit."""
    if type(max_file_bytes) is not int or not 1 <= max_file_bytes <= 33554432:
        raise ValueError('file allowance')
    for rid, repository in repositories.items():
        if (type(rid) is not str or not re.fullmatch('[1-9][0-9]*', rid)
                or type(repository['repository_id']) is not int
                or str(repository['repository_id']) != rid):
            raise ValueError('repository identity')
    if any(type(rid) is not int or str(rid) not in repositories for rid in apps.values()):
        raise ValueError('app references missing repository')
    documents = {'apps.yaml': dict(format=2, schema=schema, apps=dict(sorted(apps.items())))}
    for rid in sorted(repositories, key=int):
        # Schema describes this writer's reviewed source, not a collection time.
        documents['repositories/'+rid+'.yaml'] = dict(repositories[rid], schema=schema)
    tree = {}
    with tempfile.TemporaryDirectory(prefix='yaml-validate-') as directory:
        path = pathlib.Path(directory)/'document.yaml'
        for name, obj in documents.items():
            raw = document(obj).encode('utf-8')
            if len(raw) > max_file_bytes:
                raise ValueError('file allowance')
            # The writer owns YAML/Unicode correctness; the shell owns the subset.
            if yaml.safe_load(raw) != obj:
                raise ValueError('YAML round trip')
            path.write_bytes(raw)
            env = dict(os.environ, AM_YAML_MAX_INPUT_BYTES=str(max_file_bytes))
            run = subprocess.run(['sh', str(HERE/'reader.sh'), 'validate', str(path)],
                                 env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if run.returncode:
                raise ValueError(run.stderr.decode('utf-8', errors='replace'))
            tree[name] = raw
    return tree


def publish_local(repo, apps, repositories, *, schema, max_file_bytes, expected_parent):
    """Validate first, then atomically replace a ref in a remote-free local repo."""
    tree = candidate_tree(apps, repositories, schema=schema, max_file_bytes=max_file_bytes)
    if git(repo, 'remote').strip():
        raise ValueError('local repository required')
    if expected_parent is not None and not re.fullmatch('[0-9a-f]{40}', expected_parent):
        raise ValueError('parent commit')
    current = git(repo, 'for-each-ref', '--format=%(objectname)', REF).decode().strip() or None
    if current != expected_parent:
        raise ValueError('stale parent')
    with tempfile.TemporaryDirectory(prefix='yaml-index-') as directory:
        index = pathlib.Path(directory)/'index'
        git(repo, 'read-tree', '--empty', index=index)
        for path, raw in sorted(tree.items()):
            oid = git(repo, 'hash-object', '-w', '--stdin', data=raw).decode().strip()
            git(repo, 'update-index', '--add', '--cacheinfo', '100644', oid, path, index=index)
        oid = git(repo, 'write-tree', index=index).decode().strip()
        parent = ['-p', current] if current else []
        commit = git(repo, 'commit-tree', oid, *parent,
                     data=b'Offline format-2 catalog candidate\n').decode().strip()
        git(repo, 'update-ref', REF, commit, current or '0'*40)
        return commit
