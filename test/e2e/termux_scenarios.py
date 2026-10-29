"""Native Termux layout and non-root commands; no FHS compatibility symlinks."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

from filesystem import fingerprint_files, snapshot_tree

import scenarios as shared
from scenarios import OUT, USER, SOURCE, PIN, SQLITE, retained, render, validate


class TermuxCLI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert os.getuid() == USER.pw_uid != 0
        assert not Path('/bin').exists() and not Path('/usr').exists()
        retained.StorageContract.setUpClass()
        cls.tree=dict(retained.StorageContract.base)
        cls.tree['lookup.tsv']=render(validate(cls.tree),cls.tree['index.json'])
        cls.index=validate(cls.tree)
        cls.manager_hash = fingerprint_files(Path('/src'), ['APP-MANAGER'])['APP-MANAGER']
        cls.module_hashes = fingerprint_files(Path('/src/modules'),
                                            [p.name for p in Path('/src/modules').glob('*.am')])
        inputs=['APP-MANAGER','test/e2e/Containerfile.termux','test/e2e/termux-test.sh',
                'test/e2e/termux_scenarios.py','test/e2e/scenarios.py','test/e2e/external.py',
                'test/e2e/filesystem.py','test/e2e/transport_args.py','test/e2e/transport_records.py',
                'test/e2e/run','test/e2e/fixtures/e2e-legacy','programs/x86_64/sqlitebrowser','programs/x86_64/obsidian',
                'docs/track/release-catalog/design/staged-manifest.json',
                'docs/track/release-catalog/research/supervised-baseline-40529551070-evidence.tar.gz']
        (OUT/'tested-source.json').write_text(json.dumps({
            'inputs':fingerprint_files(Path('/src'), inputs),
            'modules':cls.module_hashes},indent=2)+'\n')
        (OUT/'user-environment.json').write_text(json.dumps({
            'uid':os.getuid(),'gid':os.getgid(),'prefix':os.environ['PREFIX'],
            'termux_exec':os.environ['LD_PRELOAD'],'bin_exists':Path('/bin').exists(),
            'usr_exists':Path('/usr').exists(),'sudo':shutil.which('sudo'),
            'architecture':os.uname().machine,'python':sys.version},indent=2)+'\n')

    setUp=shared.InstalledCLI.setUp
    tearDown=shared.InstalledCLI.tearDown
    configure=shared.InstalledCLI.configure
    prepare_home=shared.InstalledCLI.prepare_home
    command=shared.InstalledCLI.command
    test_unprivileged_appman_install_and_standalone_source=shared.InstalledCLI.test_unprivileged_appman_install_and_standalone_source
    test_remove_reinstall_preserves_user_configuration=shared.InstalledCLI.test_remove_reinstall_preserves_user_configuration

    def appman(self):
        self.prepare_home(self.home,appman=True)
        return str(self.home/'Applications/appman/appman')

    def test_local_am_automatically_uses_appman_paths(self):
        self.appman()
        executable=self.home/'.local/bin/am'
        shutil.copy2('/src/APP-MANAGER',executable)
        self.command('-i','sqlitebrowser',executable=str(executable))
        app=self.home/'Applications/sqlitebrowser'
        self.assertEqual((app/'version').read_text().strip(),SQLITE)
        self.assertTrue((self.home/'.local/bin/sqlitebrowser').samefile(app/'sqlitebrowser'))
        self.assertFalse((self.home/'.config/appman/appman-mode').exists())
        self.assertFalse(Path('/opt/sqlitebrowser').exists())

    def test_system_mode_without_privilege_tool_still_refuses(self):
        self.assertIsNone(shutil.which('sudo'))
        self.assertIsNone(shutil.which('doas'))
        os.chmod('/opt/am',0o755)
        try:
            result=self.command('--version',executable=str(Path(os.environ['PREFIX'])/'bin/am'),success=False)
            self.assertIn('No sudo or doas found',result.stdout)
            self.assertFalse((self.home/'.config/appman/appman-mode').exists())
        finally:
            os.chmod('/opt/am',0o555)

    def test_read_only_fallback_can_be_declined(self):
        self.command('-i','sqlitebrowser',executable=str(Path(os.environ['PREFIX'])/'bin/am'),input_text='n\n')
        self.assertFalse((self.home/'Applications/sqlitebrowser').exists())
        self.assertFalse((self.home/'.config/appman/appman-mode').exists())

    def test_native_cli_install_and_execute(self):
        executable=self.appman()
        # Actual native Android/Bionic ELF bytes from this environment, transported
        # through the same strictly offline adapter as other downloads.
        raw=(Path(os.environ['PREFIX'])/'bin/bash').read_bytes()
        self.assertEqual(raw[:4],b'\x7fELF')
        (self.logs/'native-cli.json').write_text(json.dumps({
            'source':'Termux packaged Bash','sha256':hashlib.sha256(raw).hexdigest(),
            'bytes':len(raw)},indent=2)+'\n')
        (self.fixture/'binary').write_bytes(raw)
        url='https://example.invalid/termux-native-bash'
        self.configure(assets=self.settings['assets']+[url])
        recipe=(self.fixture/'legacy-recipe').read_text()
        lines=recipe.splitlines()
        lines=[f'curl --fail -L -o "/opt/$APP/$APP" {url}'
               if 'inert legacy binary' in line else line for line in lines]
        (self.fixture/'legacy-recipe').write_text('\n'.join(lines)+'\n')
        self.command('-i','e2e-legacy',executable=executable)
        app=self.home/'Applications/e2e-legacy'
        self.assertEqual((app/'e2e-legacy').read_bytes(),raw)
        result=self.command('-c','printf "native-android-cli\\n"',
                            executable=str(self.home/'.local/bin/e2e-legacy'))
        self.assertEqual(result.stdout,'native-android-cli\n')

    def test_catalog_refusal_and_failed_transfer_preserve_app(self):
        executable=self.appman()
        self.command('-i','sqlitebrowser',executable=executable)
        app=self.home/'Applications/sqlitebrowser'
        before=(app/'sqlitebrowser').read_bytes()
        (app/'version').write_text('old\n')
        self.configure(download_partial_fail=True)
        self.command('-u','sqlitebrowser','--commit',PIN,executable=executable,success=False)
        self.assertEqual((app/'tmp/sqlitebrowser.AppImage').read_bytes(),
                         (self.fixture/'binary').read_bytes()[:17])
        self.assertEqual((app/'sqlitebrowser').read_bytes(),before)
        self.assertEqual((app/'version').read_text(),'old\n')
        self.configure(download_partial_fail=False)
        self.command('-u','sqlitebrowser','--commit',PIN,executable=executable)
        self.assertEqual((app/'version').read_text().strip(),SQLITE)
        before=snapshot_tree(app)
        self.configure(clock='1793500000.000000')
        self.command('-u','sqlitebrowser','--commit',PIN,executable=executable,success=False)
        self.assertEqual(snapshot_tree(app),before)

    def test_read_only_am_falls_back_without_sudo(self):
        self.appman()
        self.assertIsNone(shutil.which('sudo'))
        self.assertFalse(os.access('/opt/am',os.W_OK))
        result=self.command('-i','sqlitebrowser',executable=str(Path(os.environ['PREFIX'])/'bin/am'),input_text='y\ny\n')
        self.assertIn('AppMan Mode',result.stdout)
        self.assertTrue((self.home/'.config/appman/appman-mode').is_file())
        app=self.home/'Applications/sqlitebrowser'
        self.assertEqual((app/'version').read_text().strip(),SQLITE)
        self.assertFalse(Path('/opt/sqlitebrowser').exists())
        self.assertIn('/opt/am/modules/catalog.am',(app/'recipe.am').read_text())
        self.command('--commit',PIN,executable=str(app/'AM-updater'))
        self.command('-u','sqlitebrowser','--commit',PIN,executable=str(Path(os.environ['PREFIX'])/'bin/am'))


if __name__=='__main__':
    program=unittest.main(verbosity=2,exit=False,defaultTest=os.environ.get('E2E_TEST') or None)
    result=program.result
    (OUT/'results.json').write_text(json.dumps({
        'target':'termux','tests_run':result.testsRun,'success':result.wasSuccessful(),
        'failures':[test.id() for test,_ in result.failures],
        'errors':[test.id() for test,_ in result.errors]},indent=2)+'\n')
    sys.exit(not result.wasSuccessful())
