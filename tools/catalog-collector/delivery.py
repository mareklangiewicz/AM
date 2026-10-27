"""Fixed-repository catalog delivery. Never invokes upstream collection.

The publisher consumes a same-run artifact as data, recomputes storage, and can
push only the fixed catalog ref. All code comes from the approved source checkout.
"""
import base64
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import re
import select
import stat
import struct
import subprocess
import tempfile
import time
import zipfile

from collector import BODY_CAP, require, timestamp
from storage import INDEX_CAP, TREE_CAP, apply, decode, digest, validate
from publication import REF, HISTORY_CAP, blob, git, publish_local
from workflow_adapter import preflight

REPOSITORY = 'mareklangiewicz/AM'
URL = 'https://github.com/mareklangiewicz/AM.git'
REMOTE_REF = 'refs/heads/release-catalog'
ZIP_CAP = 105_000_000


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


def environment(token, scratch, *, github=False):
    require(type(token) is bytes and re.fullmatch(rb'[A-Za-z0-9_.-]+', token), 'invalid_delivery_token')
    env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LANG': 'C.UTF-8',
           'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
           'GIT_TERMINAL_PROMPT': '0'}
    if github:
        env.update(GH_HOST='github.com', GH_TOKEN=token.decode(), GH_PROMPT_DISABLED='1',
                   GH_CONFIG_DIR=str(scratch))
    else:
        header = 'AUTHORIZATION: basic ' + base64.b64encode(b'x-access-token:'+token).decode()
        env.update(GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='http.https://github.com/.extraheader',
                   GIT_CONFIG_VALUE_0=header)
    return env


def remote_git(repo, token, *args):
    with tempfile.TemporaryDirectory(prefix='catalog-auth-') as scratch:
        return bounded(['git', '-C', str(repo), '-c', 'core.hooksPath=/dev/null', *args],
                       env=environment(token, scratch), cap=64_000, objects=repo)


def read_git_tree(repo, commit):
    require(type(commit) is str and re.fullmatch('[0-9a-f]{40}', commit), 'invalid_publication_pin')
    listing = git(repo, 'ls-tree', '-rz', commit)
    require(len(listing) <= 200_000, 'tree_listing_bound')
    tree, total = {}, 0
    for record in listing.split(b'\0'):
        if not record:
            continue
        metadata, name = record.split(b'\t', 1)
        mode, kind, oid = metadata.split(b' ')
        path = name.decode('utf-8')
        require(mode == b'100644' and kind == b'blob' and
                (path in {'index.json', 'lookup.tsv'} or re.fullmatch(r'bodies/[0-9a-f]{64}\.json', path)),
                'unsafe_publication_tree')
        cap = INDEX_CAP if path in {'index.json', 'lookup.tsv'} else BODY_CAP
        size = int(git(repo, 'cat-file', '-s', oid.decode()))
        total += size
        require(size <= cap and total <= TREE_CAP, 'publication_tree_bound')
        tree[path] = blob(repo, commit, path, cap)
    validate(tree)
    return tree


def fetch_prior(context, token, directory):
    """Require exact caller pin or proven branch absence; no fallback/retry."""
    pin = context.get('previous_publication', '')
    require(type(pin) is str and (pin == '' or re.fullmatch('[0-9a-f]{40}', pin)), 'invalid_prior_pin')
    repo = Path(directory)
    repo.mkdir(exist_ok=False)
    # Our Git helper disables global config/hooks and accepts no executable input.
    git(repo, 'init', '--bare', '--quiet', '--template=')
    remote = remote_git(repo, token, 'ls-remote', '--refs', URL, REMOTE_REF).decode().strip()
    expected = f'{pin}\t{REMOTE_REF}' if pin else ''
    require(remote == expected, 'publication_parent_changed')
    if not pin:
        return None
    remote_git(repo, token, 'fetch', '--quiet', '--no-tags', '--depth=1', URL, f'{REMOTE_REF}:{REF}')
    actual = git(repo, 'rev-parse', REF).decode().strip()
    require(actual == pin, 'publication_parent_changed')
    tree = read_git_tree(repo, pin)
    require(timestamp(validate(tree)['generated_at']) <= datetime.now(timezone.utc), 'future_prior')
    return tree


def unpack_artifact(raw):
    """Bound ZIP members before reading; never extract paths or run files."""
    require(type(raw) is bytes and len(raw) <= ZIP_CAP, 'artifact_zip_bound')
    # Bound central-directory allocation before ZipFile constructs member objects.
    # ZIP64/multidisk envelopes are outside this deliberately small profile.
    position = raw.rfind(b'PK\x05\x06', max(0, len(raw)-65557))
    require(position >= 0 and len(raw)-position >= 22, 'artifact_zip_directory')
    disk, start_disk, disk_count, count, directory_size, offset, comment = struct.unpack(
        '<4H2IH', raw[position+4:position+22])
    require(disk == start_disk == 0 and disk_count == count and count <= 100 and
            directory_size <= 64_000 and offset+directory_size <= position and
            position+22+comment == len(raw), 'artifact_zip_directory_bound')
    files, total = {}, 0
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        infos = archive.infolist()
        require(len(infos) <= 100, 'artifact_file_count')
        for member in infos:
            name = member.filename
            require(name not in files and not member.is_dir() and
                    not member.flag_bits & 1, 'artifact_duplicate_or_directory')
            mode = member.external_attr >> 16
            require(not stat.S_ISLNK(mode) and not mode & 0o111 and
                    (stat.S_IFMT(mode) in (0, stat.S_IFREG)), 'artifact_mode')
            require(name in {'report.json', 'storage-report.json', 'candidate/index.json', 'candidate/lookup.tsv'} or
                    re.fullmatch(r'[0-9a-f]{64}\.body', name) or
                    re.fullmatch(r'candidate/bodies/[0-9a-f]{64}\.json', name), 'artifact_path')
            cap = INDEX_CAP if name.endswith(('index.json', 'lookup.tsv')) else 1_000_000 if name.endswith('report.json') else BODY_CAP
            total += member.file_size
            require(member.file_size <= cap and total <= ZIP_CAP, 'artifact_member_bound')
            with archive.open(member) as stream:
                body = stream.read(cap+1)
            require(len(body) == member.file_size and len(body) <= cap, 'artifact_member_length')
            files[name] = body
    require({'report.json', 'storage-report.json', 'candidate/index.json'} <= set(files), 'artifact_missing_file')
    return files


