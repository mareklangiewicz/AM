"""Shared AppImage interface and actual manager delivery using retained metadata."""
from datetime import datetime, timedelta
from shell_lookup import epoch
import json
import os
from pathlib import Path
import re
import subprocess
import unittest

from test_shell_consumer import ShellFixture, ROOT, HELPER, PIN, ALIAS, SOURCE

APP = ROOT / 'programs/x86_64/obsidian'
LIFECYCLE = ROOT / 'modules/appimage.am'


def selector_script(path):
    return path.read_text().rsplit('am_appimage "$0" "$@"', 1)[0].replace(
        '/opt/am/modules/appimage.am', str(LIFECYCLE)) + '\nam_appimage_select_asset\n'


def previous_selector(path, revision='f8add0784'):
    source = subprocess.check_output(['git', 'show', revision+':'+str(path.relative_to(ROOT))], cwd=ROOT).decode()
    return source.split('select_asset() {\n\t')[1].split('\n}')[0]


def bound_recipe(recipe):
    # Function-level tests bind a private root explicitly; whole installer tests
    # below exercise production expansion of compact recipes.
    bindings = ('AMREPO=${AMREPO-}\nAPPS_DIR="/opt/"\n'
                'BIN_DIR="/usr/local/bin"\n'
                'DESKTOP_DIR="/usr/local/share/applications"\n'
                'CATALOG_HELPER="/opt/am/modules/catalog.am"\n')
    return recipe.replace('. "/opt/am/modules/appimage.am"',
                          bindings + '. "/opt/am/modules/appimage.am"')


