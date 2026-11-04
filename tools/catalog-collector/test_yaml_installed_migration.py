"""Disposable exact-source transaction tests, including interrupted rename recovery."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest.mock import patch

import yaml_installed_migration as migration
import test_yaml_am_utils as am_utils
import test_yaml_manager_integration as integration
from test_yaml_cohort_shell import ROOT


class InstalledMigration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        am_utils.AMUtils.setUpClass.__func__(cls)

    def setUp(self):
        integration.YAMLManager.setUp(self)
        self.clock = self.repository['observed_at']
        for name in migration.RUNTIME:
            shutil.copyfile(ROOT/'modules'/name, self.module_dir/name)
        self.app = self.install('x86_64/7z')
        self.target = self.app/'recipe.am'
        self.source_pin = subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip()
        self.source_url = 'https://raw.githubusercontent.com/selected-owner/selected.repo/'+self.source_pin
        self.replacement = self.path/'replacement'
        self.replacement.write_bytes(self.target.read_bytes().replace(integration.SOURCE.encode(), self.source_url.encode()))
        old = self.target.read_bytes().replace(b'CATALOG_FORMAT=2\n',b'').replace(b'CATALOG_RECIPE="x86_64/7z"\n',b'')
        old = old.replace(b'CATALOG_YAML_HELPER=',b'CATALOG_HELPER=').replace(b'/catalog-yaml.am"',b'/catalog.am"')
        self.target.write_bytes(old)
        self.target.chmod(0o640)
        self.manager_file = self.path/'manager'
        shutil.copyfile(ROOT/'APP-MANAGER', self.manager_file)
        self.stage()
        self.selection = subprocess.run(['sh',str(self.module_dir/'catalog-yaml.am'),'x86_64/7z','--commit',self.pin],
            env=self.env(),check=True,capture_output=True).stdout.decode()
        self.plan = migration.prepare(ROOT,self.source_pin,self.source_url,self.app,'x86_64/7z',
            self.replacement,self.manager_file,self.module_dir,self.pin,self.selection,migration.digest(old))
        self.tx = self.path/'transaction'; self.tx.mkdir(mode=0o700)
        self.before = self.target.read_bytes()
        self.binary = (self.app/'7z').read_bytes()
        self.version = (self.app/'version').read_bytes()

    def apply(self, **kwargs):
        return migration.transact(self.plan,self.tx,env=self.env(),**kwargs)

    def test_apply_idempotence_and_exact_metadata_rollback(self):
        self.assertEqual(self.apply(),'applied')
        self.assertEqual(self.target.read_bytes(),self.replacement.read_bytes())
        self.assertEqual(migration.regular(self.target),self.plan['new'])
        self.assertEqual(self.apply(),'unchanged')
        self.assertEqual(self.apply(rollback=True),'rolled-back')
        self.assertEqual(self.target.read_bytes(),self.before)
        self.assertEqual(migration.regular(self.target),self.plan['old'])
        self.assertEqual(self.apply(rollback=True),'unchanged')
        with self.assertRaisesRegex(ValueError,'cannot reapply'):
            self.apply()
        self.assertEqual((self.app/'7z').read_bytes(),self.binary)
        self.assertEqual((self.app/'version').read_bytes(),self.version)
        self.assertEqual((self.tx/'recipe.before').read_bytes(),self.before)

    def test_stale_refusal_and_exact_selected_consent(self):
        self.clock = '2026-11-04T12:00:00Z'
        with self.assertRaises(subprocess.CalledProcessError):
            self.apply()
        self.assertEqual(self.target.read_bytes(),self.before)
        self.assertEqual([p.name for p in self.tx.iterdir()],['lock'])
        self.assertEqual(self.apply(accept=True),'applied')

    def test_selected_identity_mismatch_refuses(self):
        self.plan['selection'] = self.selection.replace('https://','https://different.',1)
        with self.assertRaisesRegex(ValueError,'selected record changed'):
            self.apply()
        self.assertEqual(self.target.read_bytes(),self.before)

    def test_every_guard_drift_and_recipe_drift_refuse(self):
        for path in self.plan['guards']:
            with self.subTest(path=path):
                p = Path(path); data=p.read_bytes(); p.write_bytes(data+b'\n')
                with self.assertRaisesRegex(ValueError,'drift'):
                    self.apply()
                self.assertEqual(self.target.read_bytes(),self.before)
                p.write_bytes(data)
        self.target.write_bytes(self.before+b'\n')
        with self.assertRaisesRegex(ValueError,'drift'):
            self.apply()

    def test_preflight_drift_is_rechecked(self):
        real = migration.preflight
        def drifting(*args):
            real(*args)
            self.target.write_bytes(self.before+b'changed')
        with patch.object(migration,'preflight',drifting):
            with self.assertRaisesRegex(ValueError,'drift'):
                self.apply()
        self.assertEqual(self.target.read_bytes(),self.before+b'changed')
        self.assertFalse((self.tx/'intent.json').exists())

    def test_all_durable_write_boundaries_resume(self):
        # Inject loss of process after each durable write (including recipe rename).
        real = migration.atomic
        for boundary in ('recipe.before','intent.json','recipe.am','receipt.json'):
            with self.subTest(boundary=boundary):
                self.target.write_bytes(self.before)
                for p in self.tx.iterdir(): p.unlink()
                fired = False
                def interrupted(path,*args,**kwargs):
                    nonlocal fired
                    real(path,*args,**kwargs)
                    if Path(path).name == boundary and not fired:
                        fired=True
                        raise InterruptedError('simulated crash')
                with patch.object(migration,'atomic',interrupted):
                    with self.assertRaises(InterruptedError): self.apply()
                self.assertTrue(fired)
                self.apply()
                self.assertEqual(self.target.read_bytes(),self.replacement.read_bytes())
                self.assertEqual(json.loads((self.tx/'receipt.json').read_text())['result'],'applied')

    def test_interrupted_rollback_cannot_reapply(self):
        self.apply()
        real = migration.atomic
        def interrupted(path,*args,**kwargs):
            real(path,*args,**kwargs)
            if Path(path)==self.target: raise InterruptedError('simulated crash')
        with patch.object(migration,'atomic',interrupted):
            with self.assertRaises(InterruptedError): self.apply(rollback=True)
        with self.assertRaisesRegex(ValueError,'rollback already started'):
            self.apply()
        self.assertEqual(self.apply(rollback=True),'unchanged')
        self.assertEqual(self.target.read_bytes(),self.before)

    def test_applied_recipe_reversion_without_rollback_intent_refuses(self):
        self.apply()
        self.target.write_bytes(self.before)
        for rollback in (False,True):
            with self.assertRaisesRegex(ValueError,'reverted without rollback intent'):
                self.apply(rollback=rollback)
        self.assertFalse((self.tx/'rollback.json').exists())

    def test_backup_and_post_update_drift_refuse_rollback(self):
        self.apply()
        (self.tx/'recipe.before').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'backup drift'): self.apply(rollback=True)
        (self.tx/'recipe.before').write_bytes(self.before)
        (self.app/'version').write_bytes(b'updated binary version')
        with self.assertRaisesRegex(ValueError,'drift'): self.apply(rollback=True)
        self.assertEqual(self.target.read_bytes(),self.replacement.read_bytes())

    def test_plan_refuses_unreviewed_recipe_or_symlink_source(self):
        args = [ROOT,self.source_pin,self.source_url,self.app,'x86_64/7z',
                self.replacement,self.manager_file,self.module_dir,self.pin,
                self.selection,'0'*64]
        with self.assertRaisesRegex(ValueError,'reviewed legacy hash'):
            migration.prepare(*args)
        args[-1] = migration.digest(self.before)
        link = self.path/'linked-source'; link.symlink_to(ROOT)
        args[0] = link
        with self.assertRaisesRegex(ValueError,'symlink directory'):
            migration.prepare(*args)
        args[0] = ROOT
        link = self.path/'linked-replacement'; link.symlink_to(self.replacement)
        args[5] = link
        with self.assertRaisesRegex(ValueError,'symlink'):
            migration.prepare(*args)

    def test_lock_symlink_and_metadata_refusals(self):
        link = self.app/'link';link.symlink_to(self.target)
        with self.assertRaisesRegex(ValueError,'symlink'): migration.regular(link)
        hard = self.app/'hard';os.link(self.target,hard)
        with self.assertRaisesRegex(ValueError,'hard-linked'): self.apply()
        hard.unlink()
        with migration.locked(self.tx):
            with self.assertRaises(BlockingIOError): self.apply()
        self.tx.chmod(0o755)
        with self.assertRaisesRegex(ValueError,'private'): self.apply()


for name in ('script','env','stage','calls','run_manager_install','snapshot','install'):
    setattr(InstalledMigration,name,getattr(integration.YAMLManager,name))

if __name__ == '__main__': unittest.main()
