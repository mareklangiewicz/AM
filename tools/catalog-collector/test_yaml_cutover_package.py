"""Read-only inventory, deterministic binding and pinned-package integrity."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml_cutover_package as cutover

ROOT=Path(__file__).resolve().parents[2]
LEGACY=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','83af4473f']).decode().strip()


class Cutover(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='yaml-package-')
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)
        self.apps=self.path/'apps';self.apps.mkdir()
        self.modules=self.path/'modules';self.modules.mkdir()
        self.manager=self.path/'manager';self.manager.write_bytes(b'manager')
        (self.modules/'catalog.am').write_bytes(b'legacy module')
        self.pin=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip()
        self.source='https://raw.githubusercontent.com/mareklangiewicz/AM/main-marek'
        self.paths=dict(APPS_DIR=str(self.apps)+'/',BIN_DIR=str(self.path/'bin'),
                        DESKTOP_DIR=str(self.path/'desktop'))
        for app in ('obsidian','sunshine'):
            installed=self.apps/app;installed.mkdir()
            body=cutover.blob(ROOT,LEGACY,'programs/x86_64/'+app)
            recipe=installed/'recipe.am'
            recipe.write_bytes(cutover.bound_recipe(body,self.source,self.paths,self.modules))
            (installed/'AM-updater').write_text("#!/bin/sh\n# AM-CATALOG-UPDATER 1\nexec sh '"+str(recipe)+"' --am-update \"$@\"\n")
            (installed/app).write_bytes(b'unchanged binary')
            (installed/'version').write_bytes(b'https://example.org/unchanged\n')
        legacy=self.apps/'legacy';legacy.mkdir()
        (legacy/'AM-updater').write_text('#!/bin/sh\necho never execute\n')
        (legacy/'legacy').write_bytes(b'legacy binary')
        (legacy/'version').write_bytes(b'1')
        self.config=self.path/'appman-config'

    def inventory(self):
        return cutover.inventory([self.apps],self.manager,self.modules,'x86_64',self.config,self.path/'data')

    def build(self,observed=None,name='package'):
        output=self.path/name
        report=cutover.package(ROOT,self.pin,LEGACY,'mareklangiewicz/AM',observed or self.inventory(),output)
        return output,report

    def test_inventory_is_read_only_and_classifies_clients(self):
        before={str(p):p.read_bytes() for p in self.apps.rglob('*') if p.is_file()}
        observed=self.inventory()
        self.assertEqual([r['kind'] for r in observed['clients']],
                         ['legacy-standalone','managed-catalog','managed-catalog'])
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.apps.rglob('*') if p.is_file()})
        self.assertIn('no other-host assertion',observed['scope']['completeness'])

    def test_pinned_package_reproducible_and_source_byte_exact(self):
        observed=self.inventory()
        one,report=self.build(observed)
        two,_=self.build(observed,'second')
        self.assertEqual((one/'manifest.json').read_bytes(),(two/'manifest.json').read_bytes())
        self.assertEqual(cutover.sha256(one/'source.tar.gz'),cutover.sha256(two/'source.tar.gz'))
        self.assertEqual((one/'runtime/APP-MANAGER').read_bytes(),cutover.blob(ROOT,self.pin,'APP-MANAGER'))
        self.assertEqual(cutover.verify_package(one),report)
        self.assertFalse(report['apply_ready'])
        choices={r['app']:r['disposition'] for r in report['clients']}
        self.assertEqual(choices['sunshine'],'retain-format-1-not-yaml-enrolled')
        self.assertEqual(choices['obsidian'],'bound-ready-pending-publication')
        replacement_path=next(r['replacement'] for r in report['clients'] if r['app']=='obsidian')
        replacement=(one/replacement_path).read_text()
        self.assertIn(self.pin,replacement)
        self.assertIn('CATALOG_FORMAT=2',replacement)
        self.assertIn('APPS_DIR="'+self.paths['APPS_DIR']+'"',replacement)
        subprocess.run(['sh','-n',str(one/replacement_path)],check=True)

    def test_payload_tamper_extra_files_and_symlinks_refuse(self):
        output,_=self.build()
        target=output/'runtime/APP-MANAGER';original=target.read_bytes()
        target.write_bytes(b'tampered')
        with self.assertRaisesRegex(ValueError,'payload drift'):cutover.verify_package(output)
        target.write_bytes(original)
        extra=output/'extra';extra.write_bytes(b'additional')
        with self.assertRaisesRegex(ValueError,'file set'):cutover.verify_package(output)
        extra.unlink();extra.symlink_to(target)
        with self.assertRaisesRegex(ValueError,'symlink'):cutover.verify_package(output)

    def test_inventory_and_legacy_recipe_drift_refuse(self):
        observed=self.inventory()
        recipe=self.apps/'obsidian/recipe.am'
        recipe.write_bytes(recipe.read_bytes()+b'changed')
        with self.assertRaisesRegex(ValueError,'installed drift'):self.build(observed)
        with self.assertRaisesRegex(ValueError,'exact legacy source binding'):self.build()

    def test_appman_roots_and_new_source_override_require_review(self):
        self.config.write_text(str(self.path/'elsewhere'))
        with self.assertRaisesRegex(ValueError,'explicitly included'):self.inventory()
        self.config.unlink()
        observed=self.inventory()
        (self.path/'data').mkdir()
        (self.path/'data/newrepo-on').write_text('https://example.org')
        with self.assertRaisesRegex(ValueError,'configuration appeared'):self.build(observed)

    def test_same_app_in_two_roots_keeps_independent_payloads(self):
        second=self.path/'second-root';second.mkdir()
        app=second/'obsidian';app.mkdir()
        paths={**self.paths,'APPS_DIR':str(second)+'/'}
        body=cutover.blob(ROOT,LEGACY,'programs/x86_64/obsidian')
        recipe=app/'recipe.am'
        recipe.write_bytes(cutover.bound_recipe(body,self.source,paths,self.modules))
        (app/'AM-updater').write_bytes(cutover.managed_updater(recipe))
        (app/'version').write_bytes(b'separate version')
        (app/'obsidian').write_bytes(b'separate binary')
        observed=cutover.inventory([self.apps,second],self.manager,self.modules,
                                  'x86_64',self.config,self.path/'data')
        output,report=self.build(observed)
        rows=[r for r in report['clients'] if r['app']=='obsidian']
        self.assertEqual(len({r['replacement'] for r in rows}),2)
        for row in rows:
            original=Path(row['installation'])/'recipe.am'
            backup=output/'before/clients'/row['installation_id']/'recipe.am'
            self.assertEqual(backup.read_bytes(),original.read_bytes())
            self.assertIn(str(original.parent.parent),(output/row['replacement']).read_text())
        cutover.verify_package(output)

    def test_symlink_manager_refuses_before_following_contents(self):
        target=self.manager.with_name('target-manager')
        self.manager.rename(target);self.manager.symlink_to(target)
        with self.assertRaisesRegex(ValueError,'manager must be a regular file'):
            self.inventory()

    def test_new_updater_or_module_refuses_stale_inventory(self):
        observed=self.inventory()
        extra=self.apps/'additional';extra.mkdir()
        (extra/'AM-updater').write_bytes(b'extra updater')
        with self.assertRaisesRegex(ValueError,'updater set changed'):self.build(observed)
        (extra/'AM-updater').unlink();extra.rmdir()
        (self.modules/'additional.am').write_bytes(b'extra module')
        with self.assertRaisesRegex(ValueError,'module set changed'):self.build(observed)

    def test_binding_literal_paths_and_refuses_noncompact_recipes(self):
        paths={k:v+'/some $`" path' for k,v in self.paths.items()}
        result=cutover.bound_recipe(cutover.blob(ROOT,self.pin,'programs/x86_64/obsidian'),
                                   self.source,paths,self.modules)
        self.assertIn(b'some \\$\\`\\" path',result)
        with self.assertRaisesRegex(ValueError,'compact recipe'):
            cutover.bound_recipe(b'#!/bin/sh\necho unrelated',self.source,paths,self.modules)


if __name__=='__main__':unittest.main()
