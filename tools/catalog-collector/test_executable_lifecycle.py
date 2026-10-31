"""Shared executable lifecycle through trusted recipes and saved standalone updaters."""
from datetime import datetime, timedelta
import os
from pathlib import Path
import subprocess

from test_shell_consumer import ShellFixture, ROOT, HELPER, PIN, SOURCE
from test_utility_selectors import accepted_tree, ALIAS
from storage import validate
from shell_lookup import epoch


class ExecutableLifecycle(ShellFixture):
    @classmethod
    def setUpClass(cls):
        cls.base = accepted_tree()
        cls.index = validate(cls.base)
        cls.rid = cls.index['aliases'][ALIAS]['request_id']
        cls.obs = cls.index['entries'][cls.rid]['observation']

    def setUp(self):
        super().setUp()
        self.root = self.path/'apps with spaces'
        self.root.mkdir()
        self.launchers = self.path/'bin with spaces'
        self.desktop = self.path/'desktop sentinel'
        self.desktop.write_text('must not touch')
        self.now = [epoch(self.index['generated_at'])]*3
        self.script('wget', '''import os,pathlib,sys
p=pathlib.Path(os.environ['FIXTURE']); (p/'download').write_text(sys.argv[-1])
out=pathlib.Path(sys.argv[sys.argv.index('-O')+1])
if os.environ.get('DOWNLOAD_FAIL'):
    out.write_bytes(b'partial');sys.exit(9)
out.write_bytes(b'#!/bin/sh\\nexit 97 # Must never be executed by the lifecycle\\n')
''')
        self.script('notify-send', 'raise SystemExit(1)\n')
        self.recipe = self.path/'recipe'
        self.bind('x86_64', '7z')

    def bind(self, arch, app):
        self.app = self.root/app
        source = (ROOT/'programs'/arch/app).read_text()
        bindings = (f'AMREPO=${{AMREPO-"{SOURCE}"}}\nAPPS_DIR="{self.root}"\n'
                    f'BIN_DIR="{self.launchers}"\nDESKTOP_DIR="{self.desktop}"\n'
                    f'CATALOG_HELPER="{HELPER}"\n')
        source = source.replace('. "/opt/am/modules/appimage.am"',
                                bindings + f'. "{ROOT}/modules/appimage.am"')
        self.recipe.write_text(source)

    def invoke(self, path=None, env=None):
        self.stage()
        return subprocess.run(['sh', str(path or self.recipe), '--commit', PIN],
            cwd=self.path, env=env or self.env(), capture_output=True)

    def install(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.app/'AM-updater'

    def snapshot(self):
        return {str(p.relative_to(self.root)): ('link', os.readlink(p)) if p.is_symlink()
                else ('file',p.read_bytes(),p.stat().st_mode) if p.is_file()
                else ('directory',) for p in self.root.rglob('*')}

    def test_representative_identities_both_architectures_install_update_and_remove_without_execution(self):
        for arch in ('x86_64','aarch64'):
            for app in ('7z','arch','c++filt','ld.bfd'):
                with self.subTest(arch=arch,app=app):
                    self.bind(arch,app)
                    updater = self.install()
                    self.assertEqual(len(updater.read_text().splitlines()),3)
                    selected = (self.app/'version').read_text().strip()
                    self.assertIn('/'+arch+'-', selected)
                    self.assertEqual((self.path/'download').read_text(),selected)
                    self.assertTrue((self.launchers/app).samefile(self.app/app))
                    self.assertFalse((self.app/'icons').exists())
                    self.assertEqual(self.desktop.read_text(),'must not touch')
                    (self.path/'download').unlink()
                    result = self.invoke(updater)
                    self.assertEqual(result.returncode,0,result.stderr)
                    self.assertIn(b'Update not needed!',result.stdout)
                    self.assertFalse((self.path/'download').exists())
                    (self.app/'version').write_text('old\n')
                    result = self.invoke(updater)
                    self.assertEqual(result.returncode,0,result.stderr)
                    self.assertEqual((self.app/'version').read_text().strip(),selected)
                    result = subprocess.run(['sh',str(self.app/'remove')],capture_output=True)
                    self.assertEqual(result.returncode,0,result.stderr)
                    self.assertFalse(self.app.exists())
                    self.assertFalse((self.launchers/app).exists())
                    self.assertEqual(self.desktop.read_text(),'must not touch')

    def test_integrity_stale_and_empty_selector_refuse_before_app_mutation(self):
        for installed in (False, True):
            if installed:
                self.install()
                (self.app/'tmp').mkdir()
                (self.app/'tmp/interrupted').write_text('keep')
            before = self.snapshot()
            self.tree['bodies/'+self.rid+'.json'] = b'[]'
            result = self.invoke(self.app/'AM-updater' if installed else None)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(self.snapshot(),before)
            self.tree = dict(self.base)
            self.now = [epoch((datetime.fromisoformat(self.obs['validated_at'])+timedelta(hours=49)).isoformat())]*3
            result = self.invoke(self.app/'AM-updater' if installed else None)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(self.snapshot(),before)
            self.now = [epoch(self.index['generated_at'])]*3
        empty = self.path/'empty.am';empty.write_text("printf '[]\\n'\n")
        self.recipe.write_text(self.recipe.read_text().replace(str(HELPER),str(empty)))
        before = self.snapshot();result = self.invoke()
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(self.snapshot(),before)

    def test_transfer_chmod_and_move_failure_preserve_working_binary_and_retry(self):
        updater = self.install()
        original = (self.app/'7z').read_bytes()
        for failure in ('transfer','chmod','mv'):
            with self.subTest(failure=failure):
                (self.app/'version').write_text('old\n')
                if failure == 'transfer':
                    env = {**self.env(),'DOWNLOAD_FAIL':'1'}
                else:
                    self.script(failure,"raise SystemExit(9)\n")
                    env = self.env()
                result = self.invoke(updater,env=env)
                self.assertNotEqual(result.returncode,0)
                self.assertEqual((self.app/'7z').read_bytes(),original)
                self.assertEqual((self.app/'version').read_text(),'old\n')
                self.assertTrue((self.app/'tmp/7z').is_file())
                if failure != 'transfer': (self.bin/failure).unlink()
                result = self.invoke(updater)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertFalse((self.app/'tmp').exists())

    def test_version_write_failure_reports_partial_replacement_and_retry(self):
        updater = self.install()
        (self.app/'7z').write_bytes(b'old executable')
        (self.app/'version').unlink();(self.app/'version').mkdir()
        result = self.invoke(updater)
        self.assertNotEqual(result.returncode,0)
        self.assertNotEqual((self.app/'7z').read_bytes(),b'old executable')
        self.assertTrue((self.app/'version').is_dir())
        (self.app/'version').rmdir()
        result = self.invoke(updater)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue((self.app/'version').is_file())

    def test_equal_url_checksum_failure_repairs_binary(self):
        updater = self.install()
        binary = (self.app/'7z').read_bytes()
        (self.app/'7z').write_bytes(b'corrupt')
        (self.app/'AM-VERIFIED').write_text('Checksum failure\n')
        result = self.invoke(updater)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual((self.app/'7z').read_bytes(),binary)

    def test_invalid_identity_or_format_refuses_without_reading_catalog(self):
        source = self.recipe.read_text()
        for app in ('../escape','-option','.','..','a/b','a;command',''):
            self.recipe.write_text(source.replace('APP=7z\n',f"APP='{app}'\n"))
            before = self.snapshot()
            result = self.invoke()
            self.assertNotEqual(result.returncode,0)
            self.assertIn(b'Invalid app identity',result.stderr)
            self.assertEqual((self.path/'calls').read_text(),'')
            self.assertEqual(self.snapshot(),before)
        self.recipe.write_text(source.replace('PACKAGE_KIND=executable','PACKAGE_KIND=archive'))
        result = self.invoke()
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'Unsupported package format',result.stderr)
