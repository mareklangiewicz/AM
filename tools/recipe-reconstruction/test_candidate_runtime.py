"""Offline assessment, not conversion approval, of the ticket-126 candidates.

Only the extracted, classified selector runs from upstream. Installer tests run
our maintained module with authored inert assets and a stub selection protocol.
All paths and transfers are confined to a TemporaryDirectory.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from originals import Catalogue, Originals

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/catalog-collector'))
import recipe_policy_source as compiler

REVISION = 'bbffd15c19d01ef9124fbf99b5b9c41d2661ea22'
CANDIDATES = {
    '20x': ('peakflo/20x', 'f10790639ac193a1ecbcdc81824a8a22d9577906c80f4403d616a990069f7f31'),
    '2fac': ('jeonjw85/2fac', '745b2c7ccd3dde951452ea86cfa33986b78f458c89b45b85ee0cdd7a82a9b0c5'),
    '4nier-patrimonio': ('4nier-app/patrimonio', '36ea29727167c231ac7fc2fb61d770c9a2622eccec258e726a1f26edce89a8ff'),
}
# Exploratory policy: case-insensitive suffix, any release channel. Intentionally
# exposes the current name/URL and armhf gaps, rather than claiming equivalence.
PATTERN = '^.*[.][Aa][Pp][Pp][Ii][Mm][Aa][Gg][Ee]$'
NOW = '2026-11-06T12:00:00Z'


def script(path, source):
    path.write_text('#!/bin/sh\nset -eu\n'+source)
    path.chmod(0o755)


def declaration(app, repository, number):
    return f'''#!/bin/sh
# AM-RECIPE-DECLARATION 1
set -eu
APP={app}
CATALOG_FORMAT=2
CATALOG_RECIPE=x86_64/{app}
CATALOG_REPOSITORY_ID={number}
CATALOG_REPOSITORY={repository}
CATALOG_CHANNEL=any
CATALOG_ASSET_PATTERN='{PATTERN}'
# shellcheck source=modules/appimage.am
. "$ASSESS_MODULE"
am_appimage "$0" "$@"
'''


class CandidateRuntime(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='am-126-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.bin = self.root/'bin'; self.bin.mkdir()
        self.env = {**os.environ, 'LC_ALL': 'C', 'PATH': str(self.bin),
                    'ASSESS_MODULE': str(ROOT/'modules/appimage.am')}
        # A closed command directory: network tools below are always stubs.
        for name in ('sh','cat','sed','grep','head','mkdir','mktemp','rm','chmod',
                     'mv','cp','ln','readlink','wc','tar','gzip','unzip','awk'):
            command = shutil.which(name)
            if command:
                (self.bin/name).symlink_to(command)
        script(self.bin/'curl', 'cat "$ASSESS_RESPONSE"\n')
        script(self.bin/'wget', 'exit 97\n')
        self.originals = Originals(ROOT)
        self.catalogue = Catalogue(self.originals, [REVISION])
        self.policy_root = self.root/'policy'
        (self.policy_root/'modules').mkdir(parents=True)
        shutil.copy2(ROOT/'modules/catalog-yaml-policy.am', self.policy_root/'modules')
        for number, (app, (repository, _)) in enumerate(CANDIDATES.items(), 1):
            path = self.policy_root/'programs/x86_64'/app
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(declaration(app, repository, number))
        with patch.object(compiler, 'ROOT', self.policy_root):
            compiler.generate()

    def asset(self, name='App-x86_64.AppImage', url=None, aid='1'):
        return dict(id=aid, name=name, browser_download_url=url or
                    'https://example.invalid/releases/download/v1/'+name)

    def release(self, assets, rid='1', published='2026-11-05T00:00:00Z', preview=False):
        return dict(id=rid, published_at=published, tag_name='v'+rid,
                    prerelease=preview, assets=assets)

    def old_select(self, app, releases):
        source = self.originals.read(REVISION, 'programs/x86_64/'+app)
        self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), CANDIDATES[app][1])
        match = self.catalogue.check(source)
        self.assertEqual(match['status'], 'instance')
        expression = match['matches'][0]['parameters'][2]
        response = self.root/'response.json'; response.write_text(json.dumps(releases))
        result = subprocess.run(['sh', '-c', expression], env={**self.env,
            'ASSESS_RESPONSE': str(response)}, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip() or None

    def new_select(self, app, releases, **extra):
        facts = ''
        for release in releases:
            for asset in release['assets']:
                facts += '\t'.join([release['id'],asset['id'],*map(json.dumps,[
                    NOW,release['published_at'],release['tag_name'],asset['name'],
                    asset['browser_download_url']]),json.dumps(release['prerelease'])])+'\n'
        number = list(CANDIDATES).index(app)+1
        result = subprocess.run(['awk', '-f', str(self.policy_root/'modules/catalog-yaml-policy.am')],
            input=facts, text=True, capture_output=True, timeout=10, env={**self.env,
                'AM_YAML_RECIPE': 'x86_64/'+app, 'AM_YAML_REPOSITORY': str(number),
                'AM_YAML_PIN': 'a'*40, 'AM_YAML_NOW': NOW, **extra})
        if result.returncode:
            self.assertEqual(result.stdout, '')
            return None
        return result.stdout.splitlines()[-1]

    def test_selection_agreements_and_policy_differences(self):
        a = self.asset(); url = a['browser_download_url']
        z = self.asset('z.AppImage'); b = self.asset('a.AppImage', aid='2')
        preview = self.asset('Preview.AppImage')
        cases = [
            ('one asset', [self.release([a])], None, url, url),
            ('release order', [self.release([a]), self.release([z], '2', '2026-11-06T00:00:00Z')],
             None, url, z['browser_download_url']),
            ('asset order', [self.release([z,b])], None, z['browser_download_url'], b['browser_download_url']),
            ('prerelease allowed', [self.release([preview], preview=True)], None,
             preview['browser_download_url'], preview['browser_download_url']),
            ('arm64 rejected', [self.release([self.asset('App-arm64.AppImage'),a])], None, url,url),
            ('name differs from URL', [self.release([self.asset('App-arm64.AppImage',url)])], None,url,None),
            ('URL tag excludes arch', [self.release([self.asset(url=url.replace('/v1/','/arm64/'))])],
             None,None,url.replace('/v1/','/arm64/')),
            ('uppercase suffix', [self.release([self.asset('App.APPIMAGE')])], None,
             self.asset('App.APPIMAGE')['browser_download_url'],self.asset('App.APPIMAGE')['browser_download_url']),
            ('no matching asset', [self.release([self.asset('checksum.txt')])], None,None,None),
            ('empty response', [], None,None,None),
            ('missing assets fallthrough', [self.release([], '2'),self.release([a])],None,url,url),
            ('retained outside page', [], [self.release([a])],None,url),
            ('OS exclusion', [self.release([self.asset('App-windows.AppImage')])],None,
             self.asset('App-windows.AppImage')['browser_download_url'],None),
            ('armhf gap', [self.release([self.asset('App-armhf.AppImage')])],None,None,
             self.asset('App-armhf.AppImage')['browser_download_url']),
        ]
        for app in CANDIDATES:
            for name, response, retained, old, new in cases:
                with self.subTest(app=app, case=name):
                    self.assertEqual(self.old_select(app,response),old)
                    self.assertEqual(self.new_select(app,response if retained is None else retained),new)

    def lifecycle(self, app):
        home = self.root/app; home.mkdir()
        helper = home/'select'
        script(helper, 'cat "$ASSESS_SELECTION"\n')
        selection = home/'selection'
        url = 'https://example.invalid/releases/download/v1/App.AppImage'
        selection.write_text('a'*40+'\n1\n1\n1\n'+NOW+'\n'+url+'\n')
        recipe = home/'candidate'
        recipe.write_text(declaration(app, CANDIDATES[app][0], 1))
        env = {**self.env, 'APPS_DIR':str(home/'apps'), 'BIN_DIR':str(home/'links'),
               'DESKTOP_DIR':str(home/'desktops'), 'CATALOG_YAML_HELPER':str(helper),
               'ASSESS_SELECTION':str(selection), 'ASSESS_PAYLOAD':str(home/'payload'),
               'ASSESS_LOG':str(home/'calls')}
        # No payload from the network. This authored program only writes fixture
        # desktop/icon data when our module asks it to extract those members.
        script(home/'payload', '''[ "$1" = --appimage-extract ] || exit 95
mkdir -p squashfs-root
case "$2" in
 '*.desktop') printf '[Desktop Entry]\\nExec=upstream --no-sandbox\\nIcon=upstream\\n' > squashfs-root/app.desktop;;
 .DirIcon) printf fixture-icon > squashfs-root/.DirIcon;;
 *) exit 96;;
esac
''')
        script(self.bin/'wget', '''echo wget >> "$ASSESS_LOG"
[ "$1" = -O ] || exit 94
cp "$ASSESS_PAYLOAD" "$2"
''')
        script(self.bin/'curl', 'exit 98\n')
        script(self.bin/'appimageupdatetool', 'echo appimageupdatetool >> "$ASSESS_LOG"\nexit 0\n')
        return home,recipe,env

    def test_selection_refuses_stale_and_wrong_repository(self):
        releases = [self.release([self.asset()])]
        for app in CANDIDATES:
            with self.subTest(app=app):
                self.assertIsNone(self.new_select(app, releases,
                    AM_YAML_NOW='2026-11-09T12:00:00Z'))
                self.assertIsNone(self.new_select(app, releases, AM_YAML_REPOSITORY='999'))

    def run_recipe(self, recipe, env, *args):
        return subprocess.run(['sh', str(recipe), *args], env=env, capture_output=True, timeout=10)

    def test_direct_install_standalone_update_preservation_and_remover(self):
        for app in CANDIDATES:
            with self.subTest(app=app):
                home,recipe,env = self.lifecycle(app)
                result = self.run_recipe(recipe,env)
                self.assertEqual(result.returncode,0,result.stderr)
                installed = home/'apps'/app
                self.assertEqual((installed/'icons'/app).read_text(),'fixture-icon')
                desktop = home/'desktops'/f'{app}-AM.desktop'
                self.assertIn(f'Exec={app} --no-sandbox',desktop.read_text())
                self.assertEqual((home/'links'/app).resolve(),installed/app)
                self.assertEqual((home/'calls').read_text(),'wget\n')
                # Updater uses recorded URL to skip transfer, even with a tool present.
                result = self.run_recipe(installed/'AM-updater',env)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertIn(b'Update not needed!',result.stdout)
                (installed/'data').write_text('preserve')
                desktop.write_text('custom desktop')
                old = (installed/app).read_bytes()
                with (home/'payload').open('a') as output: output.write('# second asset\n')
                path = home/'selection'; path.write_text(path.read_text().replace('/v1/','/v2/'))
                result = self.run_recipe(installed/'AM-updater',env)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertNotEqual((installed/app).read_bytes(),old)
                self.assertEqual((installed/'data').read_text(),'preserve')
                self.assertEqual(desktop.read_text(),'custom desktop')
                self.assertFalse((installed/(app+'.~1~')).exists())
                self.assertNotIn('appimageupdatetool',(home/'calls').read_text())
                # Reinstall also preserves an existing desktop and custom command.
                link = home/'links'/app; link.unlink();link.write_text('custom command')
                result = self.run_recipe(recipe,env)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual(link.read_text(),'custom command')
                self.assertEqual(desktop.read_text(),'custom desktop')
                remover = self.run_recipe(installed/'remove',env)
                self.assertEqual(remover.returncode,0,remover.stderr)
                self.assertFalse(installed.exists());self.assertFalse(desktop.exists())
                self.assertFalse(link.exists())  # Primary command removal is unconditional.

    def test_failed_transfer_and_empty_asset_preserve_existing_install(self):
        for app in CANDIDATES:
            with self.subTest(app=app):
                home,recipe,env = self.lifecycle(app)
                self.assertEqual(self.run_recipe(recipe,env).returncode,0)
                installed=home/'apps'/app
                before={p.name:p.read_bytes() for p in installed.iterdir() if p.is_file()}
                selection=home/'selection';selection.write_text(selection.read_text().replace('/v1/','/v2/'))
                for payload in ('exit 9\n', ': > "$2"\n'):
                    script(self.bin/'wget',payload)
                    result=self.run_recipe(installed/'AM-updater',env)
                    self.assertNotEqual(result.returncode,0)
                    self.assertEqual({p.name:p.read_bytes() for p in installed.iterdir() if p.is_file()},before)
                    self.assertFalse(list(installed.glob('.am-stage.*')))
                script(home/'select','exit 3\n')
                result=self.run_recipe(installed/'AM-updater',env)
                self.assertNotEqual(result.returncode,0)
                self.assertEqual({p.name:p.read_bytes() for p in installed.iterdir() if p.is_file()},before)

    def test_archive_staging_requires_explicit_layout_and_root(self):
        home,recipe,env=self.lifecycle('20x')
        payload=home/'payload';archive=home/'bundle.tar.gz'
        with tarfile.open(archive,'w:gz') as output: output.add(payload,arcname='bundle/20x')
        # Direct raw installation has no archive autodetection: it stores bytes.
        env['ASSESS_PAYLOAD']=str(archive)
        desktop=home/'desktops';desktop.mkdir();(desktop/'20x-AM.desktop').write_text('existing')
        result=self.run_recipe(recipe,env)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual((home/'apps/20x/20x').read_bytes(),archive.read_bytes())
        recipe.write_text(recipe.read_text().replace('CATALOG_FORMAT=2',
            'PACKAGE_LAYOUT=tar\nARCHIVE_ROOT=bundle\nCATALOG_FORMAT=2'))
        result=self.run_recipe(recipe,env)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual((home/'apps/20x/20x').read_bytes(),payload.read_bytes())
        # Wrong root refuses staging without replacing the existing executable.
        recipe.write_text(recipe.read_text().replace('ARCHIVE_ROOT=bundle','ARCHIVE_ROOT=missing'))
        before=(home/'apps/20x/20x').read_bytes()
        result=self.run_recipe(recipe,env)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual((home/'apps/20x/20x').read_bytes(),before)


if __name__ == '__main__':
    unittest.main()
