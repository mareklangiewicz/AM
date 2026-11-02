"""Real saved release selectors; synthetic publications/inert AppImages, offline."""
import copy
from decimal import Decimal
import shlex
import hashlib
import json
from pathlib import Path
import subprocess
import unittest
from functools import lru_cache

from collector import Descriptor
from identity_batch import ROOT, PAYLOAD
from migration_batch import REPORT, compact_recipe, pipeline
from storage import apply, canonical, validate
from test_appimage_lifecycle import selector_script, bound_recipe
from test_shell_consumer import ShellFixture, PIN
import test_storage as storage_fixture
from shell_lookup import epoch

GEN = '2026-11-02T11:20:00+00:00'  # labeled synthetic publication time


def migration_rows():
    return json.loads(REPORT.read_bytes())['migrated']


@lru_cache(maxsize=None)
def retained_tree(alias, evidence):
    """Six-source fixture substitutes one source; never an operational manifest."""
    if not hasattr(storage_fixture.StorageContract, "base"):
        storage_fixture.StorageContract.setUpClass()
    directory = ROOT/evidence
    report = json.loads((directory/'report.json').read_bytes())
    body = (directory/'body.json').read_bytes()
    assert report['accepted'] and hashlib.sha256(body).hexdigest() == report['body_sha256']
    manifest = json.loads(storage_fixture.StorageContract.raw)
    descriptor = report['descriptor']
    repository_id = int(descriptor['url'].split('/repositories/')[1].split('/')[0])
    manifest['sources'][0] = dict(name='batch-fixture', repository_id=repository_id,
                                 url=descriptor['url'], request_id=descriptor['request_id'],
                                 identity_evidence='docs/track/release-catalog/research/appimage-batch-20261102.md#identity-evidence', aliases=[alias])
    attempts = copy.deepcopy(storage_fixture.StorageContract.attempts[1:])
    attempts.append(dict(request_id=descriptor['request_id'],
                         descriptor={k:descriptor[k] for k in ('url','api_version','accept')},
                         repository_id=repository_id, request_started_at=report['started_at'],
                         response_completed_at=report['completed_at'], attempt_finished_at=GEN,
                         status=200, headers=report['public_headers'], body=body,
                         condition={}, outcome='response'))
    tree, _ = apply(None, canonical(manifest), attempts, workflow_identity=1291019762,
                    generated_at=GEN, revision='a'*40, run={'id':'1','attempt':'1'})
    validate(tree)
    return tree


class BatchSelectors(unittest.TestCase):
    def test_every_candidate_preserves_both_original_filters_and_real_asset(self):
        payload = json.loads(PAYLOAD.read_bytes())
        frozen = {r['path']:(row,r) for row in payload['rows'] for r in row['recipes']}
        rows = migration_rows()
        self.assertGreaterEqual(len(rows), 77)
        for item in rows:
            with self.subTest(path=item['path']):
                path = ROOT/item['path']
                row, recipe = frozen[item['path']]
                self.assertEqual(path.read_text(), compact_recipe(recipe,row))
                body = (ROOT/item['evidence']/'body.json').read_bytes()
                source = subprocess.check_output(['git','show',payload['source_revision']+':'+item['path']],cwd=ROOT)
                self.assertEqual(hashlib.sha256(source).hexdigest(), recipe['sha256'])
                actual = subprocess.run(['sh','-c',selector_script(path)],input=body,capture_output=True,check=True).stdout
                for key in ('install_selector','update_selector'):
                    expected = subprocess.run(['sh','-c','APP='+path.name+'\n'+pipeline(row,recipe[key])],
                                              input=body,capture_output=True,check=True).stdout
                    self.assertEqual(actual,expected)
                self.assertEqual(actual.decode().strip(),item['asset'])
                self.assertEqual(subprocess.run(['sh','-c',selector_script(path)],input=b'[]',capture_output=True,check=True).stdout,b'')
                subprocess.run(['sh','-n',str(path)],check=True)


