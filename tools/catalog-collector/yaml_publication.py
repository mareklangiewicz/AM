"""Validate, publish and read the maintained YAML catalog at exact Git commits."""
import re

import yaml

# The distributed reader validates the grammar before either safe loader runs.
SAFE_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
from writer import document
from wire_validation import validate_wire

from bounded import require
from publication import REF, git  # Reuse existing isolated local Git invocation.

def check_references(apps, repositories):
    for rid, repository in repositories.items():
        if (type(rid) is not str or not re.fullmatch('[1-9][0-9]*', rid)
                or type(repository['repository_id']) is not int
                or str(repository['repository_id']) != rid):
            raise ValueError('repository identity')
    if any(type(rid) is not int or str(rid) not in repositories for rid in apps.values()):
        raise ValueError('app references missing repository')


def decode_document(raw, max_file_bytes):
    """Validate the original bytes before a general YAML parser can normalize them."""
    if len(raw) > max_file_bytes:
        raise ValueError('file allowance')
    validate_wire(raw,max_file_bytes)
    return yaml.load(raw, Loader=SAFE_LOADER)


def candidate_tree(apps, repositories, *, schema, max_file_bytes):
    """Assemble a complete snapshot; trial file allowance is explicit."""
    if type(max_file_bytes) is not int or not 1 <= max_file_bytes <= 33554432:
        raise ValueError('file allowance')
    check_references(apps, repositories)
    documents = {'apps.yaml': dict(format=2, schema=schema, apps=dict(sorted(apps.items())))}
    for rid in sorted(repositories, key=int):
        # Preserve each document's source provenance when it was not attempted.
        documents['repositories/'+rid+'.yaml'] = dict(repositories[rid])
    tree = {}
    for name, obj in documents.items():
        raw = document(obj).encode('utf-8')
        if decode_document(raw, max_file_bytes) != obj:
            raise ValueError('YAML round trip')
        tree[name] = raw
    return tree


def publish_local(repo, apps, repositories, *, schema, max_file_bytes, expected_parent):
    """Validate first, then atomically replace a ref in a remote-free local repo."""
    tree = candidate_tree(apps, repositories, schema=schema, max_file_bytes=max_file_bytes)
    from publication import publish_tree
    return publish_tree(repo,tree,expected_parent)


def load_local(repo, commit, *, max_file_bytes):
    """Read a complete format-2 snapshot at an exact commit, never a moving ref."""
    require(type(max_file_bytes) is int and 1 <= max_file_bytes <= 33554432, 'invalid_yaml_file_cap')
    limits = dict(max_file_bytes=max_file_bytes,max_files=1024,max_tree_bytes=1073741824)
    tree = _read_tree(repo,commit,limits)
    return tree_documents(tree,limits)


def refresh_local(repo, commit, pages, *, attempted_at, schema, max_file_bytes,
                  **collection_options):
    """Refresh explicitly selected sources from saved responses; preserve the rest."""
    from bounded import collect_files
    apps, repositories = load_local(repo, commit, max_file_bytes=max_file_bytes)
    if any(rid not in repositories for rid in pages):
        raise ValueError('unknown selected repository')
    for rid, responses in pages.items():
        repositories[rid] = collect_files(repositories[rid], responses,
                                          attempted_at=attempted_at,
                                          max_catalog_bytes=max_file_bytes,
                                          **collection_options)
    return publish_local(repo, apps, repositories, schema=schema,
                         max_file_bytes=max_file_bytes, expected_parent=commit)


def tree_documents(tree, limits):
    require(type(tree) is dict and 'apps.yaml' in tree and len(tree) <= limits['max_files'],
            'invalid_yaml_tree')
    total = 0
    repositories = {}
    for path, body in tree.items():
        require(path == 'apps.yaml' or re.fullmatch(r'repositories/[1-9][0-9]*\.yaml',path),
                'unexpected_yaml_path')
        require(type(body) is bytes, 'invalid_yaml_bytes')
        total += len(body)
        require(total <= limits['max_tree_bytes'], 'yaml_tree_bound')
        obj = decode_document(body, limits['max_file_bytes'])
        if path == 'apps.yaml':
            apps = obj['apps']
            schema = obj['schema']
            canonical = dict(format=2, schema=schema, apps=dict(sorted(apps.items())))
        else:
            rid = path.split('/')[1][:-5]
            require(str(obj['repository_id']) == rid, 'yaml_path_identity')
            repositories[rid] = obj
            canonical = obj
        # The original bytes have already passed the distributed reader above.
        # Compare canonical encoding directly rather than validating every blob
        # a second time through candidate_tree on each publication read.
        require(document(canonical).encode('utf-8') == body, 'noncanonical_yaml_candidate')
    check_references(apps, repositories)
    return apps, repositories


def read_tree(repo, pin, limits):
    """Read only bounded canonical format-2 blobs at the exact fetched commit."""
    tree = _read_tree(repo, pin, limits)
    tree_documents(tree, limits)
    return tree


def _read_tree(repo, pin, limits):
    """Read bounded inert blobs; callers must validate through tree_documents."""
    from pathlib import Path
    from publication import bounded, environment

    require(type(pin) is str and re.fullmatch('[0-9a-f]{40}',pin), 'invalid_prior_pin')
    # Reuse credential-free isolated Git environment and bounded process I/O.
    env = environment()
    def local(*args, cap):
        return bounded(['git','-C',str(repo),'-c','core.hooksPath=/dev/null',*args],
                       env=env,cap=cap,objects=Path(repo))
    listing = local('ls-tree','-rz',pin,cap=200_000)
    tree, total = {}, 0
    for record in listing.split(b'\0'):
        if not record:
            continue
        require(len(tree) < limits['max_files'], 'yaml_prior_file_bound')
        metadata, name = record.split(b'\t',1)
        mode, kind, oid = metadata.split(b' ')
        path = name.decode('utf-8')
        require(mode == b'100644' and kind == b'blob' and
                (path == 'apps.yaml' or re.fullmatch(r'repositories/[1-9][0-9]*\.yaml',path)),
                'yaml_prior_layout')
        size = int(local('cat-file','-s',oid.decode(),cap=64))
        total += size
        require(size <= limits['max_file_bytes'] and total <= limits['max_tree_bytes'],
                'yaml_prior_byte_bound')
        body = local('cat-file','blob',oid.decode(),cap=limits['max_file_bytes'])
        require(len(body) == size, 'yaml_prior_blob_length')
        tree[path] = body
    return tree


def schema_url(revision):
    require(isinstance(revision, str) and re.fullmatch('[0-9a-f]{40}', revision),
            'invalid_source_revision')
    return ('https://raw.githubusercontent.com/mareklangiewicz/AM/' + revision
            + '/docs/catalog-format-v2.md')
