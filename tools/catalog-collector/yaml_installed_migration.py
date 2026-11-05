"""Explicit maintainer-only recipe transactions; never runs an installed updater.

No discovery or default installation paths. Plans and transaction directories are
trusted local review artifacts, not a remote distribution/authentication format.
Run with exclusive control of the chosen installation and manager/module paths;
the advisory transaction lock does not lock ordinary AM updates/module sync.
"""
from installed_recipe import managed_updater

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile

RUNTIME = ('appimage.am', 'catalog.am', 'catalog-yaml.am',
           'catalog-yaml-reader.am', 'catalog-yaml-parser.am', 'catalog-yaml-policy.am')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def regular(path):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('absolute normalized paths required')
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise ValueError(f'symlink refused: {parent}')
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError(f'nonregular or hard-linked file: {path}')
    if os.listxattr(path):
        raise ValueError(f'extended metadata needs separate adapter: {path}')
    return dict(sha256=digest(path.read_bytes()), mode=stat.S_IMODE(info.st_mode),
                uid=info.st_uid, gid=info.st_gid)


def check(path, expected):
    if regular(path) != expected:
        raise ValueError(f'drift: {path}')


def directory(path):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('absolute normalized directory required')
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise ValueError(f'symlink directory refused: {parent}')
    if not path.is_dir():
        raise ValueError(f'missing directory: {path}')
    return path


