"""Isolated local Git publication and bounded snapshot reads.

Callers validate catalog bytes. Publication is remote-free and advances only the
expected parent; read commands have explicit byte, time and history bounds.
"""
import os
import hashlib
from pathlib import Path
import re
import select
import subprocess
import tempfile
import time

from bounded import require

REF = 'refs/heads/catalog'
# Intermediate bounded profile: measured published history + 500-source tree is
# about 141 MB; retain growth headroom without allowing unbounded Git history.
HISTORY_CAP = 256 * 1024 * 1024


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


def publish_tree(repo, tree, expected_parent, *, metrics=None):
    """Commit a caller-validated inert tree and atomically advance a local ref."""
    require(not git(repo, 'remote').strip(), 'remote_publication_not_supported')
    require(expected_parent is None or type(expected_parent) is str and
            re.fullmatch('[0-9a-f]{40}', expected_parent), 'invalid_parent')
    # Refuse unbounded local history before advancing the ref. No GC/rewrites.
    objects = Path(git(repo, 'rev-parse', '--path-format=absolute', '--git-path', 'objects').decode().strip())
    object_bytes = sum(p.stat().st_size for p in objects.rglob('*') if p.is_file())
    snapshot_bytes = sum(map(len, tree.values()))
    if metrics is not None:
        metrics.update(history_object_bytes_before=object_bytes,
                       snapshot_yaml_bytes=snapshot_bytes,
                       history_guard_bytes=object_bytes+snapshot_bytes,
                       history_cap=HISTORY_CAP)
    require(object_bytes+snapshot_bytes <= HISTORY_CAP, 'history_bound')
    current = git(repo, 'for-each-ref', '--format=%(objectname)', REF).decode().strip() or None
    require(current == expected_parent, 'stale_parent')
    with tempfile.TemporaryDirectory(prefix='catalog-index-') as scratch:
        index = Path(scratch) / 'index'
        # Start from the exact validated parent. Unchanged blobs and index entries
        # are reused; the caller still supplies the entire validated next tree.
        existing = {}
        if current:
            for record in git(repo, 'ls-tree', '-rz', current).split(b'\0'):
                if record:
                    metadata, name = record.split(b'\t', 1)
                    mode, kind, oid = metadata.split(b' ')
                    existing[name.decode('utf-8')] = (mode, kind, oid.decode())
            git(repo, 'read-tree', current, index=index)
        else:
            git(repo, 'read-tree', '--empty', index=index)
        updates = bytearray()
        for path in sorted(existing.keys() - tree.keys()):
            updates.extend(b'0 '+b'0'*40+b'\t'+path.encode('utf-8')+b'\0')
        for path, raw in sorted(tree.items()):
            # Catalog pins and publication use Git's SHA-1 object format. Hash the
            # blob framing too; content digests alone are not Git object IDs.
            oid = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            if existing.get(path) == (b'100644', b'blob', oid):
                continue
            oid = git(repo, 'hash-object', '-w', '--stdin', data=raw).decode().strip()
            updates.extend(b'100644 '+oid.encode()+b'\t'+path.encode('utf-8')+b'\0')
        if updates:
            git(repo, 'update-index', '-z', '--index-info', data=bytes(updates), index=index)
        oid = git(repo, 'write-tree', index=index).decode().strip()
        parent = ['-p', current] if current else []
        commit = git(repo, 'commit-tree', oid, *parent,
                     data=b'Validated local catalog candidate\n').decode().strip()
        git(repo, 'update-ref', REF, commit, current or '0' * 40)
        if metrics is not None:
            metrics['history_object_bytes_after'] = sum(
                p.stat().st_size for p in objects.rglob('*') if p.is_file())
        return commit


def bounded(command, *, env, cap, objects=None, seconds=90):
    """No exception/command diagnostics can expose headers or token values."""
    process = subprocess.Popen(command, env=env, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, close_fds=True)
    output = bytearray(); deadline = time.monotonic() + seconds
    try:
        os.set_blocking(process.stdout.fileno(), False)
        while True:
            require(time.monotonic() < deadline, 'delivery_deadline')
            if objects is not None:
                require(sum(p.stat().st_size for p in Path(objects).rglob('*') if p.is_file()) <=
                        HISTORY_CAP, 'delivery_history_bound')
            ready, _, _ = select.select([process.stdout], [], [], min(.1, max(0, deadline-time.monotonic())))
            if not ready:
                continue
            chunk = os.read(process.stdout.fileno(), min(8192, cap-len(output)+1))
            require(len(output)+len(chunk) <= cap, 'delivery_output_bound')
            if not chunk:
                break
            output.extend(chunk)
        require(process.wait(timeout=max(.001, deadline-time.monotonic())) == 0, 'delivery_command_refusal')
        return bytes(output)
    except Exception:
        raise ValueError('delivery_command_refusal') from None
    finally:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=1)
        process.stdout.close()



def environment():
    """Credential-free Git environment; ignore caller Git config and discovery."""
    return {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LANG': 'C.UTF-8',
            'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
            'GIT_TERMINAL_PROMPT': '0'}
