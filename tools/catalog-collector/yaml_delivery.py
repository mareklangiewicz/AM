"""Inactive format-2 artifact acquisition candidate; no publication or token lookup."""
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
