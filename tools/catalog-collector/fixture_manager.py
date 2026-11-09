"""Disposable harness for actual installer and manager dispatch functions."""
import os
from pathlib import Path
import subprocess
from fixture_recipes import fixtures
from yaml_publication import git
from fixture_v3 import publish_local
from test_yaml_reader import SCHEMA

ROOT = Path(__file__).resolve().parents[2]
NOW = '2026-10-27T15:18:00Z'
SOURCE = 'https://raw.githubusercontent.com/selected-owner/selected.repo/feature/catalog'
APP = ROOT/'programs/x86_64/obsidian'
LIFECYCLE = ROOT/'modules/appimage.am'


def setup_catalog(cls):
    import tempfile
    saved = fixtures()
    cls.repositories = {str(k): v[2] for k, v in saved.items()}
    cls.apps = {'obsidian':262342594, 'nvim':16408992, 'nvim-nightly':16408992}
    cls.tmp = tempfile.TemporaryDirectory(prefix='yaml-fixture-')
    cls.addClassCleanup(cls.tmp.cleanup)
    cls.shared = Path(cls.tmp.name)
    cls.repo = cls.shared/'git'; cls.repo.mkdir()
    git(cls.repo, 'init', '--bare')
    cls.pin = publish_local(cls.repo, cls.apps, cls.repositories, schema=SCHEMA,
                           max_file_bytes=2097152, expected_parent=None)


class ManagerHarness:
    def run_manager_install(self, *, local_script=False, source_unavailable=False, amrepo=SOURCE, recipe=APP, app_name="obsidian", appman=False, flags=""):
        """Execute real install dispatch/functions with only external AM services stubbed."""
        module_dir=self.root/'opt/am/modules';module_dir.mkdir(parents=True,exist_ok=True)
        (module_dir/'appimage.am').write_bytes(LIFECYCLE.read_bytes())
        cache=self.path/'manager-cache';cache.mkdir(exist_ok=True)
        data=self.path/'manager-data';data.mkdir(exist_ok=True)
        (data/'x86_64-apps').write_text('fixture inventory\n')
        recipe_source=self.path/'managed-recipe'
        # Redirect every absolute install location before any script can execute.
        recipe_text = recipe.read_text()
        recipe_source.write_text(recipe_text.replace('/opt/',str(self.root)+'/opt/')
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

    def snapshot(self):
        return {str(p.relative_to(self.root)):
                ('link',os.readlink(p)) if p.is_symlink() else
                ('file',p.read_bytes()) if p.is_file() else ('directory',)
                for p in self.root.rglob('*')}

    def manager(self, args, source=SOURCE, *, pipe=False):
        manager=(ROOT/'APP-MANAGER').read_text()
        updater=manager[manager.index('_update_determine_gh_apps_number() {'):
                        manager.index('\n_use_force_latest() {')]
        token=manager[manager.index('_update_github_api_key_in_the_updater_files() {'):
                      manager.index('\n################################################################',manager.index('_update_github_api_key_in_the_updater_files() {'))]
        dispatch=manager[manager.index("\t'update'|'upgrade'|'-u'|'-U')"):
                         manager.index("\t'version'|'-v'|'--version')")]
        harness=self.path/'batch-manager'
        harness.write_text(token+'\n'+updater+'''
_online_check() { printf online >> "$FIXTURE/services"; }
_use_sync() { printf sync >> "$FIXTURE/services"; return "${SYNC_FAIL:-0}"; }
_use_verify() { printf '%s\\n' "$argpath" >> "$FIXTURE/verifications"; }
_alt_gh_on() { echo forbidden-proxy >&2; return 99; }
_alt_gh_off() { :; }
_detect_appman_apps() { APPMAN_APPSPATH=${APPMAN_APPSPATH_OVERRIDE:-$APPMAN_APPSPATH}; }
_determine_args() { echo forbidden-discovery >&2; exit 99; }
_clean_all_tmp_directories_from_appspath() { echo forbidden-cleanup >&2; exit 99; }
'''+"\nAMREPO='"+source+"'\n"+('NO_COLOR=1\n' if pipe else '')+'case "$1" in\n'+dispatch+'esac\n')
        self.stage()
        env={**self.env(),'APPSPATH':str(self.root/'opt'),
             'APPMAN_APPSPATH':str(self.path/'absent'),'AMCLI':'am','WGETV':'present',
             'ghapikey_file':str(self.path/'no-token')}
        return subprocess.run(['/bin/bash',str(harness),*args],env=env,capture_output=True)

    def legacy(self, name='legacy', code=0, checksum=False):
        app=self.root/'opt'/name;app.mkdir(parents=True)
        (app/'version').write_text('old\n')
        (app/'AM-updater').write_text('#!/bin/sh\n'
            'printf ran >> "$FIXTURE/legacy-runs"\n'
            + ('printf new > version\n' if code == 0 else '')
            + ('printf "Checksum failure\\n" > AM-VERIFIED\n' if checksum else '')
            + f'exit {code}\n')
        (app/'AM-updater').chmod(0o755)
        return app
