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
from test_utility_selectors import accepted_tree, ALIAS as UTILITY_ALIAS
from test_brave_migration import accepted_brave_tree, ALIAS as BRAVE_ALIAS
from test_migration_batch import retained_tree as migration_tree, migration_rows
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
                'tools/catalog-collector/test_brave_migration.py',
                'docs/track/release-catalog/research/brave-live-20261102-evidence.tar.gz',
                'programs/x86_64/brave','programs/x86_64/brave-beta','programs/x86_64/brave-nightly',
                'APP-MANAGER','programs/x86_64/nvim','programs/x86_64/nvim-nightly','programs/x86_64/obsidian','programs/x86_64/sqlitebrowser',
                'programs/x86_64/7z','programs/x86_64/arch','programs/x86_64/c++filt','programs/x86_64/ld.bfd',
                'tools/catalog-collector/test_utility_selectors.py',
                'docs/track/release-catalog/research/am-utils-live-20261031-evidence.tar.gz',
                'docs/track/release-catalog/design/staged-manifest.json',
                'docs/track/release-catalog/research/supervised-baseline-40529551070-evidence.tar.gz']
        inputs += ['tools/catalog-collector/test_migration_batch.py',
                   'docs/track/release-catalog/research/appimage-batch-20261102/migration.json']
        inputs += [row['path'] for row in migration_rows()]
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
case $app in
    7z|arch|c++filt|ld.bfd) printf forbidden > "$E2E_FIXTURE/utility-executed"; exit 97 ;;
