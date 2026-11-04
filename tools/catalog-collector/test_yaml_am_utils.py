"""Explicit executable policies and disposable existing-install transition."""
import copy
import os
import shutil
from pathlib import Path
import subprocess
import tempfile
import unittest

import test_yaml_manager_integration as integration
from test_yaml_cohort_shell import ROOT
from am_utils_cohort import RID, fixture
from yaml_publication import git, publish_local, candidate_tree
from yaml_recipe_cohort import AM_UTILS, matches, select_cohort
from attempt_adapter import utc
from experiment import SCHEMA


class AMUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw, report, cls.repository, cls.tree = fixture()
        cls.repositories = {str(RID):cls.repository}
        cls.apps = {r.split('/')[1]:RID for r in AM_UTILS}
        cls.tmp = tempfile.TemporaryDirectory(prefix='yaml-am-utils-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.repo = Path(cls.tmp.name)/'git'; cls.repo.mkdir()
        git(cls.repo,'init','--bare')
        cls.pin = publish_local(cls.repo,cls.apps,cls.repositories,schema=SCHEMA,
                               max_file_bytes=2097152,expected_parent=None)

    script = integration.YAMLManager.script
    env = integration.YAMLManager.env
    stage = integration.YAMLManager.stage
    calls = integration.YAMLManager.calls
    run_manager_install = integration.YAMLManager.run_manager_install
    snapshot = integration.YAMLManager.snapshot
    install = integration.YAMLManager.install
    standalone = integration.YAMLManager.standalone
    manager = integration.YAMLManager.manager

    def setUp(self):
        integration.YAMLManager.setUp(self)
        self.clock = self.repository['observed_at']

    def policy(self,recipe,repository,tool):
        tree = candidate_tree(self.apps,{str(RID):repository},schema=SCHEMA,max_file_bytes=2097152)
        path = self.path/'document.yaml';path.write_bytes(tree[f'repositories/{RID}.yaml'])
        facts = subprocess.run(['sh',str(ROOT/'modules/catalog-yaml-reader.am'),'asset_facts',str(path)],
                               capture_output=True,check=True).stdout
        return subprocess.run([*(['busybox','awk'] if tool=='busybox' else [tool]),
            '-f',str(ROOT/'modules/catalog-yaml-policy.am')],input=facts,capture_output=True,
            env={**self.env(),'AM_YAML_NOW':repository['observed_at'],'AM_YAML_RECIPE':recipe,
                 'AM_YAML_PIN':self.pin,'AM_YAML_REPOSITORY':str(RID)})

    def test_registry_and_unknown_refusal_before_http(self):
        for recipe in (*AM_UTILS,'i686/ls','x86_64/not-enrolled','x86_64/ls/extra','x86_64/LS'):
            r = subprocess.run(['awk','-f',str(ROOT/'modules/catalog-yaml-policy.am')],input=b'',
                capture_output=True,env={**self.env(),'AM_YAML_RECIPE':recipe,'AM_YAML_CHECK_RECIPE':'1'})
            self.assertEqual(r.returncode==0,recipe in AM_UTILS,recipe)
            self.assertEqual(r.stdout,b'')
        for recipe in ('i686/ls','x86_64/not-enrolled'):
            r = subprocess.run(['sh',str(self.module_dir/'catalog-yaml.am'),recipe],env=self.env(),capture_output=True)
            self.assertNotEqual(r.returncode,0);self.assertEqual(self.calls(),[])
        self.assertEqual(len(AM_UTILS),356)

    def test_actual_install_standalone_and_shared_repository_batch(self):
        for recipe in ('x86_64/7z','aarch64/7z','x86_64/c++filt','aarch64/c++filt','x86_64/ld.bfd'):
            with self.subTest(recipe=recipe):
                # Start clean per architecture: installed app names are shared.
                target = self.root/'opt'/recipe.split('/')[1]
                if target.exists():
                    shutil.rmtree(target)
                app = self.install(recipe)
                selected = select_cohort(recipe,self.repository,self.pin,now=utc(self.clock))
                self.assertEqual((app/'version').read_text().strip(),selected['asset']['url'])
                self.assertFalse((app/'icons').exists())
                self.assertTrue((self.root/'usr/local/bin'/app.name).samefile(app/app.name))
                r = self.standalone(app/'AM-updater');self.assertEqual(r.returncode,0,r.stderr)
                self.assertIn(b'Update not needed!',r.stdout)
        r = self.manager(['-u','7z','c++filt','ld.bfd'],source=integration.SOURCE)
        self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(len(self.calls()),3)
        for app in ('7z','c++filt','ld.bfd'):
            self.assertIn((app+': unchanged').encode(),r.stdout)

    def test_encoding_literal_dot_arch_date_and_ties_on_three_awk(self):
        repository = copy.deepcopy(self.repository)
        release = copy.deepcopy(next(iter(repository['releases'].values())))
        asset = copy.deepcopy(next(iter(release['assets'].values())))
        release.update(tag='arbitrary-tag',published_at='2026-10-28T00:00:00Z')
        prefix = 'https://example.org/download/'
        release['assets'] = {str(i):dict(asset,name=name,url=prefix+suffix) for i,name,suffix in (
            (1,'misleading','x86_64-20261028/ldXbfd_1-x86_64-static'),
            (2,'b','x86_64-20261028/ld.bfd_2-x86_64-static'),
            (3,'a','x86_64-20261028/ld.bfd_1-x86_64-static'),
            (4,'z','aarch64-20261028/ld.bfd_1-aarch64-static'),
            (5,'c','x86_64-20261028/c%2B%2Bfilt_1-x86_64-static'))}
        repository['releases'] = {'9007199254740993':release}
        for tool in ('mawk','gawk','busybox'):
            r = self.policy('x86_64/ld.bfd',repository,tool)
            self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(r.stdout.decode().splitlines()[3],'3')
            r = self.policy('x86_64/c++filt',repository,tool)
            self.assertEqual(r.returncode,0,r.stderr);self.assertIn(b'c%2B%2Bfilt',r.stdout)
        for suffix in ('x86_64-2026102/c%2B%2Bfilt_1-x86_64-static',
                       'continuous-x86_64/c%2B%2Bfilt_1-x86_64-static',
                       'x86_64-20261028/c++filt_1-x86_64-static'):
            self.assertFalse(matches('x86_64/c++filt',release,dict(asset,url=prefix+suffix)))
        wrong = copy.deepcopy(self.repository);wrong['repository_id']=1
        with self.assertRaisesRegex(ValueError,'am_utils_repository_mismatch'):
            select_cohort('x86_64/7z',wrong,self.pin,now=utc(self.clock))

    def test_existing_recipe_transition_and_exact_rollback_rehearsal(self):
        # Explicit disposable rehearsal, not an automatic production migrator.
        app = self.install('x86_64/7z');recipe = app/'recipe.am';candidate = recipe.read_bytes()
        old = b'\n'.join(line for line in candidate.split(b'\n')
                         if line != b'CATALOG_FORMAT=2' and not line.startswith(b'CATALOG_RECIPE='))
        recipe.write_bytes(old);before = self.snapshot()
        binary = (app/'7z').read_bytes();version = (app/'version').read_bytes()
        backup = self.path/'recipe.backup';backup.write_bytes(old)
        staged = app/'recipe.am.staged';staged.write_bytes(candidate)
        helper = self.module_dir/'catalog-yaml.am'
        self.stage()
        r = subprocess.run(['sh',str(helper),'x86_64/7z'],env={**self.env(),'CLOCK':'2026-11-04T12:00:00Z'},capture_output=True)
        self.assertNotEqual(r.returncode,0);self.assertEqual(recipe.read_bytes(),old)
        staged.unlink();self.assertEqual(self.snapshot(),before)
        self.stage()
        r = subprocess.run(['sh',str(helper),'x86_64/7z'],env=self.env(),capture_output=True)
        self.assertEqual(r.returncode,0,r.stderr)
        staged.write_bytes(candidate);os.replace(staged,recipe)
        r = self.standalone(app/'AM-updater');self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual((app/'7z').read_bytes(),binary);self.assertEqual((app/'version').read_bytes(),version)
        staged.write_bytes(backup.read_bytes());os.replace(staged,recipe)
        self.assertEqual(self.snapshot(),before)

    def test_stale_exact_waiver_and_missing_runtime_before_mutation(self):
        app = self.install('x86_64/7z');before = self.snapshot()
        r = self.standalone(app/'AM-updater',env={**self.env(),'CLOCK':'2026-11-04T12:00:00Z'})
        self.assertNotEqual(r.returncode,0);self.assertEqual(self.snapshot(),before)
        selected = select_cohort('x86_64/7z',self.repository,self.pin,now=utc(self.clock))
        args = ['--commit',self.pin,'--accept-stale-release',self.pin,str(RID),
                selected['release_id'],selected['asset_id'],selected['observed_at']]
        r = self.standalone(app/'AM-updater',*args,env={**self.env(),'CLOCK':'2026-11-04T12:00:00Z'})
        self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(self.snapshot(),before)
        (self.module_dir/'catalog-yaml-policy.am').unlink();before = self.snapshot()
        r = self.standalone(app/'AM-updater');self.assertNotEqual(r.returncode,0)
        self.assertEqual(self.snapshot(),before)


if __name__ == '__main__':
    unittest.main()