class AppImageLifecycle(ShellFixture):
    def setUp(self):
        super().setUp()
        self.set_up_appimage()

    def set_up_appimage(self):
        self.root=self.path/'root'
        for p in ('usr/local/bin','usr/local/share/applications'):
            (self.root/p).mkdir(parents=True,exist_ok=True)
        self.app=self.root/'opt/obsidian'
        self.source=bound_recipe(APP.read_text()).replace('/opt/am/modules/catalog.am',str(HELPER)).replace('/opt/am/modules/appimage.am',str(LIFECYCLE))
        self.source=self.source.replace('/opt/',str(self.root)+'/opt/').replace('/usr/local/',str(self.root)+'/usr/local/')
        self.recipe=self.path/'recipe'
        self.recipe.write_text(self.source)
        self.script('wget', '''import os,pathlib,sys
p=pathlib.Path(os.environ['FIXTURE']); (p/'download').write_text(sys.argv[-1])
if os.environ.get('DOWNLOAD_FAIL'): sys.exit(9)
pathlib.Path(sys.argv[sys.argv.index('-O')+1]).write_text("#!/bin/sh\\nmkdir -p squashfs-root\\ncase $2 in\\n*.desktop) printf '[Desktop Entry]\\\\nExec=obsidian\\\\nIcon=obsidian\\\\n' > squashfs-root/obsidian.desktop ;;\\n.DirIcon) printf icon > squashfs-root/.DirIcon ;;\\nesac\\n")
''')
        self.script('notify-send','pass\n')
        self.script('appimageupdatetool',"raise RuntimeError('forbidden bypass')\n")
        self.filters=[previous_selector(APP)]
        self.expected=subprocess.run(['/bin/sh','-c',self.filters[0]],input=self.body,
                                     capture_output=True,check=True).stdout.strip().decode()

    def run_script(self, path, args=None, env=None):
        self.stage()
        return subprocess.run(['/bin/sh',str(path),*(args or ['--commit',PIN])],
                              cwd=self.path,env=env or self.env(),capture_output=True)

    def install(self):
        r=self.run_script(self.recipe)
        self.assertEqual(r.returncode,0,r.stderr)
        return self.app/'AM-updater'

    def snapshot(self):
        return {str(p.relative_to(self.root)):
                ('link',os.readlink(p)) if p.is_symlink() else
                ('file',p.read_bytes()) if p.is_file() else ('directory',)
                for p in self.root.rglob('*')}

    def test_actual_recipe_and_generated_updater_keep_filter_and_upstream_url(self):
        previous=subprocess.run(['git','show','0a21fef3c:programs/x86_64/obsidian'],
                                cwd=ROOT,capture_output=True,check=True).stdout.decode()
        legacy=re.findall(r'version=\$\(curl[^|]+\| (.*)\)',previous)
        selected=subprocess.run(['sh','-c',selector_script(APP)],input=self.body,
                                capture_output=True,check=True).stdout.strip().decode()
        self.assertEqual(selected,self.expected)
        self.assertEqual(self.filters,[legacy[0]])
        self.assertEqual(legacy[0],legacy[1])
        updater=self.install()
        self.assertEqual((self.path/'download').read_text(),self.expected)
        self.assertTrue(self.expected.startswith('https://github.com/obsidianmd/'))
        self.assertIn(str(HELPER),(self.app/'recipe.am').read_text())
        self.assertEqual(len(updater.read_text().splitlines()),3)
        (self.path/'download').unlink()
        r=self.run_script(updater)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn(b'Update not needed!',r.stdout)
        self.assertFalse((self.path/'download').exists())
        (self.app/'version').write_text('old\n')
        r=self.run_script(updater)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual((self.path/'download').read_text(),self.expected)
        self.assertEqual((self.app/'version').read_text().strip(),self.expected)
        self.assertNotIn(b'forbidden bypass',r.stderr)

    def test_recipe_and_generated_updater_refuse_before_mutation(self):
        self.tree['bodies/'+self.rid+'.json']=b'[]'
        before=self.snapshot()
        r=self.run_script(self.recipe)
        self.assertNotEqual(r.returncode,0);self.assertEqual(self.snapshot(),before)
        self.tree=dict(self.base);updater=self.install();before=self.snapshot()
        self.tree['bodies/'+self.rid+'.json']=b'[]'
        r=self.run_script(updater)
        self.assertNotEqual(r.returncode,0);self.assertIn(b'mismatch',r.stderr)
        self.assertEqual(self.snapshot(),before)

    def test_missing_helper_and_empty_selection_refuse_without_fallback(self):
        self.recipe.write_text(self.source.replace(str(HELPER),str(self.path/'missing.am')))
        before=self.snapshot();r=self.run_script(self.recipe)
        self.assertNotEqual(r.returncode,0);self.assertEqual(self.snapshot(),before)
        # Run the actual recipe with an inert body-producing helper for filter refusal.
        helper=self.path/'empty.am';helper.write_text("printf '[]\\n'\n")
        self.recipe.write_text(self.source.replace(str(HELPER),str(helper)))
        r=self.run_script(self.recipe)
        self.assertNotEqual(r.returncode,0);self.assertIn(b'Error getting link',r.stderr)
        self.assertEqual(self.snapshot(),before)

    def test_download_failure_nonzero_and_version_not_updated(self):
        updater=self.install();(self.app/'version').write_text('old\n')
        r=self.run_script(updater,env={**self.env(),'DOWNLOAD_FAIL':'1'})
        self.assertNotEqual(r.returncode,0)
        self.assertEqual((self.app/'version').read_text(),'old\n')

    def test_chmod_failure_preserves_binary_and_version_then_retry(self):
        updater=self.install()
        (self.app/'obsidian').write_bytes(b'old working binary\n')
        (self.app/'version').write_text('old\n')
        before=(self.app/'obsidian').stat().st_mode
        self.script('chmod', "import sys\nsys.stderr.write('injected chmod failure\\n')\nsys.exit(9)\n")
        result=self.run_script(updater)
        self.assertNotEqual(result.returncode,0,result.stderr)
        self.assertIn(b'injected chmod failure',result.stderr)
        self.assertEqual((self.app/'obsidian').read_bytes(),b'old working binary\n')
        self.assertEqual((self.app/'obsidian').stat().st_mode,before)
        self.assertEqual((self.app/'version').read_text(),'old\n')
        self.assertTrue((self.app/'tmp/obsidian.AppImage').is_file())
        (self.bin/'chmod').unlink()
        result=self.run_script(updater)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual((self.app/'version').read_text().strip(),self.expected)
        self.assertNotEqual((self.app/'obsidian').read_bytes(),b'old working binary\n')
        self.assertTrue(os.access(self.app/'obsidian',os.X_OK))
        self.assertFalse((self.app/'tmp').exists())

    def test_replacement_failure_preserves_binary_and_version_then_retry(self):
        updater=self.install()
        (self.app/'obsidian').write_bytes(b'old working binary\n')
        (self.app/'version').write_text('old\n')
        self.script('mv', "import sys\nsys.stderr.write('injected replacement failure\\n')\nsys.exit(9)\n")
        result=self.run_script(updater)
        self.assertNotEqual(result.returncode,0,result.stderr)
        self.assertIn(b'injected replacement failure',result.stderr)
        self.assertEqual((self.app/'obsidian').read_bytes(),b'old working binary\n')
        self.assertEqual((self.app/'version').read_text(),'old\n')
        self.assertTrue(os.access(self.app/'tmp/obsidian.AppImage',os.X_OK))
        (self.bin/'mv').unlink()
        result=self.run_script(updater)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual((self.app/'version').read_text().strip(),self.expected)
        self.assertNotEqual((self.app/'obsidian').read_bytes(),b'old working binary\n')
        self.assertFalse((self.app/'tmp').exists())

    def test_version_write_failure_reports_partial_update_and_retry_recovers(self):
        updater=self.install()
        (self.app/'obsidian').write_bytes(b'old working binary\n')
        # A directory forces a real shell redirection failure, even as root.
        # Binary replacement precedes the version write: no multi-file rollback.
        (self.app/'version').unlink()
        (self.app/'version').mkdir()
        result=self.run_script(updater)
        self.assertNotEqual(result.returncode,0,result.stderr)
        self.assertTrue((self.app/'version').is_dir())
        self.assertNotEqual((self.app/'obsidian').read_bytes(),b'old working binary\n')
        self.assertTrue(os.access(self.app/'obsidian',os.X_OK))
        self.assertTrue((self.app/'tmp').exists())
        (self.app/'version').rmdir()
        (self.app/'version').write_text('old\n')
        result=self.run_script(updater)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual((self.app/'version').read_text().strip(),self.expected)
        self.assertFalse((self.app/'tmp').exists())

    def test_fresh_install_filesystem_failure_then_retry(self):
        for failure in ('chmod','mv','version'):
            with self.subTest(failure=failure):
                if failure == 'version':
                    (self.app/'version').mkdir(parents=True)
                else:
                    self.script(failure, "import sys\nsys.stderr.write('injected filesystem failure\\n')\nsys.exit(9)\n")
                result=self.run_script(self.recipe)
                self.assertNotEqual(result.returncode,0,result.stderr)
                self.assertFalse((self.app/'AM-updater').exists())
                self.assertFalse((self.root/'usr/local/bin/obsidian').exists())
                if failure == 'version':
                    self.assertTrue((self.app/'obsidian').is_file())
                    (self.app/'version').rmdir()
                else:
                    self.assertFalse((self.app/'obsidian').exists())
                    self.assertFalse((self.app/'version').exists())
                    (self.bin/failure).unlink()
                updater=self.install()
                self.assertEqual((self.app/'version').read_text().strip(),self.expected)
                self.assertTrue((self.root/'usr/local/bin/obsidian').exists())
                self.assertEqual(len(updater.read_text().splitlines()),3)
                self.assertFalse((self.app/'tmp').exists())
                result=self.run_script(self.app/'remove')
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertFalse(self.app.exists())

    def test_manager_foreground_route_precedes_legacy_mutation_and_preserves_failure(self):
        updater=self.install()
        manager=(ROOT/'APP-MANAGER').read_text()
        route=manager[manager.index('_catalog_update() {'):manager.index('\n_use_update() {')]
        # Execute the real _use_update prelude, stopping before any legacy operation.
        prelude=manager[manager.index('_use_update() {'):manager.index('\n\t_online_check',manager.index('_use_update() {'))]
        harness=self.path/'manager-test'
        harness.write_text('_use_sync() { :; }\n_use_verify() { printf verified > "$FIXTURE/verified"; }\n'+route+'\n'+prelude+'\n echo forbidden-legacy >&2; return 99\n}\n_use_update "$@"\n')
        env={**self.env(),'APPSPATH':str(self.root/'opt'),'APPMAN_APPSPATH':str(self.path/'absent')}
        self.stage()
        r=subprocess.run(['/bin/bash',str(harness),'-u','obsidian','--commit',PIN],env=env,capture_output=True)
        self.assertEqual(r.returncode,0,r.stderr)
        before=self.snapshot();self.tree['bodies/'+self.rid+'.json']=b'[]';self.stage()
        r=subprocess.run(['/bin/bash',str(harness),'-u','obsidian','--commit',PIN],env=env,capture_output=True)
        self.assertNotEqual(r.returncode,0);self.assertNotIn(b'forbidden-legacy',r.stderr)
        self.assertEqual(self.snapshot(),before)
        self.tree=dict(self.base);self.stage()
        for args in (['-u'],['-u','--apps']):
            self.stage()
            r=subprocess.run(['/bin/bash',str(harness),*args],env=env,capture_output=True)
            self.assertEqual(r.returncode,0,r.stderr);self.assertNotIn(b'forbidden-legacy',r.stderr)

    def test_real_module_location_patch_survives_appman_and_shell_metacharacters(self):
        module_dir=self.path/'owned modules $literal `literal` & |'
        module_dir.mkdir();(module_dir/'catalog.am').symlink_to(HELPER)
        (module_dir/'appimage.am').symlink_to(LIFECYCLE)
        self.recipe.write_text(bound_recipe(APP.read_text()).replace('/usr/local/',str(self.root)+'/usr/local/'))
        source=(ROOT/'modules/install.am').read_text()
        start=source.index('\t# Embed the AM/AppMan-owned module location')
        end=source.index('\t# Patch to apply to installation scripts',start)
        patch=source[start:end]
        appman=next(line for line in source.splitlines() if "/opt/am/modules/|! s#/opt/" in line)
        harness=self.path/'patch-test'
        harness.write_text('patch_recipe() {\n'+appman+'\n'+patch+'\n}\npatch_recipe\n')
        env={**self.env(),'arg':self.recipe.name,'MODULES_PATH':str(module_dir),
             'APPSPATH':str(self.root/'opt')}
        r=subprocess.run(['/bin/bash',str(harness)],cwd=self.path,env=env,capture_output=True)
        self.assertEqual(r.returncode,0,r.stderr)
        r=self.run_script(self.recipe);self.assertEqual(r.returncode,0,r.stderr)
        r=self.run_script(self.app/'AM-updater');self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn(b'Update not needed!',r.stdout)
        # The module is required locally; patching never downloads a runtime.
        (module_dir/'catalog.am').unlink()
        r=subprocess.run(['/bin/bash',str(harness)],cwd=self.path,env=env,capture_output=True)
        self.assertNotEqual(r.returncode,0);self.assertIn(b'Missing catalog.am',r.stderr)

    def test_manager_color_filter_does_not_hide_child_exit_two(self):
        updater=self.install()
        updater.write_text('#!/bin/sh\n# AM-CATALOG-UPDATER 1\necho refused >&2\nexit 2\n')
        manager=(ROOT/'APP-MANAGER').read_text()
        route=manager[manager.index('_catalog_update() {'):manager.index('\n_use_update() {')]
        prelude=manager[manager.index('_use_update() {'):manager.index('\n\t_online_check',manager.index('_use_update() {'))]
        harness=self.path/'manager-test'
        harness.write_text('_use_verify() { printf verified > "$FIXTURE/verified"; }\n'+route+'\n'+prelude+'\n echo forbidden-legacy >&2; return 0\n}\nset -o pipefail\n_use_update "$@" | sed -e "s/none/none/"\n')
        env={**self.env(),'APPSPATH':str(self.root/'opt'),'APPMAN_APPSPATH':str(self.path/'absent')}
        r=subprocess.run(['/bin/bash',str(harness),'-u','obsidian'],env=env,capture_output=True)
        self.assertNotEqual(r.returncode,0);self.assertIn(b'refused',r.stderr)
        self.assertNotIn(b'forbidden-legacy',r.stderr)

    def test_manager_checksum_failure_is_nonzero_after_successful_preflight(self):
        updater=self.install()
        manager=(ROOT/'APP-MANAGER').read_text()
        route=manager[manager.index('_catalog_update() {'):manager.index('\n_use_update() {')]
        harness=self.path/'verify-test'
        harness.write_text('_use_verify() { echo "Checksum failure" > "$argpath/AM-VERIFIED"; }\n'+route+'\n_catalog_update "$@"\n')
        self.stage()
        r=subprocess.run(['/bin/bash',str(harness),'-u','obsidian','--commit',PIN],
                         env={**self.env(),'APPSPATH':str(self.root/'opt')},capture_output=True)
        self.assertNotEqual(r.returncode,0)
        self.assertEqual((self.app/'AM-VERIFIED').read_text(),'Checksum failure\n')

    def test_real_module_sync_keeps_reader_and_existing_standalone_updater_usable(self):
        module_dir=self.path/'managed modules';module_dir.mkdir()
        installed=module_dir/'catalog.am'
        installed.write_text('#!/bin/sh\n# AMCLI obsolete fixture reader\nexit 23\n')
        obsolete=module_dir/'obsolete.am';obsolete.write_text('# inert fixture\n')
        manager=(ROOT/'APP-MANAGER').read_text()
        cleanup=manager[manager.index('_clean_old_modules() {'):manager.index('\n_clean_amcachepath() {')]
        sync=manager[manager.index('_sync_modules() {'):manager.index('\n_sync_amcli() {')]
        harness=self.path/'sync-test'
        harness.write_text(cleanup+'\n'+sync+'''\n
_use_online_downloader() { cp "$SOURCE_MODULES/${1##*/}" "$2"; }
_use_online_reading_tool() { cat "$SOURCE_MODULES/${1##*/}"; }
AMCLI_ONLINE_CONTENT=$(cat "$MANAGER_SOURCE")
_sync_modules
''')
        env={**self.env(),'SOURCE_MODULES':str(ROOT/'modules'),'MANAGER_SOURCE':str(ROOT/'APP-MANAGER'),
             'MODULES_SOURCE':SOURCE+'/modules',
             'MODULES_PATH':str(module_dir),'DIVIDING_LINE':''}
        def synchronize():
            result=subprocess.run(['/bin/bash',str(harness)],cwd=self.path,env=env,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(installed.read_bytes(),HELPER.read_bytes())
            self.assertEqual((module_dir/'appimage.am').read_bytes(),LIFECYCLE.read_bytes())
        synchronize()
        self.assertFalse(obsolete.exists())
        self.recipe.write_text(self.source.replace(str(HELPER),str(installed)).replace(str(LIFECYCLE),str(module_dir/'appimage.am')))
        updater=self.install()
        # A subsequent sync/obsolete-module pass must preserve the helper used by
        # an already generated updater; no checkout or manager sourcing at runtime.
        synchronize()
        result=self.run_script(updater)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn(b'Update not needed!',result.stdout)
        # Initial missing-module distribution follows the same existing AM path.
        installed.unlink();synchronize()
        result=self.run_script(updater)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_failed_download_can_retry_and_refusal_preserves_interrupted_work(self):
        updater=self.install();(self.app/'version').write_text('old\n')
        result=self.run_script(updater,env={**self.env(),'DOWNLOAD_FAIL':'1'})
        self.assertNotEqual(result.returncode,0)
        self.assertTrue((self.app/'tmp').is_dir())
        (self.app/'tmp/stale.AppImage').write_bytes(b'interrupted work')
        before=self.snapshot();self.tree['bodies/'+self.rid+'.json']=b'[]'
        result=self.run_script(updater)
        self.assertNotEqual(result.returncode,0);self.assertEqual(self.snapshot(),before)
        self.tree=dict(self.base)
        result=self.run_script(updater)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual((self.app/'version').read_text().strip(),self.expected)
        self.assertFalse((self.app/'tmp').exists())

    def test_same_version_checksum_repair_starts_only_after_preflight(self):
        updater=self.install()
        (self.app/'obsidian').write_text('corrupt binary\n')
        (self.app/'AM-VERIFIED').write_text('Checksum failure\n')
        (self.path/'download').unlink()
        before=self.snapshot();self.tree['bodies/'+self.rid+'.json']=b'[]'
        result=self.run_script(updater)
        self.assertNotEqual(result.returncode,0);self.assertEqual(self.snapshot(),before)
        self.assertFalse((self.path/'download').exists())
        self.tree=dict(self.base)
        result=self.run_script(updater)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual((self.path/'download').read_text(),self.expected)
        self.assertNotEqual((self.app/'obsidian').read_text(),'corrupt binary\n')
        self.assertEqual((self.app/'version').read_text().strip(),self.expected)

    def test_launcher_only_operation_reaches_legacy_launcher_branch(self):
        self.install();before=self.snapshot()
        manager=(ROOT/'APP-MANAGER').read_text()
        functions=manager[manager.index('_catalog_update() {'):manager.index('\n_use_force_latest() {')]
        harness=self.path/'launcher-test'
        harness.write_text(functions+'''\n
_online_check() { :; }
_update_github_api_key_in_the_updater_files() { :; }
_clean_all_tmp_directories_from_appspath() { :; }
_update_determine_gh_apps_number() { :; }
_clean_amcachedir() { :; }
_update_list_updatable_apps() { :; }
_update_launchers() { echo launcher-ok; }
_use_update "$@"
''')
        env={**self.env(),'APPSPATH':str(self.root/'opt'),'APPMAN_APPSPATH':str(self.path/'absent')}
        for args in (['-u','--launcher'],['-u','--debug','--launcher'],['-u','--launcher','--debug']):
            result=subprocess.run(['/bin/bash',str(harness),*args],env=env,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn(b'launcher-ok',result.stdout)
            self.assertEqual(self.snapshot(),before)

    def run_manager_install(self, *, missing_helper=False, local_script=False, source_unavailable=False, amrepo=SOURCE, recipe=APP, app_name="obsidian", appman=False, flags=""):
        """Execute real install dispatch/functions with only external AM services stubbed."""
        module_dir=self.root/'opt/am/modules';module_dir.mkdir(parents=True,exist_ok=True)
        helper=module_dir/'catalog.am'
        (module_dir/'appimage.am').write_bytes(LIFECYCLE.read_bytes())
        if not missing_helper: helper.write_bytes(HELPER.read_bytes())
        elif helper.exists(): helper.unlink()
        cache=self.path/'manager-cache';cache.mkdir(exist_ok=True)
        data=self.path/'manager-data';data.mkdir(exist_ok=True)
        (data/'x86_64-apps').write_text('fixture inventory\n')
        recipe_source=self.path/'managed-recipe'
        # Redirect every absolute install location before any script can execute.
        recipe_source.write_text(recipe.read_text().replace('/opt/',str(self.root)+'/opt/')
                                 .replace('/usr/local/',str(self.root)+'/usr/local/'))
        module=(ROOT/'modules/install.am').read_text()
        module=module.replace('/opt/',str(self.root)+'/opt/').replace('/usr/local/',str(self.root)+'/usr/local/')
        hooks='''
_online_check() { :; }
_clean_amcachedir() { :; }
_use_online_reading_tool() { [ -n "$RECIPE_UNAVAILABLE" ] || cat "$RECIPE_SOURCE"; }
_not_an_appimage_message() { return 0; }
_check_arg_variants() { return 1; }
_use_verify() { :; }
_alt_gh_off() { :; }
_check_version() { : > "$AMCACHEDIR/version-args"; }
'''
        dispatch=module.index('\ncase "$1" in\n')
        module=module[:dispatch]+'\n'+hooks+module[dispatch:]
        harness=self.path/'install-module'
        harness.write_text(module)
        self.script('privilege-wrapper', '''import os,pathlib,subprocess,sys
p=pathlib.Path(os.environ['FIXTURE'])
with (p/'privileged-calls').open('a') as f: f.write(repr(sys.argv[1:])+'\\n')
for arg in sys.argv[1:]:
    if arg.startswith('/'): assert arg.startswith(str(p)+'/'), arg
env=dict(os.environ);env.pop('AMREPO',None) # sudo normally drops this variable
sys.exit(subprocess.run(sys.argv[1:],env=env).returncode)
''')
        self.stage()
        env={**self.env(),'AMREPO':amrepo,'CLI':'appman' if appman else 'am','AMCLI':'appman' if appman else 'am','ARCH':'x86_64','REALDIR':str(self.path),
             'APPSPATH':str(self.root/'opt'),'APPSDB':'https://fixture.invalid/programs',
             'BINDIR':str(self.root/'usr/local/bin'),'XDG_BIN_HOME':str(self.root/'usr/local/bin'),'DATADIR':str(self.root/'usr/local/share'),
             'LAUNCHERS_DIR':'applications','MODULES_PATH':str(module_dir),'AMCACHEDIR':str(cache),
             'CACHEDIR':str(cache),'AMDATADIR':str(data),'RECIPE_SOURCE':str(recipe_source),'RECIPE_UNAVAILABLE':'1' if source_unavailable else '',
             'FLAGS':flags,'SUDOCMD':str(self.bin/'privilege-wrapper'),'WGETCMD':'wget','CURLCMD':'curl',
             'WGETV':'1','WGETPROGRESS':'wget','tp_flags':'--fixture-extra','tp_extensions':'.fixture-extra'}
        target=app_name
        if local_script:
            local=self.path/app_name;local.write_text(recipe_source.read_text());target=str(local)
        return subprocess.run(['/bin/bash',str(harness),'-i',target,*flags.split()],cwd=self.path,env=env,capture_output=True)

    def test_actual_install_embeds_selected_source_for_standalone_updater(self):
        source='https://raw.githubusercontent.com/another-owner/extra.apps/feature/catalog'
        result=self.run_manager_install(amrepo=source)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(all('/another-owner/extra.apps/' in c[-1] for c in self.calls()))
        updater=self.app/'AM-updater'
        self.assertIn('AMREPO=${AMREPO-"'+source+'"}',(self.app/'recipe.am').read_text())
        # Run outside the manager with no AMREPO environment; installation persists it.
        env=self.env();env.pop('AMREPO')
        result=self.run_script(updater,env=env)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn(b'Update not needed!',result.stdout)
        self.assertTrue(all('/another-owner/extra.apps/' in c[-1] for c in self.calls()))
        # Explicit empty configuration refuses, rather than choosing the embedded source.
        before=self.snapshot()
        result=self.run_script(updater,env={**env,'AMREPO':''})
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(self.snapshot(),before)
        self.assertEqual(self.calls(),[])

    def test_manager_update_passes_current_nonexported_source_to_installed_updater(self):
        result=self.run_manager_install()
        self.assertEqual(result.returncode,0,result.stderr)
        manager=(ROOT/'APP-MANAGER').read_text()
        route=manager[manager.index('_catalog_update() {'):manager.index('\n_use_update() {')]
        harness=self.path/'source-update'
        current='https://raw.githubusercontent.com/selected-owner/selected.repo/main'
        data=self.path/'manager-data';data.mkdir(exist_ok=True)
        (data/'newrepo-on').write_text(current+'\n')
        check=manager[manager.index('_am_newrepo_check() {'):manager.index('\n_am_newrepo_check "$@"')]
        default=next(line for line in manager.splitlines() if line.startswith('AMREPO='))
        harness.write_text(default+'\n'+check+'\n_am_newrepo_check "$@"\n_use_verify() { :; }\n'+route+'\n_catalog_update "$@"\n')
        env={**self.env(),'APPSPATH':str(self.root/'opt'),'APPMAN_APPSPATH':str(self.path/'absent'),
             'AMDATADIR':str(data),'AMPATH':str(self.root/'opt/am'),'ARCH':'x86_64'}
        env.pop('AMREPO')
        self.stage()
        result=subprocess.run(['/bin/bash',str(harness),'-u','obsidian','--commit',PIN],env=env,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(all('/selected-owner/selected.repo/' in c[-1] for c in self.calls()))
        self.assertEqual(len(self.calls()),2)

    def test_source_embedding_treats_shell_metacharacters_as_data(self):
        # Exercise the real install patch with an intentionally unsupported source:
        # it must not execute interpolation while preparing the recipe or updater.
        source='https://raw.githubusercontent.com/owner/repo/$(touch INJECTED) `touch INJECTED` "$x" & |'
        result=self.run_manager_install(amrepo=source)
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'AMREPO',result.stderr)
        self.assertFalse((self.path/'INJECTED').exists())
        self.assertFalse(self.app.exists())
        self.assertEqual(self.calls(),[])

    def test_actual_install_dispatch_keeps_incomplete_app_and_launcher_on_refusal(self):
        (self.app/'tmp').mkdir(parents=True)
        (self.app/'tmp/retained').write_text('old partial download\n')
        (self.app/'remove').write_text('#!/bin/sh\nprintf removed > "$FIXTURE/removed"\n')
        (self.app/'remove').chmod(0o755)
        launcher=self.root/'usr/local/bin/obsidian';launcher.symlink_to(self.path/'missing-binary')
        # Establish the managed helper before the state snapshot; its creation is test setup.
        module_dir=self.root/'opt/am/modules';module_dir.mkdir(parents=True)
        (module_dir/'catalog.am').write_bytes(HELPER.read_bytes())
        (module_dir/'appimage.am').write_bytes(LIFECYCLE.read_bytes())
        self.tree['bodies/'+self.rid+'.json']=b'[]'
        before=self.snapshot()
        for local in (False,True):
            result=self.run_manager_install(local_script=local)
            self.assertNotEqual(result.returncode,0,result.stderr)
            self.assertIn(b'mismatch',result.stderr)
            self.assertFalse((self.path/'removed').exists())
            self.assertEqual(self.snapshot(),before)

    def test_actual_install_dispatch_creates_no_launcher_dirs_with_missing_helper(self):
        import shutil
        shutil.rmtree(self.root/'usr/local')
        (self.root/'opt/am/modules').mkdir(parents=True)
        (self.root/'opt/am/modules/appimage.am').write_bytes(LIFECYCLE.read_bytes())
        before=self.snapshot()
        result=self.run_manager_install(missing_helper=True)
        self.assertNotEqual(result.returncode,0,result.stderr)
        self.assertIn(b'Missing catalog.am',result.stderr)
        self.assertEqual(self.snapshot(),before)
        calls=(self.path/'privileged-calls').read_text()
        self.assertNotIn("'mkdir'",calls)

    def test_actual_install_dispatch_repairs_incomplete_app_after_acceptance(self):
        (self.app/'tmp').mkdir(parents=True)
        (self.app/'tmp/retained').write_text('old partial download\n')
        (self.app/'obsidian').write_text('#!/bin/sh\nexit 9\n');(self.app/'obsidian').chmod(0o755)
        launcher=self.root/'usr/local/bin/obsidian';launcher.symlink_to(self.app/'obsidian')
        remove=self.app/'remove'
        remove.write_text('#!/bin/sh\nprintf removed > "$FIXTURE/removed"\nrm -rf "'+str(self.app)+'"\nrm -f "'+str(launcher)+'"\n')
        remove.chmod(0o755)
        result=self.run_manager_install()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue((self.path/'removed').exists())
        self.assertFalse((self.app/'tmp').exists())
        self.assertEqual((self.app/'version').read_text().strip(),self.expected)
        self.assertTrue((self.app/'AM-updater').is_file())
        self.assertTrue(launcher.exists())
        self.assertIn(b'INSTALLED',result.stdout)

    def test_unavailable_recipe_retains_incomplete_install_and_broken_link(self):
        (self.app/'tmp').mkdir(parents=True)
        (self.app/'tmp/retained').write_text('old partial download\n')
        (self.app/'remove').write_text('#!/bin/sh\nprintf removed > "$FIXTURE/removed"\n')
        (self.app/'remove').chmod(0o755)
        launcher=self.root/'usr/local/bin/obsidian';launcher.symlink_to(self.path/'missing-binary')
        module_dir=self.root/'opt/am/modules';module_dir.mkdir(parents=True)
        (module_dir/'catalog.am').write_bytes(HELPER.read_bytes())
        (module_dir/'appimage.am').write_bytes(LIFECYCLE.read_bytes())
        before=self.snapshot()
        result=self.run_manager_install(source_unavailable=True)
        self.assertNotEqual(result.returncode,0,result.stderr)
        self.assertIn(b'recipe unavailable',result.stderr)
        self.assertFalse((self.path/'removed').exists())
        self.assertEqual(self.snapshot(),before)
        self.assertEqual(self.calls(),[])
        # The variant-install helper also must not delete a link on an empty read.
        module=(ROOT/'modules/install.am').read_text()
        helper=module[module.index('_check_and_install() {'):module.index('\n################################################################################',module.index('_check_and_install() {'))]
        harness=self.path/'variant-install'
        harness.write_text(helper+'\n_use_online_reading_tool() { :; }\n_check_and_install\n')
        subprocess.run(['/bin/bash',str(harness)],env={**self.env(),'APPSPATH':str(self.root/'opt'),
                       'BINDIR':str(self.root/'usr/local/bin'),'arg':'obsidian','pure_arg':'obsidian'},capture_output=True)
        self.assertEqual(self.snapshot(),before)

    def test_manager_debug_option_is_not_forwarded_as_reader_option(self):
        self.install()
        manager=(ROOT/'APP-MANAGER').read_text()
        route=manager[manager.index('_catalog_update() {'):manager.index('\n_use_update() {')]
        harness=self.path/'debug-test'
        harness.write_text(route+'\n_use_verify() { :; }\n_catalog_update "$@"\n')
        env={**self.env(),'APPSPATH':str(self.root/'opt'),'APPMAN_APPSPATH':str(self.path/'absent')}
        for args in (['-u','--debug','obsidian','--commit',PIN],['-u','obsidian','--debug','--commit',PIN]):
            self.stage()
            result=subprocess.run(['/bin/bash',str(harness),*args],env=env,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn(b'Update not needed!',result.stdout)
            self.assertEqual(len(self.calls()),2)

    def test_actual_appman_delivery_and_standalone_without_source_checkout(self):
        result=self.run_manager_install(appman=True)
        self.assertEqual(result.returncode,0,result.stderr)
        (self.path/'managed-recipe').unlink()
        self.recipe.unlink()
        result=self.run_script(self.app/'AM-updater')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn(b'Update not needed!',result.stdout)
        self.assertEqual((self.root/'usr/local/bin/obsidian').resolve(),self.app/'obsidian')

    def test_installed_launcher_and_remover_quote_literal_paths(self):
        special=self.path/"literal ' $d `literal` & |"
        self.recipe.write_text(self.source.replace(str(self.root),str(special).replace('$',r'\$').replace('`',r'\`')))
        result=self.run_script(self.recipe)
        self.assertEqual(result.returncode,0,result.stderr)
        app=special/'opt/obsidian'
        self.assertIn('Icon='+str(app/'icons/obsidian'),(special/'usr/local/share/applications/obsidian-AM.desktop').read_text())
        result=self.run_script(app/'AM-updater')
        self.assertEqual(result.returncode,0,result.stderr)
        result=subprocess.run(['sh',str(app/'remove')],capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertFalse(app.exists())

    def test_missing_lifecycle_refuses_before_mutation(self):
        self.recipe.write_text(self.source.replace(str(LIFECYCLE),str(self.path/'missing.am')))
        before=self.snapshot()
        result=self.run_script(self.recipe)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(self.snapshot(),before)

    def test_failed_download_keeps_working_binary_even_on_install_retry(self):
        self.install()
        before=(self.app/'obsidian').read_bytes()
        (self.app/'tmp').mkdir()
        result=self.run_script(self.recipe,env={**self.env(),'DOWNLOAD_FAIL':'1'})
        self.assertNotEqual(result.returncode,0)
        self.assertEqual((self.app/'obsidian').read_bytes(),before)
        result=self.run_script(self.app/'AM-updater')
        self.assertEqual(result.returncode,0,result.stderr)

    def test_manager_icons_option_persists_in_installed_recipe(self):
        result=self.run_manager_install(flags='--icons')
        self.assertEqual(result.returncode,0,result.stderr)
        desktop=self.root/'usr/local/share/applications/obsidian-AM.desktop'
        self.assertIn('Icon=obsidian\n',desktop.read_text())
        result=self.run_script(self.app/'AM-updater')
        self.assertEqual(result.returncode,0,result.stderr)


class AppImageRecipeCases:
    def setUp(self):
        super().setUp()
        self.root=self.path/'root'
        self.app=self.root/'opt'/self.app_name
        source=bound_recipe(self.recipe_path.read_text()).replace('/opt/am/modules/catalog.am',str(HELPER)).replace('/opt/am/modules/appimage.am',str(LIFECYCLE))
        self.recipe=self.path/'recipe'
        self.recipe.write_text(source.replace('/opt/',str(self.root)+'/opt/').replace(
            '/usr/local/',str(self.root)+'/usr/local/'))
        self.script('wget', '''import os,pathlib,sys
p=pathlib.Path(os.environ['FIXTURE']);(p/'download').write_text(sys.argv[-1])
if os.environ.get('DOWNLOAD_FAIL'):sys.exit(9)
pathlib.Path(sys.argv[sys.argv.index('-O')+1]).write_text("#!/bin/sh\\nmkdir -p squashfs-root\\ncase $2 in\\n*.desktop) printf '[Desktop Entry]\\\\nExec=sqlitebrowser\\\\nIcon=sqlitebrowser\\\\n' > squashfs-root/sqlitebrowser.desktop ;;\\n.DirIcon) printf icon > squashfs-root/.DirIcon ;;\\nesac\\n")
''')
        # The downloaded executable is inert extraction-only fixture code.
        wget=self.bin/'wget';wget.write_text(wget.read_text().replace('sqlitebrowser',self.app_name))
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
                  timedelta(days=2,microseconds=1)).isoformat())]*3

    def test_retained_filter_install_and_standalone_unchanged(self):
        updater=self.install()
        self.assertEqual(self.url,self.expected_url)
        self.assertEqual((self.path/'download').read_text(),self.url)
        self.assertEqual(len(self.calls()),2)
        self.assertIn('# AM-CATALOG-UPDATER 1',updater.read_text())
        (self.path/'download').unlink()
        before=self.state()
        result=self.run_script(updater)
        self.assertEqual(result.returncode,0,result.stderr)
        if getattr(self,'refresh_always',False):
            self.assertNotIn(b'Update not needed!',result.stdout)
        else:
            self.assertIn(b'Update not needed!',result.stdout)
        self.assertEqual(self.state(),before)
        self.assertEqual((self.path/'download').exists(),getattr(self,'refresh_always',False))

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

    def test_integrity_and_empty_selection_refuse_before_mutation(self):
        self.install()
        before=self.state()
        self.tree['bodies/'+self.rid+'.json']=b'[]'
        result=self.run_script(self.app/'AM-updater')
        self.assertEqual(result.returncode,3,result.stderr)
        self.assertEqual(self.state(),before)
        # Explicitly synthetic valid empty response exercises selector refusal.
        import hashlib
        index=json.loads(self.tree['index.json'])
        obs=index['entries'][self.rid]['observation']
        empty=b'[]'+b' '*4096  # Leave room for the adapter trace under the transfer ulimit.
        self.tree['bodies/'+self.rid+'.json']=empty
        obs.update(sha256=hashlib.sha256(empty).hexdigest(),bytes=len(empty))
        self.tree['index.json']=json.dumps(index).encode()
        from shell_lookup import render
        from storage import validate
        self.tree['lookup.tsv']=render(index,self.tree['index.json'])
        validate(self.tree)
        result=self.run_script(self.app/'AM-updater')
        self.assertEqual(result.returncode,3,result.stderr)
        self.assertIn(b'Error getting link',result.stderr)
        self.assertEqual(self.state(),before)

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

    def test_actual_manager_route_propagates_selected_source(self):
        self.install()
        manager=(ROOT/'APP-MANAGER').read_text()
        route=manager[manager.index('_catalog_update() {'):manager.index('\n_use_update() {')]
        harness=self.path/'manager'
        harness.write_text('AMREPO=https://raw.githubusercontent.com/selected-owner/extra.apps/main\n'
            '_use_verify() { :; }\n'+route+'\n_catalog_update "$@"\n')
        self.stage()
        result=subprocess.run(['/bin/bash',str(harness),'-u',self.app_name,'--commit',PIN],
            env={**self.env(),'APPSPATH':str(self.root/'opt')},capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(all('/selected-owner/extra.apps/' in c[-1] for c in self.calls()))
        self.assertEqual(len(self.calls()),2)

    def test_real_install_dispatch_persists_source_after_privilege_environment_loss(self):
        source='https://raw.githubusercontent.com/selected-owner/extra.apps/main'
        result=AppImageLifecycle.run_manager_install(
            self,amrepo=source,recipe=self.recipe_path,app_name=self.app_name)
        self.assertEqual(result.returncode,0,result.stderr)
        updater=self.app/'AM-updater'
        self.assertIn('AMREPO=${AMREPO-"'+source+'"}',(self.app/'recipe.am').read_text())
        env=self.env();env.pop('AMREPO')
        result=self.run_script(updater,env=env)
        self.assertEqual(result.returncode,0,result.stderr)
        if getattr(self,'refresh_always',False):
            self.assertNotIn(b'Update not needed!',result.stdout)
        else:
            self.assertIn(b'Update not needed!',result.stdout)
        self.assertTrue(all('/selected-owner/extra.apps/' in c[-1] for c in self.calls()))

    def test_actual_appman_delivery(self):
        result=AppImageLifecycle.run_manager_install(
            self,recipe=self.recipe_path,app_name=self.app_name,appman=True)
        self.assertEqual(result.returncode,0,result.stderr)
        result=self.run_script(self.app/'AM-updater')
        self.assertEqual(result.returncode,0,result.stderr)
        if getattr(self,'refresh_always',False):
            self.assertNotIn(b'Update not needed!',result.stdout)
        else:
            self.assertIn(b'Update not needed!',result.stdout)
        self.assertEqual((self.root/'usr/local/bin'/self.app_name).resolve(),self.app/self.app_name)


class SQLiteLifecycle(AppImageRecipeCases, ShellFixture):
    app_name = 'sqlitebrowser'
    recipe_path = ROOT/'programs/x86_64/sqlitebrowser'
    expected_url = ('https://github.com/sqlitebrowser/sqlitebrowser/releases/'
                    'download/v3.13.1/DB.Browser.for.SQLite-v3.13.1-x86.64-v2.AppImage')
    catalog_alias = 'https://api.github.com/repos/sqlitebrowser/sqlitebrowser/releases?per_page=100'


class NvimLifecycle(AppImageRecipeCases, ShellFixture):
    app_name = 'nvim'
    recipe_path = ROOT/'programs/x86_64/nvim'
    catalog_alias = 'https://api.github.com/repos/neovim/neovim/releases'
    expected_url = 'https://github.com/neovim/neovim/releases/download/v0.12.6/nvim-linux-x86_64.appimage'

    def test_original_install_and_update_selectors_are_preserved_once(self):
        previous=subprocess.run(['git','show','c2bcd8f82:programs/x86_64/nvim'],
                                cwd=ROOT,capture_output=True,check=True).stdout.decode()
        original=re.findall(r'version=\$\(curl[^|]+\| (.*)\)',previous)
        current=previous_selector(self.recipe_path)
        self.assertEqual(original,[current,current])
        result=subprocess.run(['sh','-c',selector_script(self.recipe_path)],input=self.body,capture_output=True,check=True)
        self.assertEqual(result.stdout.strip().decode(),self.expected_url)

    def test_mutable_url_refreshes_without_version_change(self):
        # Drive the real shared runtime with the nightly recipe policy; retained
        # stable bytes isolate refresh mechanics from release selection.
        self.recipe.write_text(self.recipe.read_text().replace(
            'set -eu\n', 'set -eu\nREFRESH_ALWAYS=true\n', 1))
        updater=self.install()
        (self.path/'download').unlink()
        result=self.run_script(updater)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue((self.path/'download').exists(), 'mutable URL was incorrectly skipped')


class NvimArmLifecycle(NvimLifecycle):
    recipe_path = ROOT/'programs/aarch64/nvim'
    expected_url = 'https://github.com/neovim/neovim/releases/download/v0.12.6/nvim-linux-arm64.appimage'

    def test_original_install_and_update_selectors_are_preserved_once(self):
        assert_original_neovim_selectors(self)


class NvimNightlyLifecycle(NvimLifecycle):
    app_name = 'nvim-nightly'
    recipe_path = ROOT/'programs/x86_64/nvim-nightly'
    expected_url = 'https://github.com/neovim/neovim/releases/download/nightly/nvim-linux-x86_64.appimage'
    refresh_always = True

    def test_original_install_and_update_selectors_are_preserved_once(self):
        assert_original_neovim_selectors(self)


class NvimArmNightlyLifecycle(NvimNightlyLifecycle):
    recipe_path = ROOT/'programs/aarch64/nvim-nightly'
    expected_url = 'https://github.com/neovim/neovim/releases/download/nightly/nvim-linux-arm64.appimage'


def assert_original_neovim_selectors(case):
    previous=subprocess.run(['git','show','e38e8b844:'+str(case.recipe_path.relative_to(ROOT))],
                            cwd=ROOT,capture_output=True,check=True).stdout.decode()
    original=re.findall(r'version=\$\(curl[^|]+\| (.*)\)',previous)
    current=previous_selector(case.recipe_path)
    case.assertEqual(original,[current,current])
    result=subprocess.run(['sh','-c',selector_script(case.recipe_path)],input=case.body,capture_output=True,check=True)
    case.assertEqual(result.stdout.strip().decode(),case.expected_url)


class AssetSelection(unittest.TestCase):
    def test_declarative_selectors_match_previous_pipelines(self):
        # Compare both accepted and rejected candidates, ordering, casing and
        # empty input against the original executable policies for every recipe.
        urls = [
            'https://github.com/obsidianmd/obsidian-releases/releases/download/v1/Obsidian.AppImage',
            'https://github.com/obsidianmd/obsidian-releases/releases/download/v1/Obsidian-arm64.AppImage',
            'https://github.com/sqlitebrowser/sqlitebrowser/releases/download/v3.13.1/db-x86.64.AppImage',
            'https://github.com/sqlitebrowser/sqlitebrowser/releases/download/3.13.1/db-x86_64.AppImage',
            'https://github.com/sqlitebrowser/sqlitebrowser/releases/download/v3-rc1/db-x86_64.AppImage',
            'https://github.com/sqlitebrowser/sqlitebrowser/releases/download/continuous/db-x86_64.AppImage',
            'https://github.com/sqlitebrowser/sqlitebrowser/releases/download/dev/db-x86_64.AppImage',
            'https://github.com/neovim/neovim/releases/download/v0.12.6/nvim-linux-x86_64.appimage',
            'https://github.com/neovim/neovim/releases/download/v0.12.6/nvim-linux-arm64.appimage',
            'https://github.com/neovim/neovim/releases/download/nightly/nvim-linux-x86_64.appimage',
            'https://github.com/neovim/neovim/releases/download/nightly/nvim-linux-arm64.appimage',
            'https://github.com/neovim/neovim/releases/download/NIGHTLY/nvim-linux-x86_64.appimage',
            'https://github.com/neovim/neovim/releases/download/nightly/nvim-linux-i686.appimage',
            'https://github.com/neovim/neovim/releases/download/nightly/nvim-linux-aarch64.appimage',
            'https://example.org/x86_64.AppImage',
            'https://example.org/I386.AppImage',
            'https://example.org/file.tar.gz',
        ]
        recipes = [ROOT/'programs'/arch/app for arch,app in
                   [('x86_64','obsidian'),('x86_64','sqlitebrowser'),
                    ('x86_64','nvim'),('aarch64','nvim'),
                    ('x86_64','nvim-nightly'),('aarch64','nvim-nightly')]]
        cases = [[], urls, list(reversed(urls)), [url.upper() for url in urls]]
        cases += [[url] for url in urls]
        for recipe in recipes:
            old=previous_selector(recipe)
            new=selector_script(recipe)
            for candidates in cases:
                with self.subTest(recipe=str(recipe.relative_to(ROOT)), candidates=candidates):
                    body=json.dumps({'assets':[{'browser_download_url':url} for url in candidates]}).encode()
                    before=subprocess.run(['sh','-c',old],input=body,capture_output=True,check=True)
                    after=subprocess.run(['sh','-c',new],input=body,capture_output=True,check=True)
                    self.assertEqual(after.stdout,before.stdout)

    def test_custom_selector_takes_precedence_and_propagates_failure(self):
        for status in (0,7):
            script = (f'. "{LIFECYCLE}"\nASSET_EXCLUDE=.*\n'
                      'select_asset() { cat; return '+str(status)+'; }\n'
                      'am_appimage_select_asset\n')
            result=subprocess.run(['sh','-c',script],input=b'custom\n',capture_output=True)
            self.assertEqual(result.stdout,b'custom\n')
            self.assertEqual(result.returncode,status)