esac
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
        for name in ('obsidian','sqlitebrowser','nvim','nvim-nightly','e2e-legacy','7z','arch','c++filt','ld.bfd','brave','brave-beta','brave-nightly'):
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
        (data/'x86_64-apps').write_text(''.join('◆ '+app+' : Offline fixture\n' for app in
            ('obsidian','sqlitebrowser','nvim','nvim-nightly','7z','arch','c++filt','ld.bfd','brave','brave-beta','brave-nightly')+tuple(self.settings.get('additional_recipes', []))))
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
        self.assertEqual((app/'tmp/obsidian').read_bytes(),
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
        self.assertEqual((app/'tmp/obsidian').read_bytes(),
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

    def test_named_reinstall_preserves_unrelated_changed_app(self):
        self.check_reinstall_selection(('obsidian',),('nvim',),('obsidian',))

    def test_multiple_named_reinstall_is_deduplicated_and_scoped(self):
        self.check_reinstall_selection(('obsidian','sqlitebrowser','obsidian'),
                                       ('nvim',),('obsidian','sqlitebrowser'))

    def test_missing_reinstall_names_preserve_all_apps(self):
        # A regex-like missing name must not select nvim.
        self.check_reinstall_selection(('missing-app','nv.m'),('nvim',),())

    def test_mixed_present_missing_reinstall_names(self):
        self.check_reinstall_selection(('obsidian','missing-app'),('nvim',),('obsidian',))

    def test_no_argument_reinstall_only_selects_changed_recipes(self):
        self.check_reinstall_selection((),('nvim','sqlitebrowser'),('nvim','sqlitebrowser'))

    def test_named_reinstall_with_global_assume_yes(self):
        self.check_reinstall_selection(('obsidian',),('nvim',),('obsidian',),prefix=('-y',))

    def check_reinstall_selection(self, names, changed, expected, *, prefix=()):
        for appman in ((True,) if os.environ.get('E2E_TARGET') == 'termux' else (False,True)):
            with self.subTest(appman=appman):
                home=self.fixture/'reinstall-appman-home' if appman else self.home
                if appman:
                    home.mkdir()
                    self.prepare_home(home,appman=True)
                executable=str(home/'Applications/appman/appman') if appman else '/usr/local/bin/am'
                root=home/'Applications' if appman else Path('/opt')
                apps=('obsidian','nvim','sqlitebrowser')
                self.command('-i',*apps,home=home,executable=executable)
                for app in changed:
                    recipe=root/app/'.am-installer'/app
                    recipe.write_text(recipe.read_text()+'\n# old saved recipe\n')
                for app in apps:
                    marker=root/app/'reinstall-sentinel'
                    marker.write_text('must survive unless explicitly selected or changed\n')
                    os.chown(marker,USER.pw_uid,USER.pw_gid)
                # Discovery normally removes incomplete installations. Explicit
                # selection must exclude these before that cleanup can mutate them.
                incomplete=root/'e2e-unrelated'
                if names:
                    incomplete.mkdir()
                    remove=incomplete/'remove'
                    remove.write_text('#!/bin/sh\nrm -rf "'+str(incomplete)+'"\n')
                    remove.chmod(0o755)
                    for path in (incomplete,remove): os.chown(path,USER.pw_uid,USER.pw_gid)
                    self.addCleanup(shutil.rmtree,incomplete,True)
                before={app:snapshot_tree(root/app) for app in apps}
                incomplete_before=snapshot_tree(incomplete) if names else None
                config=home/'.config'
                sentinel=config/'e2e-reinstall/settings'
                sentinel.parent.mkdir(parents=True)
                sentinel.write_text('preserve user settings\n')
                for path in (sentinel.parent,sentinel): os.chown(path,USER.pw_uid,USER.pw_gid)
                before_config=snapshot_tree(config)
                previous=set((self.fixture/'calls').iterdir())
                self.command(*prefix,'reinstall',*names,home=home,executable=executable)
                calls=read_transport_records(self.fixture/'calls',excluding=previous)
                for app in apps:
                    with self.subTest(app=app):
                        if app in expected:
                            self.assertFalse((root/app/'reinstall-sentinel').exists())
                            self.assertTrue((root/app/'AM-updater').is_file())
                            self.assertEqual((root/app/'.am-installer'/app).read_bytes(),
                                             (Path('/src/programs/x86_64')/app).read_bytes())
                            # Exactly one binary transfer even for duplicate names.
                            self.assertEqual(sum(c['tool']=='wget' and not c['head'] and
                                c['url']==(root/app/'version').read_text().strip() for c in calls),1)
                        else:
                            self.assertEqual(snapshot_tree(root/app),before[app])
                            if names:
                                self.assertFalse(any(c['url']==SOURCE+'/programs/x86_64/'+app for c in calls))
                if names:
                    self.assertTrue(incomplete.is_dir())
                    self.assertEqual(snapshot_tree(incomplete),incomplete_before)
                self.assertEqual(snapshot_tree(config),before_config)

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


    def utility_catalog(self, tree=None):
        # Exact accepted first seven-source publication; never synthetic freshness.
        # Only the fixture clock is set to the publication's recorded time.
        self.tree=accepted_tree() if tree is None else tree
        self.index=validate(self.tree)
        assets=[]
        for entry in self.index['entries'].values():
            value=json.loads(self.tree[entry['observation']['path']])
            releases=value if isinstance(value,list) else [value]
            assets.extend(a['browser_download_url'] for release in releases for a in release['assets'])
        for name,raw in self.tree.items():
            path=self.fixture/'tree'/name
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        self.configure(catalog_paths=list(self.tree),assets=assets,clock=epoch(self.index['generated_at']))
        for path in (self.fixture,*self.fixture.rglob('*')):
            if not path.is_symlink(): os.chown(path,USER.pw_uid,USER.pw_gid)

    def test_executable_system_install_icons_standalone_update_and_remove(self):
        self.utility_catalog()
        self.command('-i','7z','arch','c++filt','ld.bfd','--icons')
        for name in ('7z','arch','c++filt','ld.bfd'):
            app=Path('/opt')/name
            selected=(app/'version').read_text().strip()
            self.assertIn('/x86_64-',selected)
            self.assertTrue((Path('/usr/local/bin')/name).samefile(app/name))
            self.assertFalse((app/'icons').exists())
            self.assertFalse((Path('/usr/local/share/applications')/(name+'-AM.desktop')).exists())
            self.assertEqual(len((app/'AM-updater').read_text().splitlines()),3)
            result=self.command('--commit',PIN,executable=str(app/'AM-updater'))
            self.assertIn('Update not needed!',result.stdout)
            (app/'version').write_text('old\n')
            self.command('-u',name,'--commit',PIN)
            self.assertEqual((app/'version').read_text().strip(),selected)
        self.assertFalse((self.fixture/'utility-executed').exists())
        config=self.home/'.config/arch';config.mkdir(parents=True);(config/'keep').write_text('user configuration')
        self.command('-r','arch',input_text='y\n')
        self.assertFalse(Path('/opt/arch').exists())
        self.assertFalse(Path('/usr/local/bin/arch').exists())
        self.assertEqual((config/'keep').read_text(),'user configuration')

    def test_executable_metadata_refusal_and_exact_stale_consent(self):
        self.utility_catalog()
        self.command('-i','7z')
        app=Path('/opt/7z');(app/'tmp').mkdir();(app/'tmp/interrupted').write_text('keep')
        before=snapshot_tree(app)
        rid=self.index['aliases'][UTILITY_ALIAS]['request_id']
        body=self.fixture/'tree/bodies'/f'{rid}.json'
        original=body.read_bytes();body.write_bytes(b'[]')
        self.command('-u','7z','--commit',PIN,success=False)
        self.assertEqual(snapshot_tree(app),before)
        self.command('-i','ld.bfd',success=False)
        self.assertFalse(Path('/opt/ld.bfd').exists())
        body.write_bytes(original)
        obs=self.index['entries'][rid]['observation']
        self.configure(clock=str(Decimal(epoch(obs['validated_at']))+Decimal('172800.000001')))
        self.command('-u','7z','--commit',PIN,success=False)
        self.assertEqual(snapshot_tree(app),before)
        self.command('-u','7z','--commit',PIN,'--accept-stale',PIN,rid,obs['sha256'])
        self.assertEqual((app/'tmp/interrupted').read_text(),'keep')
        self.assertFalse((self.fixture/'utility-executed').exists())

    def test_executable_partial_transfer_retry_and_checksum_repair(self):
        self.utility_catalog()
        self.command('-i','c++filt')
        app=Path('/opt/c++filt');binary=(app/'c++filt').read_bytes()
        (app/'version').write_text('old\n')
        self.configure(download_partial_fail=True)
        self.command('-u','c++filt','--commit',PIN,success=False)
        self.assertEqual((app/'c++filt').read_bytes(),binary)
        self.assertEqual((app/'version').read_text(),'old\n')
        self.assertEqual((app/'tmp/c++filt').read_bytes(),binary[:17])
        self.configure(download_partial_fail=False)
        self.command('-u','c++filt','--commit',PIN)
        self.assertFalse((app/'tmp').exists())
        (app/'c++filt').write_text('corrupt')
        (app/'AM-VERIFIED').write_text('Checksum failure\n')
        self.command('-u','c++filt','--commit',PIN)
        self.assertEqual((app/'c++filt').read_bytes(),binary)
        self.assertFalse((self.fixture/'utility-executed').exists())

    def test_executable_optional_digest_missing_and_mismatch(self):
        self.utility_catalog()
        self.command('-i','ld.bfd')
        app=Path('/opt/ld.bfd')
        self.configure(bad_digest=True)
        self.command('-u','ld.bfd','--commit',PIN,success=False)
        self.assertEqual((app/'AM-VERIFIED').read_text(),'Checksum failure')
        self.configure(bad_digest=False,digest_missing=True)
        self.command('-u','ld.bfd','--commit',PIN)
        self.assertFalse((app/'AM-VERIFIED').exists())
        self.assertFalse((self.fixture/'utility-executed').exists())

    def test_executable_mixed_batch_and_no_argument_sync(self):
        self.utility_catalog()
        self.command('-i','7z','arch','obsidian','e2e-legacy')
        (Path('/opt/7z/version')).write_text('old\n')
        self.configure(download_fail=True)
        before={p.name for p in (self.fixture/'calls').iterdir()}
        result=self.command('-u','7z','obsidian','e2e-legacy','arch',success=False)
        self.assertIn('7z: failed',result.stderr)
        self.assertIn('obsidian: unchanged',result.stdout)
        self.assertIn('arch: unchanged',result.stdout)
        calls=[json.loads(p.read_text()) for p in (self.fixture/'calls').iterdir() if p.name not in before]
        self.assertEqual(sum('/commits/heads/release-catalog' in c['url'] for c in calls),1)
        self.assertEqual(sum(c['url'].endswith('/lookup.tsv') for c in calls),1)
        self.assertEqual(sum(c['url'].endswith('/bodies/'+self.index['aliases'][UTILITY_ALIAS]['request_id']+'.json') for c in calls),2)
        self.configure(download_fail=False)
        (self.fixture/'legacy-fail').touch()
        result=self.command('-u',success=False)
        self.assertIn('7z: updated',result.stdout)
        self.assertIn('e2e-legacy: failed',result.stderr)
        self.assertIn('SYNCHRONIZING',result.stdout)
        self.assertFalse((self.fixture/'utility-executed').exists())

    def test_executable_appman_install_standalone_source_and_remove(self):
        self.utility_catalog()
        home=self.fixture/'utility-home';home.mkdir();self.prepare_home(home,appman=True)
        executable=str(home/'Applications/appman/appman')
        self.command('-i','7z','arch','c++filt','ld.bfd',executable=executable,home=home)
        for name in ('7z','arch','c++filt','ld.bfd'):
            app=home/'Applications'/name
            self.assertEqual((app/name).stat().st_uid,USER.pw_uid)
            self.assertTrue((home/'.local/bin'/name).samefile(app/name))
            self.assertFalse((app/'icons').exists())
            self.assertIn(str(home/'Applications/appman/modules/appimage.am'),(app/'recipe.am').read_text())
            self.assertFalse((Path('/opt')/name).exists())
        alternate='https://raw.githubusercontent.com/e2e-alternate/AM/test-source'
        self.configure(alternate_source=alternate,alternate_repository='e2e-alternate/AM')
        (home/'.local/share/AM/newrepo-on').write_text(alternate+'\n')
        before={p.name for p in (self.fixture/'calls').iterdir()}
        self.command('-u','7z','--commit',PIN,executable=executable,home=home)
        calls=[json.loads(p.read_text()) for p in (self.fixture/'calls').iterdir() if p.name not in before]
        self.assertTrue(any('raw.githubusercontent.com/e2e-alternate/AM/' in c['url'] for c in calls))
        before={p.name for p in (self.fixture/'calls').iterdir()}
        self.command('--commit',PIN,executable=str(home/'Applications/7z/AM-updater'),home=home)
        calls=[json.loads(p.read_text()) for p in (self.fixture/'calls').iterdir() if p.name not in before]
        self.assertTrue(any('raw.githubusercontent.com/e2e-selected/AM/' in c['url'] for c in calls))
        self.assertFalse(any('e2e-alternate' in c['url'] for c in calls))
        config=home/'.config/ld.bfd';config.mkdir();(config/'keep').write_text('keep')
        self.command('-r','ld.bfd',executable=executable,home=home,input_text='y\n')
        self.assertFalse((home/'Applications/ld.bfd').exists())
        self.assertFalse((home/'.local/bin/ld.bfd').exists())
        self.assertEqual((config/'keep').read_text(),'keep')
        self.assertFalse((self.fixture/'utility-executed').exists())

    def test_executable_appman_mixed_failure_preserves_install_and_continues(self):
        self.utility_catalog()
        home=self.fixture/'utility-home';home.mkdir();self.prepare_home(home,appman=True)
        executable=str(home/'Applications/appman/appman')
        self.command('-i','7z','c++filt','obsidian','e2e-legacy',executable=executable,home=home)
        apps=home/'Applications';binary=(apps/'7z/7z').read_bytes()
        (apps/'7z/version').write_text('old\n')
        self.configure(download_partial_fail=True)
        result=self.command('-u','7z','c++filt','obsidian','e2e-legacy',executable=executable,home=home,success=False)
        self.assertIn('7z: failed',result.stderr)
        self.assertIn('c++filt: unchanged',result.stdout)
        self.assertIn('obsidian: unchanged',result.stdout)
        self.assertEqual((apps/'7z/7z').read_bytes(),binary)
        self.assertEqual((apps/'7z/version').read_text(),'old\n')
        self.configure(download_partial_fail=False)
        self.command('-u','7z','--commit',PIN,executable=executable,home=home)
        self.assertFalse((apps/'7z/tmp').exists())
        self.assertFalse((self.fixture/'utility-executed').exists())


    def test_remaining_batch_both_frames_system_appman_and_mixed_failure(self):
        rows={Path(item['path']).name:item for item in migration_rows() if '/x86_64/' in item['path']}
        names=('criteria1d','wekan','eksplode.re')
        self.configure(additional_recipes=list(names))
        for name in names:
            shutil.rmtree(Path('/opt')/name,ignore_errors=True)
            launcher=Path('/usr/local/bin')/name
            if launcher.is_symlink() or launcher.exists(): launcher.unlink()
        for name in names:
            item=rows[name]
            self.utility_catalog(migration_tree(item['alias'],item['evidence']))
            self.command('-i',name,'e2e-legacy')
            app=Path('/opt')/name
            self.assertEqual((app/'version').read_text().strip(),item['asset'])
            self.assertEqual(len((app/'AM-updater').read_text().splitlines()),3)
            self.assertTrue((app/'icons'/name).is_file())
            binary=(app/name).read_bytes()
            (app/'version').write_text('old\n')
            self.configure(download_partial_fail=True)
            result=self.command('-u',name,'e2e-legacy',success=False)
            self.assertIn(name+': failed',result.stderr)
            self.assertEqual((app/name).read_bytes(),binary)
            self.assertEqual((app/'version').read_text(),'old\n')
            self.configure(download_partial_fail=False)
            self.command('--commit',PIN,executable=str(app/'AM-updater'))
            self.assertEqual((app/'version').read_text().strip(),item['asset'])
        name='wekan';item=rows[name]
        self.utility_catalog(migration_tree(item['alias'],item['evidence']))
        home=self.fixture/'remaining-appman';home.mkdir();self.prepare_home(home,appman=True)
        executable=str(home/'Applications/appman/appman')
        self.command('-i',name,executable=executable,home=home)
        app=home/'Applications'/name
        (app/'version').write_text('old\n')
        self.command('--commit',PIN,executable=str(app/'AM-updater'),home=home)
        self.assertEqual((app/'version').read_text().strip(),item['asset'])

    def test_brave_channels_install_standalone_and_mixed_retry(self):
        self.utility_catalog(accepted_brave_tree())
        self.command('-i','brave','brave-beta','brave-nightly','7z','e2e-legacy')
        for name in ('brave','brave-beta','brave-nightly'):
            app=Path('/opt')/name
            selected=(app/'version').read_text().strip()
            self.assertIn('/ivan-hc/Brave-appimage/',selected)
            self.assertTrue((app/'icons'/name).is_file())
            self.assertTrue((Path('/usr/local/share/applications')/(name+'-AM.desktop')).is_file())
            self.assertEqual(len((app/'AM-updater').read_text().splitlines()),3)
            result=self.command('--commit',PIN,executable=str(app/'AM-updater'))
            self.assertIn('Update not needed!',result.stdout)
        costs={}
        for name in ('brave','brave-beta','brave-nightly'):
            app=Path('/opt')/name
            costs[name]={p.name:{'bytes':p.stat().st_size,'lines':len(p.read_bytes().splitlines())}
                         for p in (app/'recipe.am',app/'AM-updater',app/'remove',app/'.am-installer'/name)}
        (self.logs/'installed-costs.json').write_text(json.dumps(costs,indent=2)+'\n')
        app=Path('/opt/brave');binary=(app/'brave').read_bytes()
        (app/'version').write_text('old\n')
        self.configure(download_partial_fail=True)
        result=self.command('-u','brave','brave-beta','7z','e2e-legacy',success=False)
        self.assertIn('brave: failed',result.stderr)
        self.assertIn('brave-beta: unchanged',result.stdout)
        self.assertIn('7z: unchanged',result.stdout)
        self.assertEqual((app/'brave').read_bytes(),binary)
        self.assertEqual((app/'version').read_text(),'old\n')
        self.configure(download_partial_fail=False)
        self.command('-u','brave')
        (app/'brave').write_text('corrupt')
        (app/'AM-VERIFIED').write_text('Checksum failure\n')
        self.command('-u','brave')
        self.assertEqual((app/'brave').read_bytes(),binary)

    def test_brave_integrity_stale_consent_and_fresh_install_refusal(self):
        self.utility_catalog(accepted_brave_tree())
        self.command('-i','brave')
        app=Path('/opt/brave');before=snapshot_tree(app)
        rid=self.index['aliases'][BRAVE_ALIAS]['request_id']
        body=self.fixture/'tree/bodies'/f'{rid}.json'
        raw=body.read_bytes();body.write_bytes(b'[]')
        self.command('-u','brave',success=False)
        self.command('-i','brave-beta',success=False)
        self.assertFalse(Path('/opt/brave-beta').exists())
        self.assertEqual(snapshot_tree(app),before)
        body.write_bytes(raw)
        obs=self.index['entries'][rid]['observation']
        self.configure(clock=str(Decimal(epoch(obs['validated_at']))+Decimal('172800.000001')))
        self.command('-u','brave','--commit',PIN,success=False)
        self.assertEqual(snapshot_tree(app),before)
        self.command('-u','brave','--commit',PIN,'--accept-stale',PIN,rid,obs['sha256'])

    def test_brave_appman_install_standalone_and_update(self):
        self.utility_catalog(accepted_brave_tree())
        home=self.fixture/'brave-home';home.mkdir();self.prepare_home(home,appman=True)
        executable=str(home/'Applications/appman/appman')
        self.command('-i','brave-nightly',executable=executable,home=home)
        app=home/'Applications/brave-nightly'
        self.assertEqual((app/'brave-nightly').stat().st_uid,USER.pw_uid)
        self.assertTrue((home/'.local/bin/brave-nightly').samefile(app/'brave-nightly'))
        (app/'version').write_text('old\n')
        self.command('--commit',PIN,executable=str(app/'AM-updater'),home=home)
        self.assertIn('/ivan-hc/Brave-appimage/',(app/'version').read_text())


if __name__ == '__main__':
    program=unittest.main(verbosity=2,exit=False)
    result=program.result
    (OUT/'results.json').write_text(json.dumps({
        'target':os.environ.get('E2E_TARGET','unknown'), 'tests_run':result.testsRun,
        'success':result.wasSuccessful(),
        'failures':[test.id() for test,_ in result.failures],
        'errors':[test.id() for test,_ in result.errors]},indent=2)+'\n')
    sys.exit(not result.wasSuccessful())
