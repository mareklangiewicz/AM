"""Preview or refresh one installed recipe and source snapshot, without reinstalling.

Run during exclusive maintenance: ordinary AM updates are not locked. Individual
metadata files replace by rename; the pair is not transactional. Backups support
manual recovery. No installed script is executed and no runtime module is synced.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile

from installed_recipe import bound_recipe, installed_bindings, managed_updater
from recipe_declarations import recipe_rows


def digest(body):
    return hashlib.sha256(body).hexdigest()


def regular(path):
    if path.resolve() != path.absolute() or not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError('expected regular non-symlink path: '+str(path))
    return path.read_bytes()


def prepare(source, pin, recipe, installation):
    if not re.fullmatch(r'[0-9a-f]{40}', pin):
        raise ValueError('full source commit required')
    actual = subprocess.check_output(['git', '-C', str(source), 'rev-parse', pin+'^{commit}'], text=True).strip()
    if actual != pin:
        raise ValueError('source pin must name a commit')
    if not re.fullmatch(r'(x86_64|aarch64|i686|armv7l)/[a-z0-9][a-z0-9_.+-]*', recipe):
        raise ValueError('invalid recipe identity')
    installation = installation.absolute()
    app = recipe.split('/')[1]
    path = installation/'recipe.am'
    snapshot = installation/'.am-installer'/app
    old, old_snapshot = regular(path), regular(snapshot)
    updater = installation/'AM-updater'
    updater_body = regular(updater)
    if updater_body != managed_updater(path):
        raise ValueError('unsupported managed updater')
    previous_source, paths = installed_bindings(old.decode())
    if Path(paths['APPS_DIR'])/app != installation:
        raise ValueError('installation binding mismatch')
    identities = re.findall(r'^CATALOG_RECIPE=(?:"([^"\n]+)"|([^\s"\n]+))$', old.decode(), re.M)
    if identities != [(recipe, '')] and identities != [('', recipe)]:
        raise ValueError('installed recipe identity mismatch')
    helpers = re.findall(r'^CATALOG_YAML_HELPER="([^"\n]+/catalog-yaml.am)"$', old.decode(), re.M)
    if len(helpers) != 1 or any(c in helpers[0] for c in '$`\\'):
        raise ValueError('unsupported installed helper binding')
    modules = Path(helpers[0]).parent
    if not modules.is_absolute():
        raise ValueError('absolute module binding required')
    entry = '. "'+str(modules/'appimage.am')+'"'
    if old.decode().splitlines().count(entry) != 1:
        raise ValueError('installed module/helper mismatch')
    # Keep configured repository ownership; only advance the source revision.
    match = re.fullmatch(r'(https://raw\.githubusercontent\.com/[A-Za-z0-9-]+/[A-Za-z0-9_.-]+)/.+', previous_source)
    if not match:
        raise ValueError('unsupported source ownership')
    body = subprocess.check_output(['git', '-C', str(source), 'show', pin+':programs/'+recipe])
    lines = body.decode().splitlines()
    if '# AM-RECIPE-DECLARATION 1' not in lines or 'CATALOG_FORMAT=3' not in lines:
        raise ValueError('complete YAML declaration required')
    # Parse declarations from the pinned source, not an unrelated working tree.
    with tempfile.TemporaryDirectory(prefix='am-refresh-source-') as temporary:
        root = Path(temporary)
        target = root/'programs'/recipe
        target.parent.mkdir(parents=True)
        target.write_bytes(body)
        row = recipe_rows(root)[0]
    if row['recipe'] != recipe:
        raise ValueError('source recipe identity mismatch')
    replacement = bound_recipe(body, match[1]+'/'+pin, paths, modules)
    subprocess.run(['sh', '-n'], input=replacement, check=True)
    changes = {path: (old, replacement), snapshot: (old_snapshot, body)}
    report = dict(source=pin, recipe=recipe, installation=str(installation),
                  source_url=match[1]+'/'+pin,
                  files={str(p): dict(before=digest(before), after=digest(after))
                         for p, (before, after) in changes.items()})
    return report, changes, updater_body


def apply(report, changes, updater, backup, expected_recipe, expected_snapshot):
    paths = list(changes)
    if [digest(changes[p][0]) for p in paths] != [expected_recipe, expected_snapshot]:
        raise ValueError('reviewed recipe/snapshot hashes required')
    installation = paths[0].parent
    if backup.absolute().is_relative_to(installation) or backup.resolve() != backup.absolute():
        raise ValueError('backup must be outside installation without symlinks')
    # Check every input before creating the backup or replacing any metadata.
    for path, (before, _) in changes.items():
        if regular(path) != before:
            raise ValueError('installed metadata drift: '+str(path))
    if regular(installation/'AM-updater') != updater:
        raise ValueError('updater drift')
    backup.mkdir(mode=0o700)
    for i, path in enumerate(paths):
        shutil.copy2(path, backup/('recipe.am' if i == 0 else 'source-recipe'))
    (backup/'refresh.json').write_text(json.dumps(report, indent=2)+'\n')
    for path, (_, after) in changes.items():
        info = path.stat()
        fd, temporary = tempfile.mkstemp(prefix='.am-refresh-', dir=path.parent)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(after)
                os.fchown(stream.fileno(), info.st_uid, info.st_gid)
                os.fchmod(stream.fileno(), stat.S_IMODE(info.st_mode))
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--recipe', required=True)
    parser.add_argument('--installation', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--backup', type=Path)
    parser.add_argument('--expect-recipe')
    parser.add_argument('--expect-snapshot')
    args = parser.parse_args()
    if args.apply and not args.backup:
        parser.error('--apply requires a new --backup directory')
    report, changes, updater = prepare(args.source, args.commit, args.recipe, args.installation)
    if args.apply:
        apply(report, changes, updater, args.backup, args.expect_recipe, args.expect_snapshot)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
