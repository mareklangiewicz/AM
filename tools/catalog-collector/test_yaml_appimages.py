"""Explicit remaining AppImage policies, real saved bytes and inert lifecycle."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import test_yaml_manager_integration as integration
from fixture_manager import ROOT
from fixture_appimages import fixtures
from appimage_policy_source import compile_source, START, END, POLICIES
from yaml_publication import git
from fixture_v3 import publish_local
from reference_policies import APPIMAGES, matches, select_cohort
from fixture_facts import utc
from test_yaml_reader import SCHEMA


class AppImages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved = fixtures()
        cls.repositories = {str(rid):f['repository'] for rid,f in cls.saved.items()}
        cls.apps = {recipe.split('/')[1]:row['repository_id'] for recipe,row in APPIMAGES.items()}
        cls.tmp = tempfile.TemporaryDirectory(prefix='yaml-appimages-')
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

    def policy(self, recipe, facts, tool='mawk', **env):
        return subprocess.run([*(['busybox','awk'] if tool=='busybox' else [tool]),
            '-f',str(ROOT/'modules/catalog-yaml-policy.am')],input=facts,capture_output=True,
            env={**self.env(),'LC_ALL':'C','AM_YAML_NOW':'2026-11-04T12:00:00Z',
                 'AM_YAML_RECIPE':recipe,'AM_YAML_PIN':self.pin,
                 'AM_YAML_REPOSITORY':str(APPIMAGES[recipe]['repository_id']),**env})

    def fact(self, url, *, release='1', asset='1', observed='2026-11-04T12:00:00Z',
             published='2026-11-01T00:00:00Z', name='asset', prerelease=False):
        return ('\t'.join([release,asset,*map(json.dumps,[observed,published,'tag',name,url]),
                            json.dumps(prerelease)])+'\n').encode()

    def test_generated_registry_source_identity_and_enrollment(self):
        source = (ROOT/'modules/catalog-yaml-policy.am').read_text()
        self.assertEqual(START+source.split(START,1)[1].split(END,1)[0]+END,compile_source())
        self.assertEqual(len(APPIMAGES),115)
        for row in json.loads(POLICIES.read_text()):
            recipe = row['recipe']; text=(ROOT/'programs'/recipe).read_text()
            self.assertIn('CATALOG_FORMAT=3\nCATALOG_RECIPE="'+recipe+'"\n',text)
            # Complete declarations supersede historical legacy-body hashes.
            # Their current source/selection contract is covered by declaration
            # compiler checks and the all-installed-recipes lifecycle tests.
            if '# AM-RECIPE-DECLARATION 1' in text.splitlines():
                continue
            before='\n'.join(l for l in text.split('\n') if l!='CATALOG_FORMAT=3' and not l.startswith('CATALOG_RECIPE='))
            self.assertEqual(hashlib.sha256(before.encode()).hexdigest(),row['source_sha256'])
        for recipe in (*APPIMAGES,'x86_64/unknown','x86_64/sqlitebrowser/extra','i686/sqlitebrowser'):
            r = subprocess.run(['awk','-f',str(ROOT/'modules/catalog-yaml-policy.am')],input=b'',
                capture_output=True,env={**self.env(),'AM_YAML_RECIPE':recipe,'AM_YAML_CHECK_RECIPE':'1'})
            self.assertEqual(r.returncode==0,recipe in APPIMAGES,recipe)
            self.assertEqual(r.stdout,b'')
        self.stage()
        r = subprocess.run(['sh',str(self.module_dir/'catalog-yaml.am'),'i686/sqlitebrowser'],
                           env=self.env(),capture_output=True)
        self.assertNotEqual(r.returncode,0);self.assertEqual(self.calls(),[])


    def test_latest_replacement_release_flags_fallthrough_and_selected_freshness(self):
        for recipe in ('x86_64/polymc','aarch64/polymc','i686/supertuxkart',
                       'x86_64/vivaldi-stable','aarch64/vivaldi-snapshot'):
            row=APPIMAGES[recipe];arch,app=recipe.split('/')
            archword='aarch64' if arch=='aarch64' else arch
            channel='snapshot-' if app=='vivaldi-snapshot' else 'stable-' if app=='vivaldi-stable' else ''
            url='https://example.org/releases/download/v1/'+channel+archword+'.AppImage'
            old=self.fact(url,release='1',published='2026-10-01T00:00:00Z')
            preview=self.fact(url.replace('/v1/','/v2/'),release='2',prerelease=True)
            no_asset=self.fact('https://example.org/checksum.txt',release='3',published='2026-11-02T00:00:00Z')
            for tool in ('mawk','gawk','busybox'):
                result=self.policy(recipe,old+preview+no_asset,tool)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual(result.stdout.decode().splitlines()[2],
                    '2' if app=='vivaldi-snapshot' else '1')
                selected=self.fact(url,release='4',published='2026-11-03T00:00:00Z',observed='2026-11-01T12:00:00Z')
                refused=self.policy(recipe,old+selected,tool)
                self.assertNotEqual(refused.returncode,0);self.assertEqual(refused.stdout,b'')
                token=':'.join([self.pin,str(row['repository_id']),'4','1','2026-11-01T12:00:00Z'])
                accepted=self.policy(recipe,old+selected,tool,AM_YAML_ACCEPT=token)
                self.assertEqual(accepted.returncode,0,accepted.stderr)
                self.assertEqual(accepted.stdout.decode().splitlines()[2],'4')
                wrong=self.policy(recipe,old,tool,AM_YAML_REPOSITORY='1')
                self.assertNotEqual(wrong.returncode,0);self.assertEqual(wrong.stdout,b'')

    def test_actual_manager_all_saved_matches_and_generated_updaters(self):
        for recipe,row in APPIMAGES.items():
            with self.subTest(recipe=recipe):
                repository=self.repositories[str(row['repository_id'])]
                self.clock=repository['observed_at']
                try:
                    selection=select_cohort(recipe,repository,self.pin,now=utc(self.clock))
                except ValueError as error:
                    self.assertEqual(str(error),'no_matching_asset')
                    before=self.snapshot();self.stage()
                    result=self.run_manager_install(amrepo=integration.SOURCE,recipe=ROOT/'programs'/recipe,
                        app_name=recipe.split('/')[1])
                    self.assertNotEqual(result.returncode,0);self.assertEqual(self.snapshot(),before)
                    continue
                target=self.root/'opt'/recipe.split('/')[1]
                if target.exists(): shutil.rmtree(target)
                app=self.install(recipe)
                self.assertEqual((app/'version').read_text().strip(),selection['asset']['url'])
                self.assertIn('CATALOG_FORMAT=3',(app/'recipe.am').read_text())
                result=self.standalone(app/'AM-updater')
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertIn(b'Update not needed!',result.stdout)

    def test_reassignment_and_stale_refuse_before_mutation(self):
        self.clock=self.repositories['19416551']['observed_at']
        app=self.install('x86_64/sqlitebrowser');before=self.snapshot()
        self.clock='2026-11-04T12:00:00Z'
        result=self.standalone(app/'AM-updater')
        self.assertNotEqual(result.returncode,0);self.assertEqual(self.snapshot(),before)
        apps=dict(self.apps,sqlitebrowser=next(r for r in self.saved if r!=19416551))
        pin=publish_local(self.repo,apps,self.repositories,schema=SCHEMA,max_file_bytes=2097152,expected_parent=self.pin)
        result=self.standalone(app/'AM-updater','--commit',pin)
        self.assertNotEqual(result.returncode,0);self.assertEqual(self.snapshot(),before)
        self.assertIn(b'appimage_repository_mismatch',result.stderr)


if __name__ == '__main__': unittest.main()


class AdversarialPolicies(unittest.TestCase):
    """Direct policy checks need no saved catalog, installer or Git fixture."""
    pin = 'b'*40
    policy = AppImages.policy
    fact = AppImages.fact

    def env(self):
        return dict(os.environ)

    def test_adversarial_url_rules_on_three_awk_tools(self):
        # Independently authored asset URLs exercise maintained eligibility and
        # ordering against the reference rules and all three supported awk tools.
        components = ['x86_64','aarch64','arm64','i686','armv7l','amd64','x86.64',
            'CRITERIA1D-x86_64','stable-x86_64','snapshot-x86_64','snapshot-aarch64',
            'glfw-x86_64','tip-x86_64','beta-x86_64','candidate-x86_64','DEV-x86_64',
            'dev-x86_64','basilisk','sheepshaver','circles','heat','geo','pro','clang','gcc',
            'staging','devel','proton','i386|i686|aarch64|arm64|armv7l']
        urls = ['https://example.org/releases/download/'+tag+'/'+part+suffix
                for tag in ('v1','1.2','v1-rc2','continuous','Continuous','nightly')
                for part in components for suffix in ('.AppImage','.appimage','.AppImage.zsync')]
        # Batch candidate tests per policy in one awk process. A separate unique
        # release with ascending publication picks the last eligible URL.
        for recipe,row in APPIMAGES.items():
            if '# AM-RECIPE-DECLARATION 1' in (ROOT/'programs'/recipe).read_text().splitlines():
                # Complete declarations have their own compiler and lifecycle checks.
                continue
            eligible=[]
            for url in urls:
                expected=matches(recipe,{'prerelease':False},{'url':url})
                if expected: eligible.append(url)
            facts=b''.join(self.fact(u,asset=str(i),name=f'{i:05d}') for i,u in enumerate(urls,1))
            # The first eligible by numeric-name ordering, independent of URL.
            wanted=eligible[0] if eligible else None
            for tool in ('mawk','gawk','busybox'):
                result=self.policy(recipe,facts,tool)
                self.assertEqual(result.returncode==0,wanted is not None,(recipe,tool,result.stderr))
                if wanted: self.assertEqual(result.stdout.decode().splitlines()[-1],wanted)
                else: self.assertEqual(result.stdout,b'')
