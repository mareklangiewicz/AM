"""Whole-table AppImage checks over the live recipes: every policy row, through the real manager.

Slow, and it follows whatever recipes the tree holds. Run before an upstream
merge and on demand: `-p 'tree_*.py'`.
"""
import hashlib
import json
import shutil
import subprocess
import unittest

import test_yaml_manager_integration as integration
from fixture_manager import ROOT
from appimage_policy_source import compile_source, START, END, POLICIES
from reference_policies import APPIMAGES, select_cohort
from fixture_facts import utc
from fixture_v3 import expanded
import test_yaml_appimages


class TreeAppImages(test_yaml_appimages.AppImagesCase):
    live = True

    def test_generated_registry_source_identity_and_enrollment(self):
        source = (ROOT/'modules/catalog-yaml-policy.am').read_text()
        self.assertEqual(START+source.split(START,1)[1].split(END,1)[0]+END,compile_source())
        self.assertTrue(APPIMAGES)
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

    def test_actual_manager_all_saved_matches_and_generated_updaters(self):
        for recipe,row in APPIMAGES.items():
            with self.subTest(recipe=recipe):
                repository=self.repositories[str(row['repository_id'])]
                self.clock=repository['observed_at']
                try:
                    selection=select_cohort(recipe,expanded(repository),self.pin,now=utc(self.clock))
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


if __name__=='__main__':unittest.main()
