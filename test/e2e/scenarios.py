"""Container-only tests of whole, byte-unmodified installed AM/AppMan commands."""
import hashlib
from decimal import Decimal
import json
import os
from pathlib import Path
import pwd
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest

if not Path('/run/am-e2e-container').is_file() or not Path('/src/APP-MANAGER').is_file():
    raise SystemExit('Run test/e2e/run; scenarios must never run on the host.')

sys.path.insert(0, '/src/tools/catalog-collector')
import test_storage as retained
from shell_lookup import render
from shell_lookup import epoch
from storage import validate
from filesystem import fingerprint_files, snapshot_tree
from transport_records import read_transport_records

SOURCE = 'https://raw.githubusercontent.com/e2e-selected/AM/test-source'
PIN = 'b'*40
OBSIDIAN = 'https://github.com/obsidianmd/obsidian-releases/releases/download/v1.14.5/Obsidian-1.14.5.AppImage'
SQLITE = 'https://github.com/sqlitebrowser/sqlitebrowser/releases/download/v3.13.1/DB.Browser.for.SQLite-v3.13.1-x86.64-v2.AppImage'
OUT = Path('/out')
USER = pwd.getpwnam('system' if os.environ.get('E2E_TARGET') == 'termux' else 'e2e')


class InstalledCLI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        retained.StorageContract.setUpClass()
        cls.tree = dict(retained.StorageContract.base)
        cls.tree['lookup.tsv'] = render(validate(cls.tree), cls.tree['index.json'])
        cls.index = validate(cls.tree)
        manager = Path('/opt/am');manager.mkdir(parents=True, exist_ok=True)
        shutil.copy2('/src/APP-MANAGER', manager/'APP-MANAGER')
        shutil.copytree('/src/modules', manager/'modules', dirs_exist_ok=True)
        for path in (manager, *manager.rglob('*')):
            os.chown(path, USER.pw_uid, USER.pw_gid)
        Path('/usr/local/bin/am').symlink_to(manager/'APP-MANAGER')
        cls.manager_hash = fingerprint_files(Path('/src'), ['APP-MANAGER'])['APP-MANAGER']
        cls.module_hashes = fingerprint_files(Path('/src/modules'),
                                            [p.name for p in Path('/src/modules').glob('*.am')])
        inputs=['test/e2e/scenarios.py','test/e2e/external.py','test/e2e/run',
                'test/e2e/filesystem.py','test/e2e/transport_args.py','test/e2e/transport_records.py',
                'test/e2e/container-test.sh','test/e2e/fixtures/e2e-legacy',
                'test/e2e/Containerfile.debian','test/e2e/Containerfile.fedora',
                'APP-MANAGER','programs/x86_64/nvim','programs/x86_64/nvim-nightly','programs/x86_64/obsidian','programs/x86_64/sqlitebrowser',
                'docs/track/release-catalog/design/staged-manifest.json',
                'docs/track/release-catalog/research/supervised-baseline-40529551070-evidence.tar.gz']
        (OUT/'tested-source.json').write_text(json.dumps({
            'inputs':fingerprint_files(Path('/src'), inputs),
            'modules':cls.module_hashes},indent=2)+'\n')

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='am-e2e-')
        self.addCleanup(self.tmp.cleanup)
        self.fixture = Path(self.tmp.name)
        self.bin = self.fixture/'bin';self.bin.mkdir()
        for name in ('calls','unexpected'):
            (self.fixture/name).mkdir()
        for name in ('curl','wget','date','notify-send'):
            (self.bin/name).symlink_to('/src/test/e2e/external.py')
        self.settings = {'source':SOURCE,'repository':'e2e-selected/AM','pin':PIN,
            'clock':'1793114400.000000','assets':[OBSIDIAN,SQLITE,'https://github.com/neovim/neovim/releases/download/nightly/nvim-linux-x86_64.appimage','https://github.com/neovim/neovim/releases/download/v0.12.6/nvim-linux-x86_64.appimage'],
            'catalog_paths':list(self.tree)}
        self.configure()
        shutil.copy2('/src/test/e2e/fixtures/e2e-legacy',self.fixture/'legacy-recipe')
        for name, raw in self.tree.items():
            path=self.fixture/'tree'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        (self.fixture/'binary').write_text('''#!/bin/sh
app=${0##*/}
case ${1-} in
    --appimage-extract)
        mkdir -p squashfs-root
        case $2 in
            '*.desktop') printf '[Desktop Entry]\\nExec=%s --no-sandbox\\nIcon=%s\\n' "$app" "$app" > "squashfs-root/$app.desktop" ;;
            .DirIcon) printf 'inert icon' > squashfs-root/.DirIcon ;;
            *) exit 4 ;;
        esac ;;
    --version) printf 'inert e2e binary\\n' ;;
    *) exit 5 ;;
esac
''')
        self.home=self.fixture/'home';self.home.mkdir()
        for name in ('obsidian','sqlitebrowser','nvim','nvim-nightly','e2e-legacy'):
            shutil.rmtree(Path('/opt')/name,ignore_errors=True)
            launcher=Path('/usr/local/bin')/name
            if launcher.is_symlink() or launcher.exists(): launcher.unlink()
        self.prepare_home(self.home)
        # Fixtures/logs must survive real sudo environment clearing; only the
        # explicit E2E_FIXTURE variable is retained by the container sudo policy.
        for path in (self.fixture,*self.fixture.rglob('*')):
            if not path.is_symlink(): os.chown(path,USER.pw_uid,USER.pw_gid)
        self.logs=OUT/self._testMethodName;self.logs.mkdir(exist_ok=True)
        self.sequence=0

    def configure(self, **changes):
        self.settings.update(changes)
        (self.fixture/'settings.json').write_text(json.dumps(self.settings))

    def prepare_home(self, home, *, appman=False):
        data=home/'.local/share/AM';data.mkdir(parents=True,exist_ok=True)
        (data/'locale').write_text('en\n')
        (data/'disable-dependencies-prompt').touch()
        (data/'newrepo-on').write_text(SOURCE+'\n')
        (data/'x86_64-apps').write_text('◆ obsidian : Offline fixture\n◆ sqlitebrowser : Offline fixture\n◆ nvim : Offline fixture\n◆ nvim-nightly : Offline fixture\n')
        (data/'x86_64-appimages').write_text('obsidian\nsqlitebrowser\nnvim\nnvim-nightly\n')
        (home/'.local/bin').mkdir(parents=True,exist_ok=True)
        if appman:
            apps=home/'Applications';apps.mkdir()
            manager=apps/'appman';manager.mkdir()
            shutil.copy2('/src/APP-MANAGER',manager/'appman')
            shutil.copytree('/src/modules',manager/'modules')
            config=home/'.config/appman';config.mkdir(parents=True)
            (config/'appman-config').write_text(str(apps)+'\n')
        for path in (home,*home.rglob('*')):
            os.chown(path,USER.pw_uid,USER.pw_gid)

    def command(self, *args, executable='/usr/local/bin/am', home=None, success=True, input_text=None, interrupt_download=False):
        self.sequence+=1
        chosen=home or self.home
        env={'HOME':str(chosen),'USER':'e2e','LOGNAME':'e2e','LANG':'C','TERM':'xterm',
            'PATH':str(self.bin)+':'+str(chosen/'.local/bin')+':/usr/local/bin:/usr/bin:/bin',
            'E2E_FIXTURE':str(self.fixture),'NO_COLOR':'1'}
        if os.environ.get('E2E_TARGET') == 'termux':
            for key in ('PREFIX','TMPDIR','ANDROID_DATA','ANDROID_ROOT','LD_PRELOAD','TERMUX_VERSION'):
                env[key]=os.environ[key]
            env['PATH']=str(self.bin)+':'+str(chosen/'.local/bin')+':'+env['PREFIX']+'/bin'
            env['USER']=env['LOGNAME']='system'
        # No AMREPO environment: manager configuration and saved recipes deliver it.
        cmd=['runuser','-u','e2e','--','env','-i',*[f'{k}={v}' for k,v in env.items()],executable,*args]
        if os.environ.get('E2E_TARGET') == 'termux':
            cmd=[executable,*args]
        process=subprocess.Popen(cmd,env=env if os.environ.get('E2E_TARGET') == 'termux' else None,cwd=chosen,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                 text=True,start_new_session=True,stdin=subprocess.PIPE if input_text is not None else subprocess.DEVNULL)
        paused=None
        try:
            if interrupt_download:
                marker=self.fixture/'download-paused'
                deadline=time.monotonic()+45
                while not marker.exists() and process.poll() is None and time.monotonic()<deadline:
                    time.sleep(0.02)
                if not marker.exists():
                    raise subprocess.TimeoutExpired(cmd,45)
                paused=json.loads(marker.read_text())
                os.killpg(process.pid,signal.SIGKILL)
                (self.logs/f'{self.sequence:02d}.interruption.json').write_text(json.dumps({
                    'signal':'SIGKILL','command_pgid':process.pid,'download':paused}))
                marker.unlink()
            stdout,stderr=process.communicate(input=input_text,timeout=45)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGKILL)
            stdout,stderr=process.communicate()
            stderr+='\nE2E command deadline exceeded\n'
        result=subprocess.CompletedProcess(cmd,process.returncode,stdout,stderr)
        prefix=self.logs/f'{self.sequence:02d}'
        prefix.with_suffix('.command.json').write_text(json.dumps([executable,*args]))
        prefix.with_suffix('.stdout').write_text(result.stdout)
        prefix.with_suffix('.stderr').write_text(result.stderr)
        prefix.with_suffix('.status').write_text(str(result.returncode)+'\n')
        if interrupt_download:
            self.assertIsNotNone(paused,'download never reached interruption checkpoint')
            self.assertEqual(paused['pgid'],process.pid,'download escaped command process group')
        if success:
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        else:
            self.assertNotEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertFalse(list((self.fixture/'unexpected').iterdir()),result.stdout+result.stderr)
        return result

    def tearDown(self):
        shutil.copytree(self.fixture/'calls',self.logs/'transport',dirs_exist_ok=True)
        shutil.copytree(self.fixture/'unexpected',self.logs/'unexpected',dirs_exist_ok=True)
        self.assertEqual(hashlib.sha256(Path('/opt/am/APP-MANAGER').read_bytes()).hexdigest(),self.manager_hash)
        for name,digest in self.module_hashes.items():
            self.assertEqual(hashlib.sha256((Path('/opt/am/modules')/name).read_bytes()).hexdigest(),digest)

    def test_neovim_stable_and_nightly_refresh_preserve_user_setup(self):
        # Both selectors use retained observations; executable bytes are inert.
        config=self.home/'.config/nvim';config.mkdir(parents=True)
        (config/'init.lua').write_text('-- untouched user configuration\n')
        launcher=self.home/'.local/bin/nvim'
        launcher.symlink_to('/opt/nvim-nightly/nvim-nightly')
        before=snapshot_tree(self.home/'.config')
        self.command('-i','nvim')
        app=Path('/opt/nvim')
        self.assertEqual((app/'version').read_text().strip(),
            'https://github.com/neovim/neovim/releases/download/v0.12.6/nvim-linux-x86_64.appimage')
        self.command('--commit',PIN,executable=str(app/'AM-updater'))
        self.command('-i','nvim-nightly')
        nightly=Path('/opt/nvim-nightly')
        old=(nightly/'nvim-nightly').read_bytes()
        self.configure(download_fail=True)
        self.command('-u','nvim-nightly','--commit',PIN,success=False)
        self.assertEqual((nightly/'nvim-nightly').read_bytes(),old)
        self.configure(download_fail=False)
        result=self.command('-u','nvim-nightly','--commit',PIN)
        self.assertIn('nvim-nightly: updated',result.stdout)
        previous=set((self.fixture/'calls').iterdir())
        self.command('--commit',PIN,executable=str(nightly/'AM-updater'))
        calls=read_transport_records(self.fixture/'calls', excluding=previous)
        self.assertTrue(any(c['tool']=='wget' and c['url'].endswith('/nightly/nvim-linux-x86_64.appimage') for c in calls))
        self.configure(clock='1793500000.000000')
        before_app=snapshot_tree(nightly)
        self.command('-u','nvim-nightly','--commit',PIN,success=False)
        self.assertEqual(snapshot_tree(nightly),before_app)
        self.assertEqual(os.readlink(launcher),'/opt/nvim-nightly/nvim-nightly')
        self.assertEqual(snapshot_tree(self.home/'.config'),before)

    def test_system_install_and_standalone_updater(self):
        result=self.command('-i','obsidian')
        self.assertIn('INSTALLED',result.stdout)
        app=Path('/opt/obsidian')
        self.assertEqual((app/'version').read_text().strip(),OBSIDIAN)
        self.assertTrue(Path('/usr/local/bin/obsidian').samefile(app/'obsidian'))
        self.assertEqual((app/'AM-updater').read_text().count('\n'),3)
        self.assertIn('AMREPO=${AMREPO-"'+SOURCE+'"}',(app/'recipe.am').read_text())
        self.assertIn('Checksum verified',result.stdout)
        result=self.command('--commit',PIN,executable=str(app/'AM-updater'))
        self.assertIn('Update not needed!',result.stdout)
        self.command('--version',executable='/usr/local/bin/obsidian')

    def test_unprivileged_appman_install_and_standalone_source(self):
        home=self.fixture/'appman-home';home.mkdir()
        self.prepare_home(home,appman=True)
        executable=str(home/'Applications/appman/appman')
        result=self.command('-i','sqlitebrowser',executable=executable,home=home)
        self.assertIn('INSTALLED',result.stdout)
        app=home/'Applications/sqlitebrowser'
        self.assertEqual((app/'version').read_text().strip(),SQLITE)
        self.assertTrue((home/'.local/bin/sqlitebrowser').samefile(app/'sqlitebrowser'))
        self.assertIn(str(home/'Applications/appman/modules/catalog.am'),(app/'recipe.am').read_text())
        self.assertFalse(Path('/opt/sqlitebrowser').exists())
        result=self.command('--commit',PIN,executable=str(app/'AM-updater'),home=home)
        self.assertIn('Update not needed!',result.stdout)
        self.assertEqual((app/'sqlitebrowser').stat().st_uid,USER.pw_uid)

    def test_failed_download_retry_and_same_version_repair(self):
        self.command('-i','obsidian')
        app=Path('/opt/obsidian')
        binary=(app/'obsidian').read_bytes()
        (app/'version').write_text('old synthetic installed URL\n')
        self.configure(download_fail=True)
        result=self.command('-u','obsidian','--commit',PIN,success=False)
        self.assertIn('obsidian: failed',result.stderr)
        self.assertEqual((app/'obsidian').read_bytes(),binary)
        self.assertEqual((app/'version').read_text(),'old synthetic installed URL\n')
        self.assertTrue((app/'tmp').is_dir())
        self.configure(download_fail=False)
        result=self.command('-u','obsidian','--commit',PIN)
        self.assertIn('obsidian: updated',result.stdout)
        self.assertEqual((app/'version').read_text().strip(),OBSIDIAN)
        self.assertFalse((app/'tmp').exists())
        (app/'obsidian').write_text('synthetic corruption\n')
        (app/'AM-VERIFIED').write_text('Checksum failure\n')
        result=self.command('-u','obsidian','--commit',PIN)
        self.assertIn('obsidian: updated',result.stdout)
        self.assertEqual((app/'obsidian').read_bytes(),binary)
        self.assertIn('SHA256:',(app/'AM-VERIFIED').read_text())

    def test_partial_download_preserves_installation_and_retry(self):
        self.command('-i','obsidian')
        app=Path('/opt/obsidian')
        (app/'version').write_text('old synthetic installed URL\n')
        before=snapshot_tree(app)
        self.configure(download_partial_fail=True)
        self.command('-u','obsidian','--commit',PIN,success=False)
        self.assertEqual((app/'tmp/obsidian.AppImage').read_bytes(),
                         (self.fixture/'binary').read_bytes()[:17])
        after=snapshot_tree(app)
        self.assertEqual({k:v for k,v in after.items() if k!='tmp' and not k.startswith('tmp/')},before)
        self.assertTrue(Path('/usr/local/bin/obsidian').samefile(app/'obsidian'))
        self.configure(download_partial_fail=False)
        self.command('-u','obsidian','--commit',PIN)
        self.assertEqual((app/'obsidian').read_bytes(),(self.fixture/'binary').read_bytes())
        self.assertEqual((app/'version').read_text().strip(),OBSIDIAN)
        self.assertFalse((app/'tmp').exists())

    def test_interrupted_appman_install_and_update_retry(self):
        home=self.fixture/'appman-home';home.mkdir()
        self.prepare_home(home,appman=True)
        executable=str(home/'Applications/appman/appman')
        config=home/'.config/obsidian';config.mkdir()
        (config/'sentinel').write_text('keep user configuration\n')
        before_config=snapshot_tree(config)
        app=home/'Applications/obsidian'
        self.configure(download_pause=True)
        result=self.command('-i','obsidian',executable=executable,home=home,
                            success=False,interrupt_download=True)
        self.assertEqual(result.returncode,-signal.SIGKILL)
        self.assertEqual((app/'tmp/obsidian.AppImage').read_bytes(),
                         (self.fixture/'binary').read_bytes()[:17])
        self.assertFalse((app/'version').exists())
        self.assertFalse((home/'.local/bin/obsidian').exists())
        self.configure(download_pause=False)
        self.command('-i','obsidian',executable=executable,home=home)
        self.assertEqual((app/'version').read_text().strip(),OBSIDIAN)
        self.assertFalse((app/'tmp').exists())
        self.assertTrue((home/'.local/bin/obsidian').samefile(app/'obsidian'))
        (app/'version').write_text('old\n')
        before=snapshot_tree(app)
        self.configure(download_pause=True)
        result=self.command('-u','obsidian',executable=executable,home=home,
                            success=False,interrupt_download=True)
        self.assertEqual(result.returncode,-signal.SIGKILL)
        after=snapshot_tree(app)
        self.assertEqual({k:v for k,v in after.items() if k!='tmp' and not k.startswith('tmp/')},before)
        self.assertTrue((home/'.local/bin/obsidian').samefile(app/'obsidian'))
        self.configure(download_pause=False)
        self.command('-u','obsidian',executable=executable,home=home)
        self.assertEqual((app/'version').read_text().strip(),OBSIDIAN)
        self.assertFalse((app/'tmp').exists())
        self.assertEqual(snapshot_tree(config),before_config)
        self.assertFalse(Path('/opt/obsidian').exists())

    def test_repository_switch_keeps_standalone_embedded_source(self):
        self.command('-i','obsidian')
        app=Path('/opt/obsidian')
        alternate='https://raw.githubusercontent.com/e2e-alternate/AM/test-source'
        self.configure(alternate_source=alternate,alternate_repository='e2e-alternate/AM')
        (self.home/'.local/share/AM/newrepo-on').write_text(alternate+'\n')
        previous=set((self.fixture/'calls').iterdir())
        self.command('-u','obsidian','--commit',PIN)
        calls=[record['url'] for record in read_transport_records(self.fixture/'calls', excluding=previous)]
        self.assertTrue(any(url.startswith('https://raw.githubusercontent.com/e2e-alternate/AM/'+PIN+'/') for url in calls))
        self.assertFalse(any(url.startswith('https://raw.githubusercontent.com/e2e-selected/AM/'+PIN+'/') for url in calls))
        self.assertIn('AMREPO=${AMREPO-"'+SOURCE+'"}',(app/'recipe.am').read_text())
        previous=set((self.fixture/'calls').iterdir())
        self.command('--commit',PIN,executable=str(app/'AM-updater'))
        calls=[record['url'] for record in read_transport_records(self.fixture/'calls', excluding=previous)]
        self.assertTrue(any(url.startswith('https://raw.githubusercontent.com/e2e-selected/AM/'+PIN+'/') for url in calls))
        self.assertFalse(any('e2e-alternate' in url for url in calls))

    def test_exact_48_hour_cli_freshness_boundary(self):
        self.command('-i','obsidian')
        app=Path('/opt/obsidian')
        alias='https://api.github.com/repos/obsidianmd/obsidian-releases/releases'
        rid=self.index['aliases'][alias]['request_id']
        checked=Decimal(epoch(self.index['entries'][rid]['observation']['validated_at']))
        boundary=checked+Decimal(172800)
        before=snapshot_tree(app)
        self.configure(clock=f'{boundary:.6f}')
        result=self.command('-u','obsidian','--commit',PIN)
        self.assertIn('obsidian: unchanged',result.stdout)
        after=snapshot_tree(app)
        for name in ('obsidian','version'):
            self.assertEqual(after[name],before[name])
        before=after
        self.configure(clock=f'{boundary+Decimal("0.000001"):.6f}')
        result=self.command('-u','obsidian','--commit',PIN,success=False)
        self.assertIn('stale',result.stderr)
        self.assertEqual(snapshot_tree(app),before)

    def test_remove_reinstall_preserves_user_configuration(self):
        for appman in ((True,) if os.environ.get('E2E_TARGET') == 'termux' else (False,True)):
            with self.subTest(appman=appman):
                home=self.fixture/'remove-appman-home' if appman else self.home
                if appman:
                    home.mkdir()
                    self.prepare_home(home,appman=True)
                executable=str(home/'Applications/appman/appman') if appman else '/usr/local/bin/am'
                app=home/'Applications/obsidian' if appman else Path('/opt/obsidian')
                launcher=home/'.local/bin/obsidian' if appman else Path('/usr/local/bin/obsidian')
                desktop=home/'.local/share/applications/obsidian-AM.desktop' if appman else Path('/usr/local/share/applications/obsidian-AM.desktop')
                config=home/'.config/obsidian';config.mkdir(parents=True)
                sentinel=config/'user-settings';sentinel.write_text('keep my settings\n')
                for path in (config,sentinel): os.chown(path,USER.pw_uid,USER.pw_gid)
                self.command('-i','obsidian',home=home,executable=executable)
                self.assertTrue(desktop.is_file())
                before=snapshot_tree(config)
                self.command('-r','obsidian',home=home,executable=executable,input_text='y\n')
                self.assertFalse(app.exists())
                self.assertFalse(os.path.lexists(launcher))
                self.assertFalse(os.path.lexists(desktop))
                self.assertEqual(snapshot_tree(config),before)
                self.command('-i','obsidian',home=home,executable=executable)
                self.assertTrue(launcher.samefile(app/'obsidian'))
                self.assertTrue(desktop.is_file())
                self.assertEqual((app/'version').read_text().strip(),OBSIDIAN)
                self.command('--commit',PIN,home=home,executable=str(app/'AM-updater'))
                self.assertEqual(snapshot_tree(config),before)

    def test_integrity_and_stale_refusal_preserve_app_and_interrupted_work(self):
        self.command('-i','obsidian')
        app=Path('/opt/obsidian')
        (app/'tmp').mkdir();(app/'tmp/retained').write_text('interrupted work\n')
        before=snapshot_tree(app)
        alias='https://api.github.com/repos/obsidianmd/obsidian-releases/releases'
        rid=self.index['aliases'][alias]['request_id']
        body=self.fixture/'tree/bodies'/f'{rid}.json'
        body.write_bytes(b'[]')
        result=self.command('-u','obsidian','--commit',PIN,success=False)
        self.assertIn('obsidian: refused',result.stderr)
        self.assertEqual(snapshot_tree(app),before)
        body.write_bytes(self.tree[f'bodies/{rid}.json'])
        self.configure(clock='1793500000.000000')
        result=self.command('-u','obsidian','--commit',PIN,success=False)
        self.assertIn('stale',result.stderr)
        self.assertEqual(snapshot_tree(app),before)
        digest=self.index['entries'][rid]['observation']['sha256']
        result=self.command('-u','obsidian','--commit',PIN,'--accept-stale',PIN,rid,digest)
        self.assertIn('obsidian: unchanged',result.stdout)
        self.assertEqual((app/'tmp/retained').read_text(),'interrupted work\n')

    def test_install_refusal_creates_no_app_or_launcher(self):
        self.configure(clock='1793500000.000000')
        result=self.command('-i','obsidian',success=False)
        self.assertIn('stale',result.stderr)
        self.assertFalse(Path('/opt/obsidian').exists())
        self.assertFalse(Path('/usr/local/bin/obsidian').exists())

    def test_mixed_batch_continues_with_shared_catalog_acquisition(self):
        self.command('-i','obsidian','sqlitebrowser','e2e-legacy')
        app=Path('/opt/obsidian')
        before=snapshot_tree(app)
        alias='https://api.github.com/repos/obsidianmd/obsidian-releases/releases'
        rid=self.index['aliases'][alias]['request_id']
        (self.fixture/'tree/bodies'/f'{rid}.json').write_bytes(b'[]')
        previous=set((self.fixture/'calls').iterdir())
        result=self.command('-u','obsidian','e2e-legacy','sqlitebrowser',success=False)
        self.assertIn('obsidian: refused',result.stderr)
        self.assertIn('e2e-legacy: updated',result.stdout)
        self.assertIn('sqlitebrowser: unchanged',result.stdout)
        self.assertEqual(snapshot_tree(app),before)
        self.assertEqual((self.fixture/'legacy-runs').read_text(),'ran')
        calls=read_transport_records(self.fixture/'calls', excluding=previous)
        self.assertEqual(sum('/commits/heads/release-catalog' in c['url'] for c in calls),1)
        self.assertEqual(sum(c['url'].endswith('/lookup.tsv') for c in calls),1)
        self.assertEqual(sum('/bodies/' in c['url'] for c in calls),2)

    def test_appman_mixed_batch_failures_continue_and_retry(self):
        home=self.fixture/'appman-home';home.mkdir()
        self.prepare_home(home,appman=True)
        executable=str(home/'Applications/appman/appman')
        self.command('-i','obsidian','sqlitebrowser','e2e-legacy',executable=executable,home=home)
        apps=home/'Applications';app=apps/'obsidian'
        legacy=apps/'e2e-legacy'
        before=snapshot_tree(app)
        alias='https://api.github.com/repos/obsidianmd/obsidian-releases/releases'
        rid=self.index['aliases'][alias]['request_id']
        body=self.fixture/'tree/bodies'/f'{rid}.json'
        original=body.read_bytes();body.write_bytes(b'[]')
        previous=set((self.fixture/'calls').iterdir())
        result=self.command('-u','obsidian','e2e-legacy','sqlitebrowser',
                            executable=executable,home=home,success=False)
        self.assertIn('obsidian: refused',result.stderr)
        self.assertIn('e2e-legacy: updated',result.stdout)
        self.assertIn('sqlitebrowser: unchanged',result.stdout)
        self.assertEqual(snapshot_tree(app),before)
        self.assertEqual((legacy/'version').read_text().strip(),'legacy-new')
        calls=read_transport_records(self.fixture/'calls',excluding=previous)
        self.assertEqual(sum('/commits/heads/release-catalog' in c['url'] for c in calls),1)
        self.assertEqual(sum(c['url'].endswith('/lookup.tsv') for c in calls),1)
        self.assertEqual(sum('/bodies/' in c['url'] for c in calls),2)
        body.write_bytes(original)
        (self.fixture/'legacy-fail').touch()
        result=self.command('-u','e2e-legacy','obsidian','sqlitebrowser',
                            executable=executable,home=home,success=False)
        self.assertIn('e2e-legacy: failed',result.stderr)
        self.assertIn('obsidian: unchanged',result.stdout)
        self.assertIn('sqlitebrowser: unchanged',result.stdout)
        (self.fixture/'legacy-fail').unlink()
        (app/'version').write_text('old\n')
        before_binary=(app/'obsidian').read_bytes()
        self.configure(download_fail=True)
        result=self.command('-u','obsidian','e2e-legacy','sqlitebrowser',
                            executable=executable,home=home,success=False)
        self.assertIn('obsidian: failed',result.stderr)
        self.assertIn('e2e-legacy: unchanged',result.stdout)
        self.assertIn('sqlitebrowser: unchanged',result.stdout)
        self.assertEqual((app/'obsidian').read_bytes(),before_binary)
        self.assertEqual((app/'version').read_text(),'old\n')
        self.configure(download_fail=False)
        result=self.command('-u','obsidian','e2e-legacy','sqlitebrowser',
                            executable=executable,home=home)
        self.assertIn('obsidian: updated',result.stdout)
        self.assertIn('sqlitebrowser: unchanged',result.stdout)
        self.assertEqual((app/'version').read_text().strip(),OBSIDIAN)
        self.assertEqual((self.fixture/'legacy-runs').read_text(),'ran'*4)
        for name in ('obsidian','sqlitebrowser','e2e-legacy'):
            self.assertFalse((Path('/opt')/name).exists())
            self.assertEqual((apps/name/name).stat().st_uid,USER.pw_uid)
            self.assertTrue((home/'.local/bin'/name).samefile(apps/name/name))

    def test_optional_digest_unavailable_differs_from_checksum_mismatch(self):
        self.command('-i','obsidian')
        self.configure(bad_digest=True)
        result=self.command('-u','obsidian','--commit',PIN,success=False)
        self.assertIn('obsidian: failed',result.stderr)
        self.assertEqual(Path('/opt/obsidian/AM-VERIFIED').read_text(),'Checksum failure')
        self.configure(bad_digest=False,digest_missing=True)
        result=self.command('-u','obsidian','--commit',PIN)
        self.assertIn('obsidian: updated',result.stdout)
        self.assertFalse(Path('/opt/obsidian/AM-VERIFIED').exists())

    def test_no_argument_update_preserves_failure_through_real_sync(self):
        self.command('-i','obsidian','e2e-legacy')
        (self.fixture/'legacy-fail').touch()
        # Model an older installed module, not a rewritten test harness. The real
        # sync must repair this large payload despite pipefail and grep -q.
        module=Path('/opt/am/modules/install.am')
        module.write_text('# obsolete installed module marker\n'+module.read_text())
        result=self.command('-u',success=False)
        self.assertEqual(module.read_bytes(),Path('/src/modules/install.am').read_bytes())
        self.assertIn('e2e-legacy: failed',result.stderr)
        self.assertIn('obsidian: unchanged',result.stdout)
        self.assertIn('SYNCHRONIZING',result.stdout)
        calls=read_transport_records(self.fixture/'calls')
        self.assertTrue(any(c['url']==SOURCE+'/APP-MANAGER' for c in calls))
        self.assertTrue(any(c['url']==SOURCE+'/modules/catalog.am' for c in calls))
        self.assertEqual(Path('/opt/obsidian/version').read_text().strip(),OBSIDIAN)


if __name__ == '__main__':
    program=unittest.main(verbosity=2,exit=False)
    result=program.result
    (OUT/'results.json').write_text(json.dumps({
        'target':os.environ.get('E2E_TARGET','unknown'), 'tests_run':result.testsRun,
        'success':result.wasSuccessful(),
        'failures':[test.id() for test,_ in result.failures],
        'errors':[test.id() for test,_ in result.errors]},indent=2)+'\n')
    sys.exit(not result.wasSuccessful())
