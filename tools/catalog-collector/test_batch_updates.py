"""Actual command dispatch across managed and legacy apps; no host/network work."""
import subprocess
from datetime import datetime, timedelta
from shell_lookup import epoch
from test_shell_consumer import ShellFixture, ROOT, HELPER, PIN, SOURCE
import test_appimage_lifecycle as lifecycle
LIFECYCLE = lifecycle.LIFECYCLE


class BatchUpdates(ShellFixture):
    def setUp(self):
        super().setUp()
        lifecycle.AppImageLifecycle.set_up_appimage(self)
        date=self.bin/'date'
        date.write_text(date.read_text().replace('import json, os, pathlib', 'import json, os, pathlib, sys').replace(
            'print(t.pop(0) if len(t)>1 else t[0])',
            "value=t.pop(0) if len(t)>1 else t[0]; print(value.split('.')[0] if sys.argv[-1] == '+%s' else value)"))
    run_script = lifecycle.AppImageLifecycle.run_script
    install = lifecycle.AppImageLifecycle.install
    snapshot = lifecycle.AppImageLifecycle.snapshot

    def second_catalog_app(self):
        recipe = self.path/'sqlite-recipe'
        source = (ROOT/'programs/x86_64/sqlitebrowser').read_text()
        source = source.replace('/opt/am/modules/catalog.am',str(HELPER)).replace(
            '/opt/am/modules/appimage.am',str(LIFECYCLE))
        recipe.write_text(source.replace('/opt/',str(self.root)+'/opt/').replace(
            '/usr/local/',str(self.root)+'/usr/local/'))
        result = self.run_script(recipe)
        self.assertEqual(result.returncode,0,result.stderr)
        return self.root/'opt/sqlitebrowser'

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

    def test_no_argument_updates_both_categories_and_syncs(self):
        self.install();self.second_catalog_app();legacy=self.legacy()
        result=self.manager(['-u'])
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn(b'obsidian: unchanged',result.stdout)
        self.assertIn(b'sqlitebrowser: unchanged',result.stdout)
        self.assertIn(b'legacy: updated',result.stdout)
        self.assertEqual((legacy/'version').read_text(),'new')
        self.assertEqual((self.path/'services').read_text(),'onlinesync')
        self.assertEqual(len(self.calls()),4) # one ref, one lookup, two bodies
        self.assertEqual(len((self.path/'verifications').read_text().splitlines()),3)
        self.assertNotIn(b'forbidden',result.stderr)

    def test_explicit_batch_options_and_duplicate_target(self):
        self.install();self.second_catalog_app();self.legacy()
        source='https://raw.githubusercontent.com/selected-owner/selected.repo/feature/catalog'
        result=self.manager(['-u','--debug','sqlitebrowser','legacy','obsidian','obsidian','--commit',PIN],source)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.count(b'obsidian: unchanged'),1)
        self.assertEqual(len(self.calls()),3) # one lookup, two bodies, explicit pin
        self.assertTrue(all('/selected-owner/selected.repo/' in c[-1] for c in self.calls()))
        self.assertEqual((self.path/'legacy-runs').read_text(),'ran')
        self.assertEqual((self.path/'services').read_text(),'online')

    def test_metadata_refusal_preserves_partial_app_and_continues_legacy(self):
        self.install();legacy=self.legacy()
        (self.app/'tmp').mkdir();(self.app/'tmp/retained').write_text('keep')
        before={p.name:p.read_bytes() for p in self.app.iterdir() if p.is_file()}
        self.tree['bodies/'+self.rid+'.json']=b'[]'
        result=self.manager(['-u','obsidian','legacy','--commit',PIN],pipe=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'obsidian: refused',result.stderr)
        self.assertIn(b'legacy: updated',result.stdout)
        self.assertEqual((self.app/'tmp/retained').read_text(),'keep')
        self.assertEqual({p.name:p.read_bytes() for p in self.app.iterdir() if p.is_file()},before)
        self.assertEqual((legacy/'version').read_text(),'new')
        self.assertEqual((self.path/'verifications').read_text().splitlines(),[str(legacy)])

    def test_legacy_failure_continues_catalog_and_noarg_preserves_failure_after_sync(self):
        self.install();self.legacy(code=9)
        result=self.manager(['-u'])
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'legacy: failed',result.stderr)
        self.assertIn(b'obsidian: unchanged',result.stdout)
        self.assertEqual((self.path/'verifications').read_text().splitlines(),[str(self.app)])
        self.assertEqual((self.path/'services').read_text(),'onlinesync')

    def test_download_and_checksum_failures_continue_and_aggregate(self):
        self.install();self.second_catalog_app();self.legacy(checksum=True)
        (self.app/'version').write_text('old\n')
        # Fail just the Obsidian binary download; other selected apps still run.
        wget=self.bin/'wget';wget.write_text(wget.read_text().replace(
            "if os.environ.get('DOWNLOAD_FAIL'):","if 'obsidian' in sys.argv[-1]:"))
        result=self.manager(['-u','obsidian','legacy','sqlitebrowser','--commit',PIN])
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'obsidian: failed',result.stderr)
        self.assertIn(b'legacy: failed',result.stderr)
        self.assertIn(b'sqlitebrowser: unchanged',result.stdout)
        self.assertEqual((self.app/'version').read_text(),'old\n')

    def test_stale_consent_is_exact_per_app_even_with_shared_lookup(self):
        self.install();sqlite=self.second_catalog_app();self.legacy()
        # All retained entries are now stale, but only Obsidian has exact consent.
        self.now=[epoch((datetime.fromisoformat(self.obs['validated_at'])+
            timedelta(days=4)).isoformat())]*3
        result=self.manager(['-u','obsidian','sqlitebrowser','legacy',*self.consent()])
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'obsidian: unchanged',result.stdout)
        self.assertIn(b'sqlitebrowser: refused',result.stderr)
        self.assertIn(b'legacy: updated',result.stdout)
        self.assertEqual(len(self.calls()),2) # lookup + consented body only
        self.assertFalse((sqlite/'tmp').exists())

    def test_apps_flag_and_missing_locked_targets(self):
        self.install();locked=self.legacy('locked')
        (locked/'AM-updater').rename(locked/'AM-LOCK')
        result=self.manager(['-u','--apps','--commit',PIN])
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertNotIn(b'locked:',result.stdout+result.stderr)
        self.assertFalse((self.path/'services').exists())
        result=self.manager(['-u','missing','locked','obsidian','--commit',PIN])
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'missing: failed',result.stderr)
        self.assertIn(b'locked, read-only or no updater',result.stderr)
        self.assertIn(b'obsidian: unchanged',result.stdout)

    def test_failed_acquisition_is_latched_without_repin_or_legacy_fallback(self):
        self.install();self.second_catalog_app();self.legacy()
        curl=self.bin/'curl'
        curl.write_text(curl.read_text().replace("print(os.environ.get('HTTP_STATUS','200'),end='')", "print('503',end='')"))
        result=self.manager(['-u','obsidian','sqlitebrowser','legacy'])
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(result.stderr.count(b': refused'),2)
        self.assertIn(b'legacy: updated',result.stdout)
        self.assertEqual(len(self.calls()),1)
        self.assertIn(b'already refused',result.stderr)

    def test_appman_path_and_command_session_cleanup(self):
        self.install()
        other=self.path/'user apps';other.mkdir()
        import shutil
        # Same app exists at both roots; its saved recipe points at its own root.
        app=other/'obsidian';shutil.copytree(self.app,app)
        recipe=app/'recipe.am';recipe.write_text(recipe.read_text().replace(str(self.root/'opt'),str(other)))
        (app/'AM-updater').write_text('#!/bin/sh\n# AM-CATALOG-UPDATER 1\nexec sh "'+str(recipe)+'" --am-update "$@"\n')
        # Read the private session pathname from the updater without changing its work.
        updater=self.app/'AM-updater'
        updater.write_text(updater.read_text().replace('exec sh ', 'printf "%s" "$AM_CATALOG_SESSION" > "$FIXTURE/session-path"\nexec sh '))
        # manager env allows configured AppMan root, including spaces.
        original=self.env
        self.env=lambda: {**original(),'APPMAN_APPSPATH_OVERRIDE':str(other)}
        result=self.manager(['-u','obsidian','--commit',PIN])
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.count(b'obsidian: unchanged'),2)
        self.assertEqual(len(self.calls()),3)
        session=(self.path/'session-path').read_text()
        from pathlib import Path
        self.assertFalse(Path(session).exists())

    def test_hidden_apps_are_excluded_and_explicit_hidden_target_fails(self):
        self.install();hidden=self.legacy('hidden')
        (hidden/'remove.old').write_text('hidden marker')
        result=self.manager(['-u','--apps','--commit',PIN])
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertFalse((self.path/'legacy-runs').exists())
        result=self.manager(['-u','hidden','obsidian','--commit',PIN])
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'hidden, locked',result.stderr)
        self.assertIn(b'obsidian: unchanged',result.stdout)
        self.assertFalse((self.path/'legacy-runs').exists())

    def test_symlinked_duplicate_roots_update_once(self):
        self.install()
        alias=self.path/'alias';alias.symlink_to(self.root/'opt')
        original=self.env
        self.env=lambda: {**original(),'APPMAN_APPSPATH_OVERRIDE':str(alias)}
        result=self.manager(['-u','--apps','--commit',PIN])
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.count(b'obsidian: unchanged'),1)
        self.assertEqual(len(self.calls()),2)

    def test_unsupported_options_refuse_before_any_app_work(self):
        self.install();self.legacy()
        before=self.snapshot()
        result=self.manager(['-u','legacy','obsidian','--unknown'])
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'Unsupported update option',result.stderr)
        self.assertEqual(self.snapshot(),before)
        self.assertEqual(self.calls(),[])
        self.assertFalse((self.path/'legacy-runs').exists())

    def test_legacy_only_upgrade_preserves_failure_and_never_reads_catalog(self):
        self.legacy('first',code=7);self.legacy('second')
        result=self.manager(['upgrade','first','second'])
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'first: failed',result.stderr)
        self.assertIn(b'second: updated',result.stdout)
        self.assertEqual(self.calls(),[])
        self.assertEqual((self.path/'legacy-runs').read_text(),'ranran')

    def test_freshness_is_rechecked_for_later_apps_in_one_command(self):
        self.install();self.second_catalog_app()
        fresh=self.now[0]
        stale=epoch((datetime.fromisoformat(self.obs['validated_at'])+
            timedelta(days=4)).isoformat())
        self.now=[fresh]*3+[stale]*3
        result=self.manager(['-U','obsidian','sqlitebrowser','--commit',PIN])
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'obsidian: unchanged',result.stdout)
        self.assertIn(b'sqlitebrowser: refused',result.stderr)
        self.assertEqual(len(self.calls()),2)

    def test_noarg_sync_failure_is_nonzero_after_successful_apps(self):
        self.install()
        original=self.env
        self.env=lambda: {**original(),'SYNC_FAIL':'8'}
        result=self.manager(['-u'])
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'obsidian: unchanged',result.stdout)
        self.assertEqual((self.path/'services').read_text(),'sync')
