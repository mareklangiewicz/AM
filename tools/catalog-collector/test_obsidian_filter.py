"""Actual recipe/generated updater in temporary roots with stubbed app operations."""
import json
import os
from pathlib import Path
import re
import subprocess
import unittest

from test_shell_consumer import ShellFixture, ROOT, HELPER, PIN, ALIAS, SOURCE

APP = ROOT / 'programs/x86_64/obsidian'


class ObsidianFilter(ShellFixture):
    def setUp(self):
        super().setUp()
        self.root=self.path/'root'
        for p in ('usr/local/bin','usr/local/share/applications'):
            (self.root/p).mkdir(parents=True,exist_ok=True)
        self.app=self.root/'opt/obsidian'
        self.source=APP.read_text().replace('/opt/am/modules/catalog.am',str(HELPER))
        self.source=self.source.replace('/opt/',str(self.root)+'/opt/').replace('/usr/local/',str(self.root)+'/usr/local/')
        self.recipe=self.path/'recipe'
        self.recipe.write_text(self.source)
        self.script('wget', '''import os,pathlib,sys
p=pathlib.Path(os.environ['FIXTURE']); (p/'download').write_text(sys.argv[-1])
if os.environ.get('DOWNLOAD_FAIL'): sys.exit(9)
pathlib.Path('Obsidian.AppImage').write_text("#!/bin/sh\\nmkdir -p squashfs-root\\ncase $2 in\\n*.desktop) printf '[Desktop Entry]\\\\nExec=obsidian\\\\nIcon=obsidian\\\\n' > squashfs-root/obsidian.desktop ;;\\n.DirIcon) printf icon > squashfs-root/.DirIcon ;;\\nesac\\n")
''')
        self.script('notify-send','pass\n')
        self.script('appimageupdatetool',"raise RuntimeError('forbidden bypass')\n")
        self.filters=re.findall(r'version=\$\(printf[^|]+\| (.*)\)',APP.read_text())
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
        self.assertEqual(self.filters,legacy)
        updater=self.install()
        self.assertEqual((self.path/'download').read_text(),self.expected)
        self.assertTrue(self.expected.startswith('https://github.com/obsidianmd/'))
        self.assertIn(str(HELPER),updater.read_text())
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

    def test_manager_foreground_route_precedes_legacy_mutation_and_preserves_failure(self):
        updater=self.install()
        manager=(ROOT/'APP-MANAGER').read_text()
        route=manager[manager.index('_catalog_update() {'):manager.index('\n_use_update() {')]
        # Execute the real _use_update prelude, stopping before any legacy operation.
        prelude=manager[manager.index('_use_update() {'):manager.index('\n\t_online_check',manager.index('_use_update() {'))]
        harness=self.path/'manager-test'
        harness.write_text('_use_verify() { printf verified > "$FIXTURE/verified"; }\n'+route+'\n'+prelude+'\n echo forbidden-legacy >&2; return 99\n}\n_use_update "$@"\n')
        env={**self.env(),'APPSPATH':str(self.root/'opt'),'APPMAN_APPSPATH':str(self.path/'absent')}
        self.stage()
        r=subprocess.run(['/bin/bash',str(harness),'-u','obsidian','--commit',PIN],env=env,capture_output=True)
        self.assertEqual(r.returncode,0,r.stderr)
        before=self.snapshot();self.tree['bodies/'+self.rid+'.json']=b'[]';self.stage()
        r=subprocess.run(['/bin/bash',str(harness),'-u','obsidian','--commit',PIN],env=env,capture_output=True)
        self.assertNotEqual(r.returncode,0);self.assertNotIn(b'forbidden-legacy',r.stderr)
        self.assertEqual(self.snapshot(),before)
        for args in (['-u'],['-u','--apps'],['-u','another','obsidian']):
            r=subprocess.run(['/bin/bash',str(harness),*args],env=env,capture_output=True)
            self.assertNotEqual(r.returncode,0);self.assertNotIn(b'forbidden-legacy',r.stderr)

    def test_real_module_location_patch_survives_appman_and_shell_metacharacters(self):
        module_dir=self.path/'owned modules $literal `literal` & |'
        module_dir.mkdir();(module_dir/'catalog.am').symlink_to(HELPER)
        self.recipe.write_text(APP.read_text().replace('/usr/local/',str(self.root)+'/usr/local/'))
        source=(ROOT/'modules/install.am').read_text()
        start=source.index('\t# Embed the AM/AppMan-owned module location')
        end=source.index('\t# Patch to apply to installation scripts',start)
        patch=source[start:end]
        appman=next(line for line in source.splitlines() if "catalog.am\"|! s#/opt/" in line)
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
        synchronize()
        self.assertFalse(obsolete.exists())
        self.recipe.write_text(self.source.replace(str(HELPER),str(installed)))
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

    def run_manager_install(self, *, missing_helper=False, local_script=False, source_unavailable=False, amrepo=SOURCE):
        """Execute real install dispatch/functions with only external AM services stubbed."""
        module_dir=self.root/'opt/am/modules';module_dir.mkdir(parents=True,exist_ok=True)
        helper=module_dir/'catalog.am'
        if not missing_helper: helper.write_bytes(HELPER.read_bytes())
        elif helper.exists(): helper.unlink()
        cache=self.path/'manager-cache';cache.mkdir(exist_ok=True)
        data=self.path/'manager-data';data.mkdir(exist_ok=True)
        (data/'x86_64-apps').write_text('fixture inventory\n')
        recipe_source=self.path/'managed-recipe'
        # Redirect every absolute install location before any script can execute.
        recipe_source.write_text(APP.read_text().replace('/opt/',str(self.root)+'/opt/')
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
        env={**self.env(),'AMREPO':amrepo,'CLI':'am','AMCLI':'am','ARCH':'x86_64','REALDIR':str(self.path),
             'APPSPATH':str(self.root/'opt'),'APPSDB':'https://fixture.invalid/programs',
             'XDG_BIN_HOME':str(self.root/'usr/local/bin'),'DATADIR':str(self.root/'usr/local/share'),
             'LAUNCHERS_DIR':'applications','MODULES_PATH':str(module_dir),'AMCACHEDIR':str(cache),
             'CACHEDIR':str(cache),'AMDATADIR':str(data),'RECIPE_SOURCE':str(recipe_source),'RECIPE_UNAVAILABLE':'1' if source_unavailable else '',
             'SUDOCMD':str(self.bin/'privilege-wrapper'),'WGETCMD':'wget','CURLCMD':'curl',
             'WGETV':'1','WGETPROGRESS':'wget','tp_flags':'--fixture-extra','tp_extensions':'.fixture-extra'}
        target='obsidian'
        if local_script:
            local=self.path/'obsidian';local.write_text(recipe_source.read_text());target=str(local)
        return subprocess.run(['/bin/bash',str(harness),'-i',target],cwd=self.path,env=env,capture_output=True)

    def test_actual_install_embeds_selected_source_for_standalone_updater(self):
        source='https://raw.githubusercontent.com/another-owner/extra.apps/feature/catalog'
        result=self.run_manager_install(amrepo=source)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(all('/another-owner/extra.apps/' in c[-1] for c in self.calls()))
        updater=self.app/'AM-updater'
        self.assertIn('AMREPO=${AMREPO-"'+source+'"}',updater.read_text())
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
