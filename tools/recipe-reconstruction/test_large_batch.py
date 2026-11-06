"""Replay retained batch evidence without network or downloaded application code.

Real desktop/icon bytes are inert fixtures. Only our authored extractor runs;
AppRun and the complete AppImage are never copied into the executable fixture.
"""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tarfile
import tempfile
import unittest

from originals import Catalogue, Originals

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / 'docs/track/release-catalog/research'
RECEIPT = RESEARCH / 'large-batch-evidence.json'


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def script(path, source):
    path.write_text('#!/bin/sh\nset -eu\n' + source)
    path.chmod(0o755)


def closed_commands(directory):
    directory.mkdir()
    for name in ('sh', 'cat', 'sed', 'grep', 'head', 'mkdir', 'mktemp', 'rm',
                 'chmod', 'mv', 'cp', 'ln', 'readlink', 'wc', 'awk', 'dirname'):
        source = shutil.which(name)
        if source is None:
            raise AssertionError('required test command missing: ' + name)
        (directory / name).symlink_to(source)
    return {**os.environ, 'LC_ALL': 'C', 'PATH': str(directory)}


class LargeBatch(unittest.TestCase):
    receipt_path = RECEIPT

    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(cls.receipt_path.read_text())
        archive = RESEARCH / cls.receipt['evidence_archive']
        if sha256(archive.read_bytes()) != cls.receipt['evidence_archive_sha256']:
            raise AssertionError('batch evidence archive digest mismatch')
        cls.archive = tarfile.open(archive)
        cls.addClassCleanup(cls.archive.close)
        cls.members = {}
        for member in cls.archive.getmembers():
            name = PurePosixPath(member.name)
            if name.is_absolute() or '..' in name.parts or member.name in cls.members:
                raise AssertionError('unsafe or repeated evidence member: ' + member.name)
            if not (member.isdir() or member.isfile() or member.issym()):
                raise AssertionError('unsupported evidence member: ' + member.name)
            cls.members[member.name] = member
        candidates = cls.receipt['candidates']
        cls.rows = {row['app']: row for row in candidates}
        if len(cls.rows) != len(candidates):
            raise AssertionError('duplicate candidate identity')
        cls.converted = cls.receipt['converted']
        if not cls.converted or len(set(cls.converted)) != len(cls.converted):
            raise AssertionError('converted batch must be nonempty and unique')
        if not set(cls.converted) <= cls.rows.keys():
            raise AssertionError('converted recipe missing evidence')

    @classmethod
    def evidence(cls, app, name):
        member = cls.members[app + '/' + name]
        if not member.isfile() or member.size > 32 * 1024 * 1024:
            raise AssertionError('invalid regular evidence file: ' + member.name)
        return cls.archive.extractfile(member).read()

    def test_source_identity_reconstruction_and_saved_selector_winners(self):
        originals = Originals(ROOT)
        revisions = sorted({match['template'].split(':', 1)[0]
                            for row in self.rows.values()
                            for match in row['provenance']['matches']})
        catalogue = Catalogue(originals, revisions)
        with tempfile.TemporaryDirectory(prefix='am-large-source-') as temporary:
            home = Path(temporary)
            commands = home / 'bin'
            env = closed_commands(commands)
            script(commands / 'curl', 'cat "$ASSESS_RESPONSE"\n')
            for app in self.converted:
                with self.subTest(app=app):
                    row = self.rows[app]
                    provenance = row['provenance']
                    source = originals.read(provenance['source_commit'], provenance['recipe'])
                    self.assertEqual(sha256(source.encode()), provenance['source_sha256'])
                    checked = catalogue.check(source)
                    self.assertEqual(checked['status'], 'instance')
                    match = provenance['matches'][0]
                    self.assertEqual(catalogue.render(match['template'], match['parameters']), source)
                    self.assertEqual(match['parameters'][:3], match['parameters'][3:])
                    template_revision, template_path = match['template'].split(':', 1)
                    self.assertEqual(sha256(originals.read(template_revision, template_path).encode()),
                                     match['source_sha256'])
                    raw = self.evidence(app, 'releases.json')
                    self.assertEqual(sha256(raw), row['releases_sha256'])
                    response = home / 'response.json'
                    response.write_bytes(raw)
                    selected = subprocess.run(['sh', '-c', match['parameters'][2]],
                        env={**env, 'ASSESS_RESPONSE': str(response)},
                        capture_output=True, text=True, timeout=10)
                    self.assertEqual(selected.returncode, 0, selected.stderr)
                    self.assertEqual(selected.stdout.strip(), row['old_selected_url'])
                    self.assertEqual(row['old_selected_url'],
                                     row['selected_asset']['browser_download_url'])
                    repository = self.evidence(app, 'repository.json')
                    self.assertEqual(sha256(repository), row['repository_sha256'])
                    repository = json.loads(repository)
                    self.assertEqual(repository['id'], row['repository_id'])
                    self.assertEqual(repository['full_name'], row['repository'])
                    payload = json.loads(self.evidence(app, 'payload-receipt.json'))
                    self.assertEqual(payload['status'], 'verified')
                    asset = row['selected_asset']
                    self.assertEqual(payload['asset_id'], asset['id'])
                    self.assertEqual(payload['release_id'], row['selected_release'])
                    self.assertEqual(payload['bytes'], asset['size'])
                    self.assertEqual('sha256:' + payload['sha256'], asset['digest'])
                    self.assertEqual(payload['url'], asset['browser_download_url'])

    def test_maintained_selectors_replay_full_saved_responses(self):
        for app in self.converted:
            with self.subTest(app=app):
                row = self.rows[app]
                now = row['observed_at'][:19] + 'Z'
                facts = ''
                releases = json.loads(self.evidence(app, 'releases.json'))
                for release in releases:
                    for asset in release['assets']:
                        facts += '\t'.join([str(release['id']), str(asset['id']),
                            *map(json.dumps, [now, release['published_at'], release['tag_name'],
                                asset['name'], asset['browser_download_url']]),
                            json.dumps(release['prerelease'])]) + '\n'
                for command in (['mawk'], ['gawk'], ['busybox', 'awk']):
                    with self.subTest(command=command):
                        result = subprocess.run([*command, '-f',
                            str(ROOT / 'modules/catalog-yaml-policy.am')], input=facts,
                            text=True, capture_output=True, timeout=15,
                            env={**os.environ, 'LC_ALL': 'C',
                                 'AM_YAML_RECIPE': 'x86_64/' + app,
                                 'AM_YAML_REPOSITORY': str(row['repository_id']),
                                 'AM_YAML_NOW': now, 'AM_YAML_PIN': 'a' * 40})
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(result.stdout.splitlines()[-1],
                                         row['selected_asset']['browser_download_url'])

    def metadata_fixture(self, app, destination):
        static = json.loads(self.evidence(app, 'static.json'))
        self.assertEqual(static['status'], 'compatible')
        self.assertEqual(len(static['root_desktops']), 1)
        destination.mkdir()
        # Construct regular files before relative links; never extract AppRun.
        records = static['files']
        for record in records:
            name = record['path']
            path = PurePosixPath(name)
            self.assertFalse(path.is_absolute())
            self.assertNotIn('..', path.parts)
            member = self.members[app + '/metadata/' + name]
            if 'symlink' in record:
                self.assertTrue(member.issym())
                self.assertEqual(member.linkname, record['symlink'])
                target = PurePosixPath(member.linkname)
                self.assertFalse(target.is_absolute())
                self.assertNotIn('..', target.parts)
            else:
                data = self.evidence(app, 'metadata/' + name)
                self.assertEqual(len(data), record['bytes'])
                self.assertEqual(sha256(data), record['sha256'])
                if name != 'AppRun':
                    target = destination / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
                    target.chmod(0o644)
        for record in records:
            if 'symlink' in record and record['path'] != 'AppRun':
                target = destination / record['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                target.symlink_to(record['symlink'])
        self.assertFalse((destination / 'AppRun').exists())
        self.assertEqual((destination / static['desktop_chain'][-1]).read_text(),
                         static['desktop_text'])
        self.assertEqual(sha256((destination / static['icon_chain'][-1]).read_bytes()),
                         static['icon_sha256'])
        return static

    def test_actual_converted_recipes_inert_install_update_and_removal(self):
        for app in self.converted:
            with self.subTest(app=app), tempfile.TemporaryDirectory(prefix='am-large-life-') as temporary:
                home = Path(temporary)
                commands = home / 'bin'
                env = closed_commands(commands)
                metadata = home / 'metadata'
                static = self.metadata_fixture(app, metadata)
                helper = home / 'select'
                script(helper, 'cat "$ASSESS_SELECTION"\n')
                selection = home / 'selection'
                url = self.rows[app]['selected_asset']['browser_download_url']
                selection.write_text('a' * 40 + '\n1\n1\n1\n' +
                                     self.rows[app]['observed_at'][:19] + 'Z\n' + url + '\n')
                recipe = home / 'candidate'
                source = (ROOT / 'programs/x86_64' / app).read_text()
                self.assertIn('# AM-RECIPE-DECLARATION 1', source)
                self.assertIn('PACKAGE_LAYOUT=raw', source)
                recipe.write_text(source.replace('/opt/am/modules/appimage.am',
                                                 str(ROOT / 'modules/appimage.am')))
                payload = home / 'payload'
                script(payload, '''[ "$1" = --appimage-extract ] || exit 95
mkdir -p squashfs-root
case "$2" in
 '*.desktop') cp -a "$ASSESS_METADATA"/*.desktop squashfs-root/ ;;
 *) mkdir -p "squashfs-root/$(dirname "$2")"
    cp -a "$ASSESS_METADATA/$2" "squashfs-root/$2" ;;
esac
''')
                script(commands / 'wget', '''echo wget >> "$ASSESS_LOG"
[ "$1" = -O ] || exit 94
cp "$ASSESS_PAYLOAD" "$2"
''')
                script(commands / 'curl', 'exit 98\n')
                script(commands / 'appimageupdatetool', 'exit 99\n')
                env.update(APPS_DIR=str(home / 'apps'), BIN_DIR=str(home / 'links'),
                    DESKTOP_DIR=str(home / 'desktops'), CATALOG_YAML_HELPER=str(helper),
                    ASSESS_SELECTION=str(selection), ASSESS_METADATA=str(metadata),
                    ASSESS_PAYLOAD=str(payload), ASSESS_LOG=str(home / 'calls'))
                def run(path, *args):
                    result = subprocess.run(['sh', str(path), *args], env=env,
                                            capture_output=True, timeout=15)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    return result
                run(recipe)
                installed = home / 'apps' / app
                desktop = home / 'desktops' / (app + '-AM.desktop')
                icon = installed / 'icons' / app
                self.assertFalse(icon.is_symlink())
                self.assertEqual(sha256(icon.read_bytes()), static['icon_sha256'])
                # Compare original versus converted desktop transformations on
                # the actual saved bytes, with the disposable icon path mapped.
                expected = re.sub(r'Exec=[^ \n]*', 'Exec=' + app, static['desktop_text'])
                expected = re.sub(r'Icon=.*', 'Icon=' + str(icon), expected)
                expected = expected.replace(' --no-sandbox', '')
                self.assertEqual(desktop.read_text(), expected)
                self.assertEqual((home / 'links' / app).resolve(), installed / app)
                self.assertEqual((installed / app).read_bytes(), payload.read_bytes())
                self.assertEqual((installed / 'version').read_text(), url + '\n')
                self.assertEqual((home / 'calls').read_text(), 'wget\n')
                unchanged = run(installed / 'AM-updater')
                self.assertIn(b'Update not needed!', unchanged.stdout)
                self.assertEqual((home / 'calls').read_text(), 'wget\n')
                (installed / 'data').write_text('preserve app data')
                desktop.write_text('preserve custom desktop')
                with payload.open('a') as output:
                    output.write('# next authored fixture version\n')
                updated_url = url + '?batch-fixture=2'
                selection.write_text(selection.read_text().replace(url, updated_url))
                run(installed / 'AM-updater')
                self.assertEqual((installed / app).read_bytes(), payload.read_bytes())
                self.assertEqual((installed / 'version').read_text(), updated_url + '\n')
                self.assertEqual((installed / 'data').read_text(), 'preserve app data')
                self.assertEqual(desktop.read_text(), 'preserve custom desktop')
                self.assertEqual((home / 'calls').read_text(), 'wget\nwget\n')
                run(installed / 'remove')
                self.assertFalse(installed.exists())
                self.assertFalse(desktop.exists())
                self.assertFalse((home / 'links' / app).is_symlink())


if __name__ == '__main__':
    unittest.main()