def verify_artifact(files, context, manifest_raw, revision, previous):
    preflight(context, manifest_raw, revision)
    report = decode(files['report.json'])
    require(report['context'] == context, 'artifact_context_mismatch')
    tree = {p[len('candidate/'):]: raw for p, raw in files.items() if p.startswith('candidate/')}
    index = validate(tree)
    require(index['collector_revision'] == revision and index['manifest_json'].encode() == manifest_raw and
            index['run'] == {'id': context['run_id'], 'attempt': context['run_attempt']}, 'candidate_provenance')
    require(timestamp(index['generated_at']) <= datetime.now(timezone.utc), 'future_candidate')
    attempts = []
    expected = {'report.json', 'storage-report.json', *('candidate/'+p for p in tree)}
    for item in report['attempts']:
        record = dict(item)
        length, sha = record.pop('body_bytes'), record.pop('body_sha256')
        path = record['request_id']+'.body'
        if record['outcome'] == 'response':
            require(path in files, 'artifact_missing_body')
            body = files[path]; expected.add(path)
        else:
            body = b''
        require(type(length) is int and len(body) == length and digest(body) == sha, 'artifact_body_integrity')
        record['body'] = body; attempts.append(record)
    require(set(files) == expected, 'artifact_extra_file')
    rebuilt, transitions = apply(previous, manifest_raw, attempts,
        workflow_identity=int(context['repository_id']), generated_at=index['generated_at'],
        revision=revision, run={'id': context['run_id'], 'attempt': context['run_attempt']})
    require(rebuilt == tree, 'candidate_recomputation_mismatch')
    storage_report = decode(files['storage-report.json'])
    require(storage_report == {'outcome':'validated_candidate', 'transitions':transitions,
        'files':{p:{'bytes':len(raw),'sha256':digest(raw)} for p,raw in tree.items()}}, 'storage_report_mismatch')
    require(report['run']['complete'] is True and len(attempts) == 6 and
            all(t['outcome'] in {'observed', 'validated'} for t in transitions), 'incomplete_publication')
    return tree


def download_artifact(context, artifact_id, expected_digest, token):
    require(type(artifact_id) is str and re.fullmatch('[1-9][0-9]*', artifact_id), 'invalid_artifact_id')
    require(type(expected_digest) is str and re.fullmatch('[0-9a-f]{64}', expected_digest), 'invalid_artifact_digest')
    endpoint = f'repos/{REPOSITORY}/actions/artifacts/{artifact_id}'
    with tempfile.TemporaryDirectory(prefix='catalog-api-') as scratch:
        env = environment(token, scratch, github=True)
        command = ['gh', 'api', '--hostname', 'github.com', '-H', 'X-GitHub-Api-Version: 2022-11-28']
        meta = decode(bounded([*command, endpoint], env=env, cap=64_000))
        run = meta['workflow_run']
        require(meta['id'] == int(artifact_id) and meta['expired'] is False and
                meta['name'] == f'restricted-catalog-{context["run_id"]}-{context["run_attempt"]}' and
                run['id'] == int(context['run_id']) and run['head_sha'] == context['sha'] and
                run['repository_id'] == int(context['repository_id']) and
                run['head_repository_id'] == int(context['repository_id']) and
                run['head_branch'] == 'main-marek' and meta['size_in_bytes'] <= ZIP_CAP and
                meta['digest'] == 'sha256:'+expected_digest, 'artifact_origin_mismatch')
        raw = bounded([*command, endpoint+'/zip'], env=env, cap=ZIP_CAP)
        require(digest(raw) == expected_digest, 'artifact_download_digest')
        return unpack_artifact(raw)


def publish(context, manifest_raw, revision, artifact_id, artifact_digest, token, directory):
    preflight(context, manifest_raw, revision)
    root = Path(directory); root.mkdir(exist_ok=False)
    previous = fetch_prior(context, token, root/'git')
    files = download_artifact(context, artifact_id, artifact_digest, token)
    tree = verify_artifact(files, context, manifest_raw, revision, previous)
    parent = context.get('previous_publication') or None
    commit = publish_local(root/'git', tree, parent)
    # Check again immediately before a normal push. A racing descendant is rejected
    # by Git's ordinary fast-forward requirement; there is no force/retry path.
    actual = remote_git(root/'git', token, 'ls-remote', '--refs', URL, REMOTE_REF).decode().strip()
    require(actual == (f'{parent}\t{REMOTE_REF}' if parent else ''), 'publication_parent_changed')
    remote_git(root/'git', token, 'push', '--quiet', URL, f'{commit}:{REMOTE_REF}')
    result = dict(commit=commit, parent=parent, ref=REMOTE_REF, source_revision=revision,
                  run_id=context['run_id'], run_attempt=context['run_attempt'],
                  artifact_id=artifact_id, artifact_digest=artifact_digest,
                  index_sha256=digest(tree['index.json']), tree_bytes=sum(map(len,tree.values())))
    (root/'publication.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
