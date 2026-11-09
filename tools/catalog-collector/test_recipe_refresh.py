"""Metadata refresh in disposable installations; no live applications touched."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from installed_recipe import bound_recipe, managed_updater
import recipe_refresh as refresh

ROOT = Path(__file__).resolve().parents[2]


class RecipeRefresh(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/"owner's paths"
        self.installation = self.root/'apps/nvim'
        self.installation.mkdir(parents=True)
        self.pin = subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
        self.body = subprocess.check_output(['git','-C',str(ROOT),'show',self.pin+':programs/x86_64/nvim'])
        self.paths = {name:str(self.root/part) for name,part in
                      (('APPS_DIR','apps'), ('BIN_DIR','bin'), ('DESKTOP_DIR','desktop'))}
        self.modules = self.root/'manager/modules'
        self.old = bound_recipe(self.body, 'https://raw.githubusercontent.com/other-owner/custom.repo/old-ref',
                                self.paths, self.modules).replace(b'CATALOG_FORMAT=3\n',b'CATALOG_FORMAT=2\n')
        (self.installation/'recipe.am').write_bytes(self.old)
        snapshot = self.installation/'.am-installer/nvim'
        snapshot.parent.mkdir()
        snapshot.write_bytes(self.body+b'# previous snapshot\n')
        (self.installation/'AM-updater').write_bytes(managed_updater(self.installation/'recipe.am'))
        (self.installation/'version').write_text('keep-version')
        (self.installation/'nvim').write_text('keep-binary')
        for path in self.installation.rglob('*'):
            if path.is_file():path.chmod(0o750 if path.name=='recipe.am' else 0o640)

    def prepare(self):
        return refresh.prepare(ROOT,self.pin,'x86_64/nvim',self.installation)

    def state(self):
        return {str(p.relative_to(self.installation)):(p.read_bytes(),p.stat().st_mode & 0o777)
                for p in self.installation.rglob('*') if p.is_file()}

    def test_preview_then_refresh_preserves_bindings_owner_modes_and_other_metadata(self):
        before = self.state()
        report, changes, updater = self.prepare()
        self.assertEqual(self.state(), before)
        backup = self.root/'backup'
        old_hashes = [refresh.digest(old) for old,_ in changes.values()]
        refresh.apply(report,changes,updater,backup,*old_hashes)
        self.assertEqual((backup/'recipe.am').read_bytes(),self.old)
        self.assertEqual((backup/'source-recipe').read_bytes(),before['.am-installer/nvim'][0])
        self.assertEqual((self.installation/'.am-installer/nvim').read_bytes(),self.body)
        recipe = (self.installation/'recipe.am').read_bytes()
        self.assertIn(b'CATALOG_FORMAT=3\n',recipe)
        self.assertNotIn(b'CATALOG_FORMAT=2\n',recipe)
        self.assertIn(('other-owner/custom.repo/'+self.pin).encode(),recipe)
        self.assertIn(str(self.modules).encode(),recipe)
        for name,(body,mode) in before.items():
            path = self.installation/name
            self.assertEqual(path.stat().st_mode & 0o777,mode)
            if name not in ('recipe.am','.am-installer/nvim'):
                self.assertEqual(path.read_bytes(),body)
        # Applying twice refuses the existing backup rather than overwriting evidence.
        with self.assertRaises((ValueError,FileExistsError)):
            refresh.apply(report,changes,updater,backup,*old_hashes)

    def test_hash_drift_and_custom_updater_refuse_without_writes(self):
        report, changes, updater = self.prepare()
        backup = self.root/'backup'
        before = self.state()
        with self.assertRaises(ValueError):
            refresh.apply(report,changes,updater,backup,'0'*64,'0'*64)
        self.assertFalse(backup.exists())
        self.assertEqual(self.state(),before)
        hashes = [refresh.digest(old) for old,_ in changes.values()]
        (self.installation/'.am-installer/nvim').write_text('drift')
        with self.assertRaisesRegex(ValueError,'drift'):
            refresh.apply(report,changes,updater,backup,*hashes)
        self.assertFalse(backup.exists())
        (self.installation/'AM-updater').write_text('# custom updater\n')
        with self.assertRaisesRegex(ValueError,'unsupported managed updater'):
            self.prepare()

    def test_managed_updater_handles_literal_paths_and_arguments(self):
        script = self.root/"script's name"
        script.write_text('printf "%s\\n" "$@"\n')
        result = subprocess.run(['sh','-s','--','literal $value'],
                                input=managed_updater(script),capture_output=True,check=True)
        self.assertEqual(result.stdout,b'--am-update\nliteral $value\n')

    def test_symlinks_and_mismatched_identity_refuse(self):
        path = self.installation/'recipe.am'
        path.write_bytes(self.old.replace(b'x86_64/nvim',b'aarch64/nvim'))
        with self.assertRaisesRegex(ValueError,'identity mismatch'):self.prepare()
        path.unlink()
        path.symlink_to(self.installation/'.am-installer/nvim')
        with self.assertRaisesRegex(ValueError,'non-symlink'):self.prepare()


if __name__ == '__main__':
    unittest.main()
