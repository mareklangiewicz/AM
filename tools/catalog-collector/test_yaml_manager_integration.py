"""Actual candidate install/batch/sync functions with local Git-backed fake HTTP."""
import copy
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

import fixture_manager as harness
from fixture_manager import ROOT, NOW
from fixture_v3 import publish_local

SOURCE='https://raw.githubusercontent.com/selected-owner/selected.repo/feature/catalog'
OLD='2026-11-11T15:18:01Z'  # 15 days after NOW, when the fixture's releases were seen
RUNTIME=('catalog-yaml.am','catalog-contract-reader.am','catalog-contract-parser.am','catalog-contract-tables.am','catalog-yaml-policy.am')


class YAMLManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        harness.setup_catalog(cls)

    def setUp(self):
        self.tmpcase=tempfile.TemporaryDirectory(prefix='yaml-manager-')
        self.addCleanup(self.tmpcase.cleanup)
        self.path=Path(self.tmpcase.name); self.bin=self.path/'bin'; self.bin.mkdir()
        self.root=self.path/'root'; self.module_dir=self.root/'opt/am/modules'
        self.module_dir.mkdir(parents=True)
        for name in RUNTIME:
            shutil.copyfile(ROOT/'modules'/name,self.module_dir/name)
        self.clock=NOW
        self.script('date', '''import datetime,json,os,pathlib,sys
p=pathlib.Path(os.environ['FIXTURE'])/'clock-sequence'
if p.exists():
 values=json.loads(p.read_text());s=values.pop(0) if len(values)>1 else values[0];p.write_text(json.dumps(values))
else: s=os.environ['CLOCK']
d=datetime.datetime.fromisoformat(s.replace('Z','+00:00')); epoch=int(d.timestamp())
f=sys.argv[-1]
if f=='+%s %Y-%m-%dT%H:%M:%SZ': print(str(epoch)+' '+s)
elif f=='+%s.%N': print(str(epoch)+'.000000000')
elif f=='+%s': print(epoch)
else: raise ValueError(f)
''')
        self.script('curl', '''import json,os,pathlib,re,subprocess,sys
p=pathlib.Path(os.environ['FIXTURE']); args=sys.argv[1:]; url=args[-1]
with (p/'calls').open('a') as f: f.write(json.dumps(args)+'\\n')
assert args[0]=='-q' and '-L' not in args
assert args[args.index('--noproxy')+1]=='*'
assert args[args.index('--proto')+1]=='=https'
assert args[args.index('--max-redirs')+1]=='0'
assert not any('Authorization' in a for a in args)
def git(*a):
 return subprocess.run(['/usr/bin/git','-C',os.environ['REMOTE'],*a],capture_output=True,check=True).stdout
expected=os.environ.get('EXPECTED_REPOSITORY','selected-owner/selected.repo')
if url=='https://api.github.com/repos/'+expected+'/commits/heads/release-catalog-v3':
 raw=(p/'ref').read_bytes() if (p/'ref').exists() else (os.environ['PIN']+'\\n').encode()
else:
 match=re.fullmatch(r'https://raw.githubusercontent.com/'+expected+r'/([0-9a-f]{40})/(catalog\\.yaml|apps\\.yaml|repositories/[a-z0-9_.+-]+\\.yaml)',url)
 assert match,url
 pin,name=match.groups(); raw=git('show',pin+':'+name)
 if name=='apps.yaml' and (p/'move-to').exists():
  (p/'ref').write_bytes((p/'move-to').read_bytes()); (p/'move-to').unlink()
 if os.environ.get('BAD_SUFFIX') and name.startswith('repositories/'):
  raw+=b'unknown: true\\n'
 if os.environ.get('OVERSIZE') and name=='apps.yaml': raw=b'x'*2097153
pathlib.Path(args[args.index('--output')+1]).write_bytes(raw)
print(os.environ.get('HTTP_STATUS','200'),end='')
''')
        self.script('wget', '''import os,pathlib,sys
p=pathlib.Path(os.environ['FIXTURE'])
with (p/'downloads').open('a') as f: f.write(sys.argv[-1]+'\\n')
if os.environ.get('DOWNLOAD_FAIL'): sys.exit(9)
pathlib.Path(sys.argv[sys.argv.index('-O')+1]).write_text("#!/bin/sh\\napp=${0##*/}\\nmkdir -p squashfs-root\\ncase $2 in\\n*.desktop) printf '[Desktop Entry]\\\\nExec=%s --no-sandbox\\\\nIcon=%s\\\\n' \\\"$app\\\" \\\"$app\\\" > \\\"squashfs-root/$app.desktop\\\" ;;\\n.DirIcon) printf icon > squashfs-root/.DirIcon ;;\\nesac\\n")
''')
        self.script('notify-send','pass\n')
        self.script('appimageupdatetool',"raise RuntimeError('forbidden fallback')\n")
        self.app=self.root/'opt/obsidian'

    def script(self,name,body):
        p=self.bin/name;p.write_text('#!'+sys.executable+'\n'+body);p.chmod(0o755)

    def env(self):
        return dict(os.environ,PATH=str(self.bin)+':'+os.environ['PATH'],FIXTURE=str(self.path),
            REMOTE=str(self.repo),PIN=self.pin,CLOCK=self.clock,AMREPO=SOURCE)

    def stage(self):
        (self.path/'calls').unlink(missing_ok=True)

    def calls(self):
        path=self.path/'calls'
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def run_manager_install(self, **kwargs):
        return harness.ManagerHarness.run_manager_install(self, **kwargs)
    snapshot=harness.ManagerHarness.snapshot
    manager=harness.ManagerHarness.manager
    legacy=harness.ManagerHarness.legacy

    live=harness.ManagerHarness.live
    recipe_file=harness.ManagerHarness.recipe_file

    def install(self,recipe='x86_64/obsidian',appman=False):
        r=self.run_manager_install(amrepo=SOURCE,recipe=self.recipe_file(recipe),
                                   app_name=recipe.split('/')[1],appman=appman)
        self.assertEqual(r.returncode,0,r.stderr)
        return self.root/'opt'/recipe.split('/')[1]

    def standalone(self,updater,*args,env=None):
        self.stage()
        return subprocess.run(['/bin/sh',str(updater),*args],env=env or self.env(),
                              cwd=self.path,capture_output=True)

    def test_actual_manager_install_all_cohort_paths_and_standalone_source(self):
        for recipe in ('x86_64/obsidian','x86_64/nvim','aarch64/nvim',
                       'x86_64/nvim-nightly','aarch64/nvim-nightly'):
            with self.subTest(recipe=recipe):
                app=self.install(recipe)
                installed=(app/'recipe.am').read_text()
                self.assertIn('CATALOG_FORMAT=3',installed)
                self.assertIn(str(self.module_dir/'catalog-yaml.am'),installed)
                self.assertIn('AMREPO=${AMREPO-"'+SOURCE+'"}',installed)
                self.assertTrue((app/'version').read_text().startswith('https://github.com/'))
                env=self.env();env.pop('AMREPO')
                r=self.standalone(app/'AM-updater',env=env)
                self.assertEqual(r.returncode,0,r.stderr)
                self.assertEqual(len(self.calls()),4)
                before=self.snapshot()
                r=self.standalone(app/'AM-updater',env={**env,'AMREPO':''})
                self.assertNotEqual(r.returncode,0);self.assertEqual(self.snapshot(),before)
                self.assertEqual(self.calls(),[])

    def test_missing_runtime_refuses_before_installation_and_appman_paths(self):
        parser=self.module_dir/'catalog-contract-parser.am'; original=parser.read_bytes();parser.unlink()
        before=self.snapshot()
        r=self.run_manager_install(amrepo=SOURCE)
        self.assertNotEqual(r.returncode,0); self.assertFalse(self.app.exists())
        self.assertEqual(self.calls(),[])
        parser.write_bytes(original)
        app=self.install(appman=True)
        self.assertIn(str(self.module_dir/'catalog-yaml.am'),(app/'recipe.am').read_text())
        self.assertEqual(self.standalone(app/'AM-updater').returncode,0)

    def test_a_failed_catalog_install_does_not_end_the_batch(self):
        # mylenovo, 2026-11-22: one recipe failing ended `am -i a b c` for every later app.
        broken=self.recipe_file('x86_64/obsidian').read_text().replace('am_appimage "$0" "$@"','exit 7')
        self.assertIn('exit 7',broken)
        r=self.run_manager_install(amrepo=SOURCE,recipes={'broken':broken},argv=['-i','broken','obsidian'])
        self.assertNotEqual(r.returncode,0)
        self.assertIn(b'"BROKEN" installation failed',r.stderr)
        self.assertTrue((self.app/'AM-updater').exists(),r.stderr)

    def test_reinstall_refuses_before_removing_anything_when_a_module_is_missing(self):
        app=self.install()
        (self.module_dir/'catalog-yaml-policy.am').unlink()
        before=self.snapshot()
        r=self.run_manager_install(amrepo=SOURCE,argv=['reinstall','obsidian'])
        self.assertNotEqual(r.returncode,0)
        self.assertIn(b'Missing catalog-yaml-policy.am',r.stderr)
        self.assertEqual(self.snapshot(),before)
        self.assertTrue((app/'AM-updater').exists())

    def test_batch_reuses_pin_and_documents(self):
        self.install();self.install('x86_64/nvim');self.legacy()
        r=self.manager(['-u','obsidian','nvim','legacy'],source=SOURCE)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn(b'obsidian: unchanged',r.stdout);self.assertIn(b'nvim: unchanged',r.stdout)
        self.assertIn(b'legacy: updated',r.stdout)
        self.assertEqual(len(self.calls()),5) # ref + descriptor + apps + two sources
        self.assertNotIn(b'last seen',r.stderr)

    def test_a_batch_on_old_data_updates_and_warns_once_per_app(self):
        self.install();self.install('x86_64/nvim')
        self.clock=OLD
        r=self.manager(['-u','obsidian','nvim'],source=SOURCE)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn(b'obsidian: unchanged',r.stdout);self.assertIn(b'nvim: unchanged',r.stdout)
        self.assertEqual(r.stderr.count(b'warning: obsidian catalog data last seen 15 days ago'),1,r.stderr)
        self.assertEqual(r.stderr.count(b'warning: nvim catalog data last seen 15 days ago'),1,r.stderr)

    def test_bad_transport_latches_batch_and_preserves_incomplete_install(self):
        obsidian=self.install();self.install('x86_64/nvim');self.legacy()
        (obsidian/'tmp').mkdir();(obsidian/'tmp/keep').write_text('keep')
        old_env=self.env
        self.env=lambda: {**old_env(),'HTTP_STATUS':'503'}
        before={p.name:p.read_bytes() for p in obsidian.iterdir() if p.is_file()}
        r=self.manager(['-u','obsidian','nvim','legacy'],source=SOURCE)
        self.assertNotEqual(r.returncode,0)
        self.assertEqual(len(self.calls()),1)
        self.assertEqual(r.stderr.count(b': refused'),2)
        self.assertIn(b'legacy: updated',r.stdout)
        self.assertEqual((obsidian/'tmp/keep').read_text(),'keep')
        self.assertEqual({p.name:p.read_bytes() for p in obsidian.iterdir() if p.is_file()},before)

    def test_invalid_documents_refuse_no_mutation_no_format1_fallback(self):
        app=self.install();before=self.snapshot()
        for flag in ('BAD_SUFFIX','OVERSIZE'):
            r=self.standalone(app/'AM-updater',env={**self.env(),flag:'1'})
            self.assertNotEqual(r.returncode,0);self.assertEqual(self.snapshot(),before)
            self.assertTrue(all('lookup.tsv' not in c[-1] and '/bodies/' not in c[-1] for c in self.calls()))
        r=self.standalone(app/'AM-updater','--accept-stale','b'*40,'c'*64,'d'*64)
        self.assertNotEqual(r.returncode,0);self.assertEqual(self.calls(),[])
        self.assertEqual(self.snapshot(),before)

    def test_clock_and_option_refusals_precede_install_or_update_mutation(self):
        r=self.run_manager_install(amrepo=SOURCE,flags='--force-latest')
        self.assertNotEqual(r.returncode,0);self.assertFalse(self.app.exists())
        self.assertEqual(self.calls(),[])
        app=self.install();before=self.snapshot()
        for later in ('2026-10-27T15:17:59Z','2026-10-27T15:19:31Z'):
            (self.path/'clock-sequence').write_text(json.dumps([NOW,later]))
            r=self.standalone(app/'AM-updater')
            self.assertNotEqual(r.returncode,0);self.assertEqual(self.snapshot(),before)
        # A clock jump past the 90 s read window between policy passes refuses.
        (self.path/'clock-sequence').write_text(json.dumps([NOW]*5+['2026-11-04T12:00:00Z']))
        r=self.standalone(app/'AM-updater')
        self.assertNotEqual(r.returncode,0);self.assertEqual(self.snapshot(),before)
        (self.path/'clock-sequence').unlink()
        for flag in ('--commit','--accept-stale-release'):
            r=self.manager(['-u','obsidian',flag],source=SOURCE)
            self.assertNotEqual(r.returncode,0);self.assertEqual(self.calls(),[])
            self.assertEqual(self.snapshot(),before)

    def test_later_app_rechecks_clock_and_manager_current_source_overrides_binding(self):
        self.install();self.install('x86_64/nvim')
        (self.path/'clock-sequence').write_text(json.dumps([NOW]*7+[OLD]*20))
        r=self.manager(['-u','obsidian','nvim'],source=SOURCE)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn(b'obsidian: unchanged',r.stdout);self.assertIn(b'nvim: unchanged',r.stdout)
        self.assertNotIn(b'warning: obsidian',r.stderr)
        self.assertIn(b'warning: nvim catalog data last seen 15 days ago',r.stderr)
        (self.path/'clock-sequence').unlink()
        original_env=self.env
        self.env=lambda: {**original_env(),'EXPECTED_REPOSITORY':'another-owner/current-source'}
        source='https://raw.githubusercontent.com/another-owner/current-source/other/branch'
        r=self.manager(['-u','obsidian'],source=source)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertTrue(all('/another-owner/current-source/' in c[-1] for c in self.calls()))

    def test_real_module_sync_retains_runtime_and_standalone_needs_no_checkout(self):
        app=self.install()
        manager=(ROOT/'APP-MANAGER').read_text()
        cleanup=manager[manager.index('_clean_old_modules() {'):manager.index('\n_clean_amcachepath() {')]
        sync=manager[manager.index('_sync_modules() {'):manager.index('\n_sync_amcli() {')]
        harness=self.path/'sync-runtime'
        harness.write_text(cleanup+'\n'+sync+'\n_use_online_downloader() { cp "$SOURCE_MODULES/${1##*/}" "$2"; }\n_use_online_reading_tool_strict() { cat "$SOURCE_MODULES/${1##*/}" 2>/dev/null; }\nAMCLI_ONLINE_CONTENT=$(cat "$MANAGER_SOURCE")\n_sync_modules\n')
        obsolete=self.module_dir/'obsolete.am';obsolete.write_text('old')
        (self.module_dir/'catalog-contract-parser.am').unlink()
        # Stale copies without the AMCLI marker: sync must refresh every shipped
        # module by fetch success, not by a marker some modules never carry.
        shipped=sorted(set(re.findall(r'"([a-z-]+\.am)"',manager)))
        for name in shipped:
            if name!='catalog-contract-parser.am': (self.module_dir/name).write_text('# stale\n')
        source_modules=self.path/'source-modules';shutil.copytree(ROOT/'modules',source_modules)
        (source_modules/'template.am').unlink() # its fetch fails: keep the installed copy
        env={**self.env(),'SOURCE_MODULES':str(source_modules),'MANAGER_SOURCE':str(ROOT/'APP-MANAGER'),
            'MODULES_SOURCE':SOURCE+'/modules','MODULES_PATH':str(self.module_dir),'DIVIDING_LINE':''}
        r=subprocess.run(['/bin/bash',str(harness)],env=env,capture_output=True)
        self.assertEqual(r.returncode,0,r.stderr);self.assertFalse(obsolete.exists())
        self.assertEqual((self.module_dir/'template.am').read_text(),'# stale\n')
        for name in (n for n in shipped if n!='template.am'):
            self.assertEqual((self.module_dir/name).read_bytes(),(ROOT/'modules'/name).read_bytes())
        for tool in ('git','python','python3','jq'):
            self.script(tool,"raise RuntimeError('forbidden runtime dependency')\n")
        r=self.standalone(app/'AM-updater')
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn(b'Update not needed!',r.stdout)

    def test_pinned_network_read_survives_tip_movement_and_same_repo_batch_reuse(self):
        other=copy.deepcopy(self.repositories)
        other['262342594']['collected_at']='2026-10-27T16:00:00Z'  # any change moves the tip
        after=publish_local(self.repo,self.apps,other,expected_parent=self.pin)
        (self.path/'move-to').write_text(after)
        helper=self.module_dir/'catalog-yaml.am'
        r=subprocess.run(['/bin/sh',str(helper),'x86_64/obsidian'],env=self.env(),capture_output=True)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(r.stdout.decode().splitlines()[0],self.pin)
        self.assertEqual(len(self.calls()),4)
        self.assertTrue(all('/'+self.pin+'/' in c[-1] for c in self.calls()[1:]))
        (self.path/'ref').unlink()
        self.install('x86_64/nvim');self.install('x86_64/nvim-nightly')
        r=self.manager(['-u','nvim','nvim-nightly'],source=SOURCE)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(len(self.calls()),4) # ref/apps/one shared repository
        self.assertIn(b'nvim: unchanged',r.stdout)
        self.assertIn(b'nvim-nightly: updated',r.stdout)

    def test_old_data_installs_with_one_warning_and_the_old_consent_flag_is_unsupported(self):
        self.clock=OLD
        r=self.run_manager_install(amrepo=SOURCE)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertTrue((self.app/'version').exists())
        self.assertEqual(r.stderr.count(b'last seen '),1,r.stderr)
        self.assertIn(b'warning: obsidian catalog data last seen 15 days ago',r.stderr)
        self.app.rename(self.path/'first')
        r=self.run_manager_install(amrepo=SOURCE,flags=' '.join(['--accept-stale-release',self.pin,'1','1','1',NOW]))
        self.assertNotEqual(r.returncode,0);self.assertFalse(self.app.exists())

    def test_commit_operands_are_not_apps(self):
        r=self.run_manager_install(amrepo=SOURCE,flags='--commit '+self.pin)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertTrue((self.app/'version').exists())
        self.assertEqual(len(self.calls()),3) # descriptor/map/source at explicit pin
        self.assertFalse((self.root/'opt'/self.pin).exists())

    def test_nightly_refresh_repair_failed_download_and_source_override(self):
        app=self.install('x86_64/nvim-nightly')
        before=len((self.path/'downloads').read_text().splitlines())
        r=self.standalone(app/'AM-updater');self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(len((self.path/'downloads').read_text().splitlines()),before+1)
        app=self.install()
        (app/'AM-VERIFIED').write_text('Checksum failure\n')
        before=len((self.path/'downloads').read_text().splitlines())
        r=self.standalone(app/'AM-updater');self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(len((self.path/'downloads').read_text().splitlines()),before+1)
        (app/'version').write_text('old\n');binary=(app/'obsidian').read_bytes()
        r=self.standalone(app/'AM-updater',env={**self.env(),'DOWNLOAD_FAIL':'1'})
        self.assertNotEqual(r.returncode,0);self.assertEqual((app/'obsidian').read_bytes(),binary)
        self.assertEqual((app/'version').read_text(),'old\n')
        self.assertEqual(self.standalone(app/'AM-updater').returncode,0)
        before=self.snapshot()
        for source in ('file:///tmp/no-fallback','',SOURCE+'?bad'):
            r=self.standalone(app/'AM-updater',env={**self.env(),'AMREPO':source})
            self.assertNotEqual(r.returncode,0);self.assertEqual(self.calls(),[])
            self.assertEqual(self.snapshot(),before)


if __name__=='__main__':
    unittest.main()
