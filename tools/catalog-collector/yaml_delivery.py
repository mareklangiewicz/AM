"""Inactive format-2 artifact/prior/publication candidate; no token lookup."""
import io
import re
import stat
import struct
import zipfile

from collector import require
from delivery import download_artifact
from yaml_staging import checked, stage, verify


def archive_cap(limits):
    # Uncompressed tree + receipt, with bounded ZIP framing/compression overhead.
    return limits['max_tree_bytes'] + limits['max_receipt_bytes'] + 1_000_000


def unpack(raw, limits):
    """Decode a closed ZIP as data only, bounding directory allocation first.

    GitHub upload-artifact can include directory entries. Accept only the two
    structural directories; never extract archive names onto the filesystem.
    ZIP64, multi-disk, encryption and non-store/deflate codecs are out of profile.
    """
    require(type(raw) is bytes and len(raw) <= archive_cap(limits), 'yaml_zip_bound')
    position = raw.rfind(b'PK\x05\x06', max(0,len(raw)-65557))
    require(position >= 0 and len(raw)-position >= 22, 'yaml_zip_directory')
    disk, start, disk_count, count, size, offset, comment = struct.unpack(
        '<4H2IH',raw[position+4:position+22])
    require(disk == start == 0 and disk_count == count and
            count <= limits['max_files']+3 and size <= 200_000 and
            offset+size == position and position+22+comment == len(raw),
            'yaml_zip_directory_bound')
    files, names, total = {}, set(), 0
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            infos = archive.infolist()
            require(len(infos) == count, 'yaml_zip_file_count')
            for member in infos:
                name = member.filename
                mode = member.external_attr >> 16
                require(name == member.orig_filename and name not in names and
                        not member.flag_bits & 1 and
                        member.compress_type in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED),
                        'yaml_zip_member')
                names.add(name)
                if member.is_dir():
                    require(name in {'candidate/','candidate/repositories/'} and
                            member.file_size == 0 and stat.S_IFMT(mode) in (0,stat.S_IFDIR),
                            'yaml_zip_directory_path')
                    continue
                require(stat.S_IFMT(mode) in (0,stat.S_IFREG) and not mode & 0o111,
                        'yaml_zip_mode')
                require(name in {'receipt.json','candidate/apps.yaml'} or
                        re.fullmatch(r'candidate/repositories/[1-9][0-9]*\.yaml',name),
                        'yaml_zip_path')
                require(len(files) < limits['max_files']+1, 'yaml_zip_file_bound')
                cap = limits['max_receipt_bytes'] if name == 'receipt.json' else limits['max_file_bytes']
                total += member.file_size
                require(member.file_size <= cap and
                        total <= limits['max_tree_bytes']+limits['max_receipt_bytes'],
                        'yaml_zip_member_bound')
                with archive.open(member) as stream:
                    body = stream.read(cap+1)
                require(len(body) == member.file_size and len(body) <= cap, 'yaml_zip_length')
                files[name] = body
    except (zipfile.BadZipFile,NotImplementedError,RuntimeError,EOFError):
        raise ValueError('yaml_zip_invalid') from None
    require('receipt.json' in files and 'candidate/apps.yaml' in files, 'yaml_zip_missing_file')
    receipt = files.pop('receipt.json')
    tree = {p.removeprefix('candidate/'):body for p,body in files.items()}
    require(len(tree) <= limits['max_files'] and
            sum(map(len,tree.values())) <= limits['max_tree_bytes'], 'yaml_tree_bound')
    return tree, receipt


