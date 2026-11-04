"""Maintainer-only legacy layout rehearsal using already downloaded selected assets.

Creates a new private disposable directory; never installs, downloads, executes an
asset, or calls an embedded updater. Selection/consent must already be reviewed.
This is not a consumer interface or a production update/recovery transaction.
"""
import hashlib
import io
from datetime import datetime
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tarfile
import zipfile

from yaml_installed_migration import directory, regular

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT/'docs/track/release-catalog/research/yaml-host-rehearsal-20261104/legacy-updaters.json'
APPIMAGES = ('appimagetool', 'appimageupdatetool', 'logseq-app-db-nightly',
             'logseq-app-og', 'neovide', 'neovide-nightly', 'rclone-ui', 'satty')
TOOLS = ('emmylua_ls', 'emmylua_check', 'emmylua_doc_cli', 'luafmt')
SINGLES = ('fzf', 'lazygit', 'rclone', 'zellij', 'zmx')
# Private rehearsal limits; independent of and never increasing catalog caps.
MAX_FILES = 10000
MAX_BYTES = 512 * 1024 * 1024


def contracts(root=ROOT):
    rows = json.loads(AUDIT.read_text())['clients']
    expected = set(APPIMAGES + SINGLES + ('btop', 'kitty', 'emmylua', 'yt-dlp'))
    if len(rows) != 17 or {row['app'] for row in rows} != expected:
        raise ValueError('audited legacy scope changed')
    result = {}
    for row in rows:
        source = Path(root)/row['source_path']
        if regular(source)['sha256'] != row['source_sha256']:
            raise ValueError('audited source drift: '+row['app'])
        app = row['app']
        result[app] = dict(row, acquisition='direct-selected-asset',
            version_identity='published_at' if app == 'logseq-app-db-nightly' else 'url',
            refresh='explicit-reviewed-request-only',
            release_policy='pending-numeric-identity-list-and-channel-review',
            enrollment_ready=False, apply_ready=False,
            transition_requirements=[
                'Exact installed updater hash must match updater_sha256; app name is insufficient.',
                'Bind reviewed numeric source, release/channel rule, runtime and publication pins.',
                'Back up updater, recipe if present, version, binary/tree and affected launchers.',
                'Stage all selected assets before replacement; preserve launcher and supporting paths.',
                'Use durable intent/receipts and drift guards for every replaced path.',
                'Rehearse interrupted apply and rollback including binaries; recipe rollback is insufficient.',
                'Replace standalone updater explicitly; recipe-only migrator is ineligible.',
            ])
    return result


def relative(name):
    # Reject normalization ambiguities, traversal, Windows paths and control chars.
    if (not name or name.startswith('/') or '\\' in name or
            any(ord(c) < 32 or ord(c) == 127 for c in name)):
        raise ValueError('unsafe archive member')
    parts = name.rstrip('/').split('/')
    if any(p in ('', '.', '..') for p in parts):
        raise ValueError('unsafe archive member')
    return PurePosixPath(*parts)


def unpack(archive):
    """Return regular member bytes only; links/special files need explicit review."""
    files, permissions, seen, directories, total = {}, {}, set(), set(), 0

    def add(name, size, read, mode, directory=False):
        nonlocal total
        path = relative(name)
        if path in seen or len(seen) >= MAX_FILES:
            raise ValueError('duplicate member or file budget')
        seen.add(path)
        total += size
        if size < 0 or total > MAX_BYTES:
            raise ValueError('expanded archive byte budget')
        if directory:
            directories.add(path)
        else:
            data = read()
            if len(data) != size:
                raise ValueError('incomplete archive member')
            files[path.as_posix()] = data
            permissions[path.as_posix()] = 0o755 if mode & 0o111 else 0o644

    archive = io.BytesIO(archive) if isinstance(archive, bytes) else archive
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as stream:
            for member in stream.infolist():
                mode = member.external_attr >> 16
                if stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR):
                    raise ValueError('archive links/special files need separate review')
                add(member.filename, member.file_size,
                    lambda m=member: stream.read(m), mode, member.is_dir())
    else:
        if hasattr(archive, 'seek'):
            archive.seek(0)
        options = {'fileobj': archive} if hasattr(archive, 'read') else {'name': archive}
        with tarfile.open(mode='r:*', **options) as stream:
            for member in stream:
                if not (member.isfile() or member.isdir()):
                    raise ValueError('archive links/special files need separate review')
                add(member.name, member.size,
                    lambda m=member: stream.extractfile(m).read(), member.mode, member.isdir())
    if not files:
        raise ValueError('empty archive')
    for name in seen:
        if any(p.as_posix() in files for p in name.parents if str(p) != '.'):
            raise ValueError('file/directory member collision')
    for path in directories:
        if not any(name.startswith(path.as_posix()+'/') for name in files):
            raise ValueError('empty directory needs separate layout review')
    return files, permissions


