"""Real SQLite recipe/updater with retained metadata and isolated app operations."""
from datetime import datetime, timedelta
import test_obsidian_filter as install_fixture
import subprocess

from shell_lookup import epoch
from test_shell_consumer import ShellFixture, ROOT, HELPER, PIN

APP = ROOT/'programs/x86_64/sqlitebrowser'


class SQLiteBrowserFilter(ShellFixture):
    catalog_alias = 'https://api.github.com/repos/sqlitebrowser/sqlitebrowser/releases?per_page=100'

    def setUp(self):
        super().setUp()
        self.root=self.path/'root'
        self.app=self.root/'opt/sqlitebrowser'
        source=APP.read_text().replace('/opt/am/modules/catalog.am',str(HELPER))
        self.recipe=self.path/'recipe'
        self.recipe.write_text(source.replace('/opt/',str(self.root)+'/opt/').replace(
            '/usr/local/',str(self.root)+'/usr/local/'))
        self.script('wget', '''import os,pathlib,sys
p=pathlib.Path(os.environ['FIXTURE']);(p/'download').write_text(sys.argv[-1])
if os.environ.get('DOWNLOAD_FAIL'):sys.exit(9)
pathlib.Path('SQLite.AppImage').write_text("#!/bin/sh\\nmkdir -p squashfs-root\\ncase $2 in\\n*.desktop) printf '[Desktop Entry]\\\\nExec=sqlitebrowser\\\\nIcon=sqlitebrowser\\\\n' > squashfs-root/sqlitebrowser.desktop ;;\\n.DirIcon) printf icon > squashfs-root/.DirIcon ;;\\nesac\\n")
''')
        self.script('notify-send','raise SystemExit(1)\n')
        self.script('appimageupdatetool',"raise RuntimeError('forbidden bypass')\n")

    def run_script(self,path,args=None,env=None):
        self.stage()
        return subprocess.run(['/bin/sh',str(path),*(args or ['--commit',PIN])],
            cwd=self.path,env=env or self.env(),capture_output=True)

    def install(self):
        result=self.run_script(self.recipe)
        self.assertEqual(result.returncode,0,result.stderr)
        self.url=(self.app/'version').read_text().strip()
        return self.app/'AM-updater'

    def state(self):
        return {str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*')
                if p.is_file() and not p.is_symlink()}

    def stale(self):
        self.now=[epoch((datetime.fromisoformat(self.obs['validated_at'])+
                  timedelta(days=1,microseconds=1)).isoformat())]*3

    def test_retained_filter_install_and_standalone_unchanged(self):
        updater=self.install()
        self.assertEqual(self.url, 'https://github.com/sqlitebrowser/sqlitebrowser/releases/'
            'download/v3.13.1/DB.Browser.for.SQLite-v3.13.1-x86.64-v2.AppImage')
        self.assertEqual((self.path/'download').read_text(),self.url)
        self.assertEqual(len(self.calls()),2)
        self.assertIn('# AM-CATALOG-UPDATER 1',updater.read_text())
        (self.path/'download').unlink()
        before=self.state()
        result=self.run_script(updater)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn(b'Update not needed!',result.stdout)
        self.assertEqual(self.state(),before)
        self.assertFalse((self.path/'download').exists())

    def test_stale_install_refuses_before_any_directory_or_download(self):
        self.stale()
        result=self.run_script(self.recipe)
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'stale',result.stderr)
        self.assertFalse(self.root.exists())
        self.assertFalse((self.path/'download').exists())
        self.assertEqual(len(self.calls()),1)
        result=self.run_script(self.recipe,self.consent())
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue((self.app/'AM-updater').exists())

    def test_changed_update_download_retry_and_checksum_repair(self):
        updater=self.install()
        (self.app/'version').write_text('old-url\n')
        result=self.run_script(updater,env={**self.env(),'DOWNLOAD_FAIL':'1'})
        self.assertNotEqual(result.returncode,0)
        self.assertEqual((self.app/'version').read_text(),'old-url\n')
        self.assertTrue((self.app/'tmp').exists())
        result=self.run_script(updater)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual((self.app/'version').read_text().strip(),self.url)
        self.assertFalse((self.app/'tmp').exists())
        (self.app/'AM-VERIFIED').write_text('Checksum failure\n')
        (self.path/'download').unlink()
        result=self.run_script(updater)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual((self.path/'download').read_text(),self.url)

    def test_stale_updater_preserves_incomplete_state(self):
        updater=self.install()
        (self.app/'tmp').mkdir();(self.app/'tmp/retained').write_text('partial')
        self.stale();before=self.state()
        result=self.run_script(updater)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(self.state(),before)

    def test_actual_manager_route_propagates_selected_source_for_second_app(self):
        self.install()
        manager=(ROOT/'APP-MANAGER').read_text()
        route=manager[manager.index('_catalog_update() {'):manager.index('\n_use_update() {')]
        harness=self.path/'manager'
        harness.write_text('AMREPO=https://raw.githubusercontent.com/selected-owner/extra.apps/main\n'
            '_use_verify() { :; }\n'+route+'\n_catalog_update "$@"\n')
        self.stage()
        result=subprocess.run(['/bin/bash',str(harness),'-u','sqlitebrowser','--commit',PIN],
            env={**self.env(),'APPSPATH':str(self.root/'opt')},capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(all('/selected-owner/extra.apps/' in c[-1] for c in self.calls()))
        self.assertEqual(len(self.calls()),2)

    def test_real_install_dispatch_persists_source_after_privilege_environment_loss(self):
        source='https://raw.githubusercontent.com/selected-owner/extra.apps/main'
        result=install_fixture.ObsidianFilter.run_manager_install(
            self,amrepo=source,recipe=APP,app_name='sqlitebrowser')
        self.assertEqual(result.returncode,0,result.stderr)
        updater=self.app/'AM-updater'
        self.assertIn('AMREPO=${AMREPO-"'+source+'"}',updater.read_text())
        env=self.env();env.pop('AMREPO')
        result=self.run_script(updater,env=env)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn(b'Update not needed!',result.stdout)
        self.assertTrue(all('/selected-owner/extra.apps/' in c[-1] for c in self.calls()))