def acquire(context, manifest_raw, revision, policy_raw, recipes, artifact_id,
            artifact_digest, token, output, *, repo):
    """Authenticate, decode and verify before creating any accepted output.

    Caller supplies trusted workflow context, upload artifact ID/digest and an
    already acquired exact-pin local prior. This does not infer branch absence,
    fetch prior state or mutate a publication ref.
    """
    from pathlib import Path
    limits = checked(context,manifest_raw,revision,policy_raw)
    destination = Path(output)
    require(not destination.exists() and not destination.is_symlink(), 'yaml_output_exists')
    tree, receipt = download_artifact(context,artifact_id,artifact_digest,token,
        artifact_name=f'yaml-bootstrap-{context["run_id"]}-{context["run_attempt"]}',
        zip_cap=archive_cap(limits),unpacker=lambda raw:unpack(raw,limits))
    verify(tree,receipt,context,manifest_raw,revision,policy_raw,recipes,repo=repo)
    stage(destination,tree,receipt,limits)
    return tree


def read_prior(repo, pin, limits):
    """Read only bounded canonical format-2 blobs at the exact fetched commit."""
    from pathlib import Path
    import tempfile
    from delivery import bounded, environment
    from yaml_staging import tree_documents

    require(type(pin) is str and re.fullmatch('[0-9a-f]{40}',pin), 'invalid_prior_pin')
    # Reuse credential-free isolated Git environment and bounded process I/O.
    with tempfile.TemporaryDirectory(prefix='yaml-local-git-') as scratch:
        env = environment(b'local',scratch,github=True)
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
    tree_documents(tree,limits)
    return tree


def fetch_prior(context, manifest_raw, revision, policy_raw, token, directory):
    """Require proven absence or exact remote format-2 pin; never convert format 1."""
    from delivery import fetch_pinned_repository
    limits = checked(context,manifest_raw,revision,policy_raw)
    pin = fetch_pinned_repository(context,token,directory)
    return None if pin is None else read_prior(directory,pin,limits)


def publish(context, manifest_raw, revision, policy_raw, recipes, artifact_id,
            artifact_digest, token, directory):
    """Inactive fixed-ref publisher candidate, invoked only by an explicit caller.

    Fetch/verify against one pin, construct its direct child, then require that
    exact pin at remote ref update. No retry/rebase, format conversion or repin.
    """
    from pathlib import Path
    from delivery import remote_git, URL, REMOTE_REF
    from publication import git, HISTORY_CAP
    from storage import canonical
    from yaml_publication import publish_local
    from yaml_staging import tree_documents

    limits = checked(context,manifest_raw,revision,policy_raw)
    root = Path(directory)
    root.mkdir(mode=0o700,exist_ok=False)
    repo = root/'git'
    fetch_prior(context,manifest_raw,revision,policy_raw,token,repo)
    tree = acquire(context,manifest_raw,revision,policy_raw,recipes,artifact_id,
                   artifact_digest,token,root/'artifact',repo=repo)
    apps, repositories = tree_documents(tree,limits)
    require(sum(p.stat().st_size for p in repo.rglob('*') if p.is_file()) +
            sum(map(len,tree.values())) <= HISTORY_CAP, 'yaml_publication_history_bound')
    parent = context.get('previous_publication') or None
    from yaml_adapter import schema_url
    commit = publish_local(repo,apps,repositories,schema=schema_url(revision),
                           max_file_bytes=limits['max_file_bytes'],expected_parent=parent)
    # Defensive ancestry assertion before the exact lease: the lease is not
    # permission to construct a replacement history or change another ref.
    parents = git(repo,'cat-file','-p',commit).split(b'\n\n',1)[0].splitlines()
    require([line[7:].decode() for line in parents if line.startswith(b'parent ')] ==
            ([parent] if parent else []), 'yaml_publication_parent')
    expected = parent or ''
    remote_git(repo,token,'push','--quiet',f'--force-with-lease={REMOTE_REF}:{expected}',
               URL,f'{commit}:{REMOTE_REF}')
    result = dict(commit=commit,parent=parent,ref=REMOTE_REF,source_revision=revision,
                  run_id=context['run_id'],run_attempt=context['run_attempt'],
                  artifact_id=artifact_id,artifact_digest=artifact_digest,
                  tree_bytes=sum(map(len,tree.values())))
    (root/'publication.json').write_bytes(canonical(result)+b'\n')
    return result