def sync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic(path, data, metadata=None):
    """Data + metadata fsync, same-directory rename, directory fsync."""
    path = Path(path)
    directory(path.parent)
    fd, name = tempfile.mkstemp(prefix='.am-migration-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            if metadata:
                os.fchown(stream.fileno(), metadata['uid'], metadata['gid'])
                os.fchmod(stream.fileno(), metadata['mode'])
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        sync_dir(path.parent)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def write_json(path, value):
    atomic(path, (json.dumps(value, indent=2, sort_keys=True)+'\n').encode())


def blob(source, pin, name):
    return subprocess.run(['git', '-C', str(source), 'show', pin+':'+name],
                          check=True, capture_output=True).stdout


def prepare(source, source_pin, source_url, installation, recipe, replacement,
            manager, modules, publication_pin, selection, expected_old_sha256):
    """Inventory only selected paths. Caller must review binding and all hashes."""
    for pin in (source_pin, publication_pin):
        if not re.fullmatch('[0-9a-f]{40}', pin):
            raise ValueError('full source/publication commit required')
    if not re.fullmatch(r'https://raw\.githubusercontent\.com/[A-Za-z0-9-]+/[A-Za-z0-9_.-]+/'+source_pin, source_url):
        raise ValueError('AMREPO must name exact source commit')
    if not re.fullmatch(r'(x86_64|aarch64)/[a-z0-9][a-z0-9.+_-]*', recipe):
        raise ValueError('explicit supported architecture/app required')
    source = directory(source)
    regular(replacement)
    installation = directory(installation)
    modules = directory(modules)
    if installation.name != recipe.split('/')[1]:
        raise ValueError('installation/app mismatch')
    old = installation/'recipe.am'
    updater = installation/'AM-updater'
    expected_updater = managed_updater(old)
    if updater.read_bytes() != expected_updater:
        raise ValueError('unsupported managed updater')
    original = old.read_bytes()
    if digest(original) != expected_old_sha256:
        raise ValueError('installed recipe differs from reviewed legacy hash')
    new = Path(replacement).read_bytes()
    upstream = blob(source, source_pin, 'programs/'+recipe)
    for data in (original, new, upstream):
        if b'# AM-CATALOG-RECIPE 1\n' not in data:
            raise ValueError('unsupported recipe marker')
    if b'CATALOG_FORMAT=2\n' in original or b'CATALOG_FORMAT=2\n' not in new:
        raise ValueError('expected format-1 to format-2 transition')
    # Fully bound recipes are reviewed inputs. Check critical identities without
    # sourcing/evaluating arbitrary recipe code during planning or preflight.
    required = [f'APP={installation.name}', 'CATALOG_FORMAT=2',
                f'CATALOG_RECIPE="{recipe}"',
                'AMREPO=${AMREPO-"'+source_url+'"}',
                f'CATALOG_YAML_HELPER="{modules}/catalog-yaml.am"',
                f'. "{modules}/appimage.am"']
    lines = new.decode().splitlines()
    if any(lines.count(line) != 1 for line in required):
        raise ValueError('replacement lacks exact installed/source bindings')
    guards = {str(updater): regular(updater), str(manager): regular(manager)}
    if Path(manager).read_bytes() != blob(source, source_pin, 'APP-MANAGER'):
        raise ValueError('manager differs from exact source package')
    for name in RUNTIME:
        path = modules/name
        guards[str(path)] = regular(path)
        if path.read_bytes() != blob(source, source_pin, 'modules/'+name):
            raise ValueError('module differs from exact source package: '+name)
    for name in (installation.name, 'version'):
        path = installation/name
        guards[str(path)] = regular(path)
    fields = selection.splitlines()
    if len(fields) != 6 or fields[0] != publication_pin or not fields[5].startswith('https://'):
        raise ValueError('expected exact six-line selected-record output')
    for field in fields[1:4]:
        if not re.fullmatch('[0-9]+', field):
            raise ValueError('invalid selected identity')
    old_metadata = regular(old)
    if old_metadata['sha256'] == digest(new):
        raise ValueError('replacement unchanged')
    return dict(format=1, source_pin=source_pin, source_url=source_url,
                source_recipe_sha256=digest(upstream), recipe=recipe,
                target=str(old), old=old_metadata,
                new={**old_metadata, 'sha256':digest(new)},
                replacement=new.hex(), guards=guards, publication_pin=publication_pin,
                selection=selection)


def preflight(plan, accept, env=None):
    helper = next(path for path in plan['guards'] if path.endswith('/catalog-yaml.am'))
    args = ['sh', helper, plan['recipe'], '--commit', plan['publication_pin']]
    if accept:
        args += ['--accept-stale-release', *plan['selection'].splitlines()[:5]]
    clean_env = dict(os.environ if env is None else env)
    # Never reuse an unrelated command session or AMREPO from the caller.
    clean_env.pop('AM_CATALOG_SESSION', None)
    clean_env['AMREPO'] = plan['source_url']
    result = subprocess.run(args, env=clean_env, check=True, capture_output=True).stdout
    if result.decode() != plan['selection']:
        raise ValueError('selected record changed')


def guards(plan):
    for path, expected in plan['guards'].items():
        check(path, expected)


@contextlib.contextmanager
def locked(transaction):
    transaction = directory(transaction)
    info = transaction.stat()
    if info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != 0o700:
        raise ValueError('transaction directory must be private and caller-owned')
    lock = transaction/'lock'
    fd = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield transaction
    finally:
        os.close(fd)


def transact(plan, transaction, rollback=False, accept=False, env=None):
    """Resume from durable intent + exact backup after either atomic rename."""
    with locked(transaction) as tx:
        encoded = (json.dumps(plan, sort_keys=True)+'\n').encode()
        intent = tx/'intent.json'
        backup = tx/'recipe.before'
        receipt = tx/'receipt.json'
        target = Path(plan['target'])
        new = bytes.fromhex(plan['replacement'])
        if digest(new) != plan['new']['sha256']:
            raise ValueError('replacement hash mismatch')
        guards(plan)
        current = regular(target)
        if current not in (plan['old'], plan['new']):
            raise ValueError('recipe drift')
        if intent.exists():
            regular(intent)
            if intent.read_bytes() != encoded:
                raise ValueError('transaction belongs to another plan')
            regular(backup)
            if digest(backup.read_bytes()) != plan['old']['sha256']:
                raise ValueError('backup drift')
        else:
            if rollback or current != plan['old']:
                raise ValueError('missing apply intent')
            # Refuse leftover state instead of overwriting a backup after a crash.
            if receipt.exists():
                raise ValueError('receipt without intent')
            if backup.exists() or backup.is_symlink():
                regular(backup)
                if backup.read_bytes() != target.read_bytes():
                    raise ValueError('backup drift')
            preflight(plan, accept, env)
            guards(plan)
            check(target, plan['old'])
            atomic(backup, target.read_bytes())
            atomic(intent, encoded)
        record = None
        if receipt.exists():
            regular(receipt)
            record = json.loads(receipt.read_text())
            if record['plan_sha256'] != digest(encoded):
                raise ValueError('receipt belongs to another plan')
            if record['result'] == 'rolled-back':
                check(target, plan['old'])
                if not rollback:
                    raise ValueError('rolled-back transaction cannot reapply')
                return 'unchanged'
        rollback_intent = tx/'rollback.json'
        if rollback_intent.exists():
            regular(rollback_intent)
            if rollback_intent.read_bytes() != encoded:
                raise ValueError('rollback belongs to another plan')
            if not rollback:
                raise ValueError('rollback already started')
        else:
            if record and record['result'] == 'applied' and current != plan['new']:
                raise ValueError('applied recipe reverted without rollback intent')
            if rollback:
                atomic(rollback_intent, encoded)
        desired = plan['old'] if rollback else plan['new']
        if current != desired:
            if not rollback:
                preflight(plan, accept, env)
            guards(plan)
            check(target, current)
            atomic(target, backup.read_bytes() if rollback else new, desired)
        guards(plan)
        check(target, desired)
        write_json(receipt, dict(plan_sha256=digest(encoded),
                   source_pin=plan['source_pin'], publication_pin=plan['publication_pin'],
                   old=plan['old'], new=plan['new'], selection=plan['selection'],
                   result='rolled-back' if rollback else 'applied'))
        return 'unchanged' if current == desired else ('rolled-back' if rollback else 'applied')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prepare_parser = commands.add_parser('plan')
    for name in ('source', 'source-pin', 'source-url', 'installation', 'recipe',
                 'replacement', 'manager', 'modules', 'publication-pin', 'selection',
                 'expected-old-sha256', 'out'):
        prepare_parser.add_argument('--'+name, required=True)
    for action in ('apply', 'rollback'):
        command = commands.add_parser(action)
        command.add_argument('--plan', required=True)
        command.add_argument('--transaction', required=True)
        if action == 'apply':
            command.add_argument('--accept-stale-selection', action='store_true')
    args = vars(parser.parse_args())
    action = args.pop('command')
    if action == 'plan':
        out = Path(args.pop('out'))
        regular(args['selection'])
        args['selection'] = Path(args['selection']).read_text()
        if out.exists():
            raise ValueError('plan output already exists')
        write_json(out, prepare(**args))
    else:
        plan_path = Path(args.pop('plan'))
        regular(plan_path)
        print(transact(json.loads(plan_path.read_text()), args['transaction'],
                       rollback=action == 'rollback',
                       accept=args.get('accept_stale_selection', False)))


if __name__ == '__main__':
    main()
