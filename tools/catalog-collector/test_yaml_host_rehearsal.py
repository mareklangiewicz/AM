"""Sunshine policy and inert end-to-end source/module/recipe/binary recovery."""
import copy
from datetime import timedelta
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from sunshine_fixture import observation, RID
from attempt_adapter import utc
from experiment import SCHEMA
import test_yaml_manager_integration as integration
import yaml_installed_migration as migration
from yaml_cutover_package import bound_recipe
from yaml_enrollment import enroll,shared_recipes
from yaml_publication import git,publish_local,candidate_tree
from publication import publish_tree
from storage import apply,canonical
from yaml_recipe_cohort import select_cohort
from recipe_cohort import legacy

ROOT=Path(__file__).resolve().parents[2]
LEGACY=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','83af4473f']).decode().strip()


class HostRehearsal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source,cls.raw,cls.report,cls.repository=observation()
        cls.tmp=tempfile.TemporaryDirectory(prefix='yaml-host-rehearsal-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.repo=Path(cls.tmp.name)/'catalog.git';cls.repo.mkdir()
        git(cls.repo,'init','--bare')
        cls.source_pin=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip()
        raw_manifest=canonical(dict(schema=2,sources=[cls.source]))
        r=cls.report
        attempt=dict(request_id=cls.source['request_id'],descriptor={k:r['descriptor'][k] for k in ('url','api_version','accept')},repository_id=RID,
            request_started_at=r['started_at'],response_completed_at=r['completed_at'],
            attempt_finished_at=r['completed_at'],status=200,headers=r['public_headers'],
            body=cls.raw,condition={},outcome='response')
        tree,_=apply(None,raw_manifest,[attempt],workflow_identity=1,generated_at=r['completed_at'],
                     revision=cls.source_pin,run={'id':'1','attempt':'1'})
        cls.format1=publish_tree(cls.repo,tree,None)
        git(cls.repo,'update-ref','refs/heads/release-catalog',cls.format1)
        git(cls.repo,'update-ref','-d','refs/heads/catalog',cls.format1)
        cls.pin=publish_local(cls.repo,{'sunshine':RID},{str(RID):cls.repository},
                             schema=SCHEMA,max_file_bytes=2097152,expected_parent=None)
        git(cls.repo,'update-ref','refs/heads/release-catalog-yaml-v2',cls.pin)

    def setUp(self):
        integration.YAMLManager.setUp(self)
        self.clock=(utc(self.report['completed_at']).replace(microsecond=0)+timedelta(seconds=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        self.source_url='https://raw.githubusercontent.com/selected-owner/selected.repo/'+self.source_pin
        self.script('curl','''import json,os,pathlib,re,subprocess,sys
p=pathlib.Path(os.environ['FIXTURE']);a=sys.argv[1:];url=a[-1]
with (p/'calls').open('a') as f:f.write(json.dumps(a)+'\\n')
def git(*args):return subprocess.check_output(['/usr/bin/git','-C',os.environ['REMOTE'],*args])
m=re.fullmatch(r'https://api.github.com/repos/selected-owner/selected.repo/commits/heads/(release-catalog(?:-yaml-v2)?)',url)
if m:raw=git('rev-parse','refs/heads/'+m[1])
else:
 m=re.fullmatch(r'https://raw.githubusercontent.com/selected-owner/selected.repo/([0-9a-f]{40})/(lookup\\.tsv|bodies/[0-9a-f]{64}\\.json|apps\\.yaml|repositories/[0-9]+\\.yaml)',url)
 assert m,url
 raw=git('show',m[1]+':'+m[2])
pathlib.Path(a[a.index('--output')+1]).write_bytes(raw)
print('200',end='')
''')

    def test_saved_policy_matches_legacy_and_three_awk(self):
        selected=select_cohort('x86_64/sunshine',self.repository,self.pin,now=utc(self.clock))
        self.assertEqual(legacy('x86_64/sunshine',self.raw),selected['asset']['url'])
        self.assertEqual(len(self.repository['releases']),30)
        tree=candidate_tree({'sunshine':RID},{str(RID):self.repository},schema=SCHEMA,max_file_bytes=2097152)
        file=self.path/'repository.yaml';file.write_bytes(tree[f'repositories/{RID}.yaml'])
        facts=subprocess.check_output(['sh',str(ROOT/'modules/catalog-yaml-reader.am'),'asset_facts',str(file)])
        for command in (['mawk'],['gawk'],['busybox','awk']):
            result=subprocess.run([*command,'-f',str(ROOT/'modules/catalog-yaml-policy.am')],input=facts,
                env={**self.env(),'AM_YAML_RECIPE':'x86_64/sunshine','AM_YAML_REPOSITORY':str(RID),
                     'AM_YAML_NOW':self.clock,'AM_YAML_PIN':self.pin},capture_output=True,check=True)
            self.assertEqual(result.stdout.decode().splitlines(),[self.pin,str(RID),selected['release_id'],
                selected['asset_id'],selected['observed_at'],selected['asset']['url']])
        raw=(ROOT/'docs/track/release-catalog/design/yaml-manifest.json').read_bytes()
        apps,identities,report=enroll(raw,1,shared_recipes(ROOT),source_revision=self.source_pin)
        self.assertEqual((len(identities),len(report['recipes']),len(report['excluded'])),(50,476,986))
        self.assertEqual(apps['sunshine'],RID)

    def test_module_delivery_migrate_update_binary_recovery_and_restored_format1(self):
        app=self.root/'opt/sunshine';app.mkdir()
        recipe=app/'recipe.am';updater=app/'AM-updater'
        paths=dict(APPS_DIR=str(self.root/'opt')+'/',BIN_DIR=str(self.root/'usr/local/bin'),
                   DESKTOP_DIR=str(self.root/'usr/local/share/applications'))
        for path in self.module_dir.iterdir():path.unlink()
        manager=self.root/'opt/am/APP-MANAGER'
        manager.write_bytes(migration.blob(ROOT,LEGACY,'APP-MANAGER'));manager.chmod(0o755)
        before_modules={}
        for name in ('catalog.am','appimage.am'):
            path=self.module_dir/name;path.write_bytes(migration.blob(ROOT,LEGACY,'modules/'+name))
            before_modules[name]=(path.read_bytes(),migration.regular(path))
        before_manager=(manager.read_bytes(),migration.regular(manager))
        old=bound_recipe(migration.blob(ROOT,LEGACY,'programs/x86_64/sunshine'),
                         integration.SOURCE,paths,self.module_dir)
        recipe.write_bytes(old);recipe.chmod(0o750)
        updater.write_bytes(migration.managed_updater(recipe));updater.chmod(0o755)
        selected=select_cohort('x86_64/sunshine',self.repository,self.pin,now=utc(self.clock))
        (app/'sunshine').write_bytes(b'old inert Sunshine binary');(app/'sunshine').chmod(0o755)
        (app/'version').write_text(selected['asset']['url']+'\n')
        env=self.env();env.pop('AMREPO')
        r=self.standalone(updater,'--commit',self.format1,env=env)
        self.assertEqual(r.returncode,0,r.stderr);self.assertIn(b'Update not needed',r.stdout)
        # Exact guarded module/manager delivery, only inside this disposable root.
        migration.check(manager,before_manager[1])
        migration.atomic(manager,migration.blob(ROOT,self.source_pin,'APP-MANAGER'),before_manager[1])
        for name in migration.RUNTIME:
            path=self.module_dir/name
            if name in before_modules:migration.check(path,before_modules[name][1])
            metadata=before_modules[name][1] if name in before_modules else dict(
                uid=recipe.stat().st_uid,gid=recipe.stat().st_gid,mode=0o644)
            migration.atomic(path,migration.blob(ROOT,self.source_pin,'modules/'+name),metadata)
        replacement=self.path/'replacement'
        replacement.write_bytes(bound_recipe(migration.blob(ROOT,self.source_pin,'programs/x86_64/sunshine'),
                                            self.source_url,paths,self.module_dir))
        result=subprocess.run(['sh',str(self.module_dir/'catalog-yaml.am'),'x86_64/sunshine','--commit',self.pin],
                              env={**self.env(),'AMREPO':self.source_url},check=True,capture_output=True)
        plan=migration.prepare(ROOT,self.source_pin,self.source_url,app,'x86_64/sunshine',replacement,
            manager,self.module_dir,self.pin,result.stdout.decode(),migration.digest(old))
        tx=self.path/'transaction';tx.mkdir(mode=0o700)
        self.assertEqual(migration.transact(plan,tx,env=self.env()),'applied')
        backups={name:((app/name).read_bytes(),migration.regular(app/name)) for name in ('sunshine','version')}
        r=self.standalone(updater,'--commit',self.pin,env=env)
        self.assertEqual(r.returncode,0,r.stderr);self.assertIn(b'Update not needed',r.stdout)
        # Explicit synthetic next-release facts drive a real inert update. They
        # are test data, never represented as an upstream observation/capacity run.
        changed=copy.deepcopy(self.repository)
        release=copy.deepcopy(next(iter(changed['releases'].values())))
        release_id=str(max(map(int,changed['releases']))+1)
        release.update(published_at=max(r['published_at'] for r in changed['releases'].values()))
        asset=copy.deepcopy(next(iter(release['assets'].values())))
        asset.update(name='synthetic-next.AppImage',url='https://example.org/synthetic-next.AppImage')
        release['assets']={'1':asset};changed['releases'][release_id]=release
        next_pin=publish_local(self.repo,{'sunshine':RID},{str(RID):changed},schema=SCHEMA,
                               max_file_bytes=2097152,expected_parent=self.pin)
        r=self.manager(['-u','sunshine','--commit',next_pin],source=self.source_url)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual((app/'version').read_text().strip(),asset['url'])
        self.assertNotEqual((app/'sunshine').read_bytes(),backups['sunshine'][0])
        with self.assertRaisesRegex(ValueError,'drift'):
            migration.transact(plan,tx,rollback=True,env=self.env())
        post={name:migration.regular(app/name) for name in backups}
        # An independently retained, exact artifact/version pair restores the
        # guards. These two restores are separate renames, not pair-atomic.
        for name,(data,metadata) in backups.items():
            migration.check(app/name,post[name]);migration.atomic(app/name,data,metadata)
        self.assertEqual(migration.transact(plan,tx,rollback=True,env=self.env()),'rolled-back')
        self.assertEqual(recipe.read_bytes(),old)
        # Restore prior manager/modules and execute actual format-1 helper/updater.
        delivered={p:migration.regular(p) for p in (manager,*self.module_dir.iterdir())}
        migration.check(manager,delivered[manager]);migration.atomic(manager,*before_manager)
        for name,(data,metadata) in before_modules.items():
            path=self.module_dir/name;migration.check(path,delivered[path]);migration.atomic(path,data,metadata)
        for name in set(migration.RUNTIME)-set(before_modules):
            path=self.module_dir/name;migration.check(path,delivered[path]);path.unlink()
        r=self.standalone(updater,'--commit',self.format1,env=env)
        self.assertEqual(r.returncode,0,r.stderr);self.assertIn(b'Update not needed',r.stdout)
        for name,(data,metadata) in backups.items():
            self.assertEqual((app/name).read_bytes(),data);migration.check(app/name,metadata)


for name in ('script','env','stage','calls','standalone','manager'):
    setattr(HostRehearsal,name,getattr(integration.YAMLManager,name))

if __name__=='__main__':unittest.main()