def selected(value):
    # Accept the full reviewed Python selected-record result, not the six-line
    # handoff: Logseq needs published_at and EmmyLua needs same-release identity.
    for key in ('commit', 'repository_id', 'release_id', 'asset_id', 'observed_at',
                'published_at', 'tag', 'asset'):
        if key not in value:
            raise ValueError('incomplete selected record')
    if not re.fullmatch('[0-9a-f]{40}', value['commit']):
        raise ValueError('full publication pin required')
    for key in ('repository_id', 'release_id', 'asset_id'):
        if not re.fullmatch('[1-9][0-9]*', str(value[key])):
            raise ValueError('numeric selected identity required')
    for key in ('observed_at', 'published_at'):
        if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z', value[key]):
            raise ValueError('UTC identity required')
        datetime.strptime(value[key], '%Y-%m-%dT%H:%M:%SZ')
    if not value['asset']['url'].startswith('https://') or any(
            c in value['asset']['url'] for c in ('\n', '\r', '\t')):
        raise ValueError('selected HTTPS URL required')
    return value


def download_snapshot(path):
    """Bound the read and hash exactly the supplied bytes used for staging."""
    directory(path.parent)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or os.listxattr(stream.fileno()):
            raise ValueError('regular metadata-free download required')
        if info.st_size > MAX_BYTES:
            raise ValueError('download byte budget')
        data = stream.read(MAX_BYTES+1)
        after = os.fstat(stream.fileno())
        fields = ('st_size', 'st_mtime_ns', 'st_ctime_ns', 'st_mode', 'st_nlink')
        if (len(data) > MAX_BYTES or len(data) != info.st_size or
                any(getattr(after, key) != getattr(info, key) for key in fields)):
            raise ValueError('oversized or changing download')
    return data, dict(sha256=hashlib.sha256(data).hexdigest(), mode=stat.S_IMODE(info.st_mode),
                      uid=info.st_uid, gid=info.st_gid)