class BatchLifecycle(ShellFixture):
    @classmethod
    def setUpClass(cls):
        cls.rows = migration_rows()
        cls.trees = {item['alias']:retained_tree(item['alias'],item['evidence']) for item in cls.rows}
        item = cls.rows[0]
        cls.base = cls.trees[item['alias']]
        cls.index = validate(cls.base)
        cls.rid = cls.index['aliases'][item['alias']]['request_id']
        cls.obs = cls.index['entries'][cls.rid]['observation']

    def activate(self, item):
        self.tree = dict(self.trees[item['alias']])
        self.index = validate(self.tree)
        self.rid = self.index['aliases'][item['alias']]['request_id']
        self.obs = self.index['entries'][self.rid]['observation']
        self.body = self.tree[self.obs['path']]
        self.now = [epoch(GEN)]*3

    def installer(self, item):
        path = ROOT/item['path']
        root = self.path/path.parent.name/path.name
        (root/'usr/local/bin').mkdir(parents=True)
        (root/'usr/local/share/applications').mkdir(parents=True)
        source = bound_recipe(path.read_text()).replace('/opt/am/modules/catalog.am',str(ROOT/'modules/catalog.am')).replace('/opt/am/modules/appimage.am',str(ROOT/'modules/appimage.am'))
        source = source.replace('/opt/',str(root)+'/opt/').replace('/usr/local/',str(root)+'/usr/local/')
        script = root/'installer'; script.write_text(source)
        return root, script

    def run_script(self, path, *, fail=False, args=None):
        self.stage()
        return subprocess.run(['sh',str(path),*(args or ['--commit',PIN])],cwd=self.path,
                              env={**self.env(),**({'DOWNLOAD_FAIL':'1'} if fail else {})},capture_output=True)

    def setUp(self):
        super().setUp()
        self.script('wget', """import os,pathlib,sys
if os.environ.get('DOWNLOAD_FAIL'): sys.exit(9)
pathlib.Path(sys.argv[sys.argv.index('-O')+1]).write_text('#!/bin/sh\\nmkdir -p squashfs-root\\ncase $2 in\\n*.desktop) printf "[Desktop Entry]\\\\nExec=fixture\\\\nIcon=fixture\\\\n" > squashfs-root/fixture.desktop ;;\\n.DirIcon) printf icon > squashfs-root/.DirIcon ;;\\nesac\\n')
""")
        self.script('notify-send','pass\n')

    def test_all_candidate_install_and_generated_standalone_update(self):
        for item in self.rows:
            with self.subTest(path=item['path']):
                self.activate(item)
                root, script = self.installer(item)
                result = self.run_script(script)
                self.assertEqual(result.returncode,0,result.stderr)
                app = root/'opt'/Path(item['path']).name
                self.assertEqual((app/'version').read_text().strip(),item['asset'])
                updater = app/'AM-updater'
                self.assertEqual(len(updater.read_text().splitlines()),3)
                self.assertTrue((root/'usr/local/bin'/app.name).samefile(app/app.name))
                self.assertTrue((root/'usr/local/share/applications'/(app.name+'-AM.desktop')).exists())
                (app/'version').write_text('old\n')
                result = self.run_script(updater)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual((app/'version').read_text().strip(),item['asset'])

    def test_invalid_app_identities_refuse_before_mutation(self):
        item=self.rows[0]
        self.activate(item)
        root, script=self.installer(item)
        source=script.read_text()
        for name in ('', '.', '..', '../escape', 'bad/name', 'bad;name'):
            with self.subTest(name=name):
                script.write_text(source.replace('APP='+Path(item['path']).name+'\n',
                                                 'APP='+shlex.quote(name)+'\n',1))
                result=self.run_script(script)
                self.assertNotEqual(result.returncode,0)
                self.assertIn(b'Invalid app identity',result.stderr)
                self.assertFalse((root/'opt').exists())

    def test_each_architecture_failure_retry_integrity_stale_and_exact_consent(self):
        representatives = {}
        for item in self.rows:
            representatives.setdefault(Path(item['path']).parent.name,item)
        self.assertEqual(set(representatives),getattr(self, 'expected_architectures',
                         {'x86_64','aarch64','i686','armv7l'}))
        for item in representatives.values():
            with self.subTest(path=item['path']):
                self.activate(item)
                root, script = self.installer(item)
                result = self.run_script(script)
                self.assertEqual(result.returncode,0,result.stderr)
                app = root/'opt'/Path(item['path']).name
                updater = app/'AM-updater'
                binary = (app/app.name).read_bytes()
                (app/'version').write_text('old\n')
                result = self.run_script(updater,fail=True)
                self.assertNotEqual(result.returncode,0)
                self.assertEqual((app/app.name).read_bytes(),binary)
                self.assertEqual((app/'version').read_text(),'old\n')
                result = self.run_script(updater)
                self.assertEqual(result.returncode,0,result.stderr)
                (app/app.name).write_text('corrupt')
                (app/'AM-VERIFIED').write_text('Checksum failure\n')
                result = self.run_script(updater)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual((app/app.name).read_bytes(),binary)
                self.tree[self.obs['path']] = b'[]'
                self.assertNotEqual(self.run_script(updater).returncode,0)
                self.assertEqual((app/app.name).read_bytes(),binary)
                self.activate(item)
                (app/'version').write_text('old\n')
                self.now = [str(Decimal(epoch(getattr(self, 'generation', GEN)))+49*3600)]*3
                self.assertNotEqual(self.run_script(updater).returncode,0)
                self.assertEqual((app/'version').read_text(),'old\n')
                result = self.run_script(updater,args=self.consent())
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual((app/'version').read_text().strip(),item['asset'])


if __name__ == '__main__':
    unittest.main()