def stage(app, downloads, destination, root=ROOT):
    """downloads: {tool: {'selection': reviewed_record, 'path': local_download}}.

    Local file hashes describe staged bytes, NOT publisher authenticity or proof
    that the provided download came from its selected URL. No output is installable
    without subsequent source/policy review and an installed transition protocol.
    """
    contract = contracts(root)[app]
    keys = TOOLS if app == 'emmylua' else (app,)
    if set(downloads) != set(keys):
        raise ValueError('exact asset set required')
    records, payload, modes, inputs = {}, {}, {}, {}
    for key in keys:
        entry = downloads[key]
        value = selected(entry['selection'])
        records[key] = value
        path = Path(entry['path'])
        data, inputs[key] = download_snapshot(path)
        if app in APPIMAGES or app == 'yt-dlp':
            files = {app: data}
            file_modes = {app: 0o755}
            if not files[app]:
                raise ValueError('empty download')
        else:
            files, file_modes = unpack(data)
            if app == 'emmylua':
                if set(files) != {key}:
                    raise ValueError('tool archive must contain exact executable only')
            elif app == 'btop':
                if not all(n.startswith('btop/') for n in files):
                    raise ValueError('expected btop root directory')
                files = {n[len('btop/'):]: b for n, b in files.items()}
                file_modes = {n[len('btop/'):]: m for n, m in file_modes.items()}
                if 'bin/btop' not in files:
                    raise ValueError('missing bin/btop')
            elif app == 'kitty':
                if not {'bin/kitty', 'bin/kitten'} <= files.keys():
                    raise ValueError('expected kitty bin tree')
            elif app == 'rclone':
                prefixes = {n.split('/')[0] for n in files}
                if len(prefixes) != 1 or not all('/' in n for n in files):
                    raise ValueError('expected single rclone archive root')
                prefix = next(iter(prefixes))
                if not re.fullmatch(r'rclone-[A-Za-z0-9.+_-]+-linux-amd64', prefix):
                    raise ValueError('unexpected rclone root')
                files = {n[len(prefix)+1:]: b for n, b in files.items()}
                file_modes = {n[len(prefix)+1:]: m for n, m in file_modes.items()}
                if app not in files:
                    raise ValueError('missing rclone binary')
            elif app not in files:
                raise ValueError('missing exact binary entry')
        if payload.keys() & files.keys():
            raise ValueError('overlapping tool payloads')
        payload.update(files)
        modes.update(file_modes)
        if sum(map(len, payload.values())) > MAX_BYTES:
            raise ValueError('combined payload byte budget')
    if app == 'emmylua':
        fields = ('commit', 'repository_id', 'release_id', 'observed_at', 'published_at', 'tag')
        if len({tuple(str(r[f]) for f in fields) for r in records.values()}) != 1:
            raise ValueError('tool assets must belong to same selected release')
        if len({str(r['asset_id']) for r in records.values()}) != 4:
            raise ValueError('four distinct selected assets required')
    if app == 'logseq-app-db-nightly' and records[app]['tag'] != 'nightly':
        raise ValueError('Logseq nightly tag required')
    if app == 'neovide-nightly' and 'nightly' not in records[app]['asset']['url'].lower():
        raise ValueError('Neovide nightly URL gate required')
    executables = (set(TOOLS) if app == 'emmylua' else {'bin/btop'} if app == 'btop'
                   else {'bin/kitty', 'bin/kitten'} if app == 'kitty' else {app})
    # Keep supporting files; do not flatten/replace an existing installation.
    for name in payload:
        relative(name)
        if any(p.as_posix() in payload for p in PurePosixPath(name).parents if str(p) != '.'):
            raise ValueError('payload path collision')
        if name in executables:
            modes[name] = 0o755
    version = (records[keys[0]]['published_at'] if contract['version_identity'] == 'published_at'
               else records[keys[0]]['asset']['url'])
    report = dict(format=1, app=app, contract=contract, selections=records,
                  downloads=inputs, version=version, apply_ready=False,
                  payload={n: dict(sha256=hashlib.sha256(b).hexdigest(), mode=modes[n])
                           for n,b in payload.items()})
    destination = Path(destination)
    directory(destination.parent)
    # Exclusive creation: no cleanup/overwrite of caller-owned output on failure.
    # Partial output after an I/O error is disposable, never an applied transaction.
    destination.mkdir(mode=0o700)
    tree = destination/'payload'
    tree.mkdir(mode=0o700)
    for name, data in payload.items():
        target = tree/name
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with target.open('xb') as stream:
            stream.write(data)
        os.chmod(target, modes[name])
    (destination/'review.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app', required=True, choices=sorted(contracts()))
    parser.add_argument('--downloads', required=True, help='Trusted local JSON map of selected records and absolute download paths')
    parser.add_argument('--out', required=True, help='New absolute disposable directory')
    args = parser.parse_args()
    manifest = Path(args.downloads)
    regular(manifest)
    stage(args.app, json.loads(manifest.read_text()), args.out)


if __name__ == '__main__':
    main()
