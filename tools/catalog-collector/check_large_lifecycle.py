"""Explicit offline full-batch recipe install/update check; not discovery default.

Uses exact retained metadata and inert test AppImages. Never executes a downloaded
application. The common lifecycle test harness binds every install to a temp root.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

from identity_batch import ROOT
from large_evidence import DIRECTORY
from large_replay import build
from shards import split
from storage import validate
from test_appimage_lifecycle import selector_script
import test_migration_batch as fixtures
from shell_lookup import epoch


class LargeLifecycle(fixtures.BatchLifecycle):
    expected_architectures = {'x86_64','aarch64','i686'}

    @classmethod
    def setUpClass(cls):
        migration = json.loads((DIRECTORY/'prepared/migration.json').read_bytes())
        cls.rows = [dict(item, asset=item['selected']) for item in migration['migrated']]
        if getattr(cls,'only',None):
            cls.rows = [item for item in cls.rows if item['path'] in cls.only]
            if {item['path'] for item in cls.rows} != cls.only:
                raise ValueError('unknown_selected_recipe')
            cls.expected_architectures = {Path(item['path']).parent.name for item in cls.rows}
        cls.base, _, cls.generation = build()
        cls.entries = {}
        cls.aliases = {}
        for tree in split(cls.base).values():
            index = validate(tree)
            cls.entries.update(index['entries'])
            cls.aliases.update(index['aliases'])
        cls.rid = cls.aliases[cls.rows[0]['alias']]['request_id']
        cls.obs = cls.entries[cls.rid]['observation']

    def activate(self, item):
        self.rid = self.aliases[item['alias']]['request_id']
        self.obs = self.entries[self.rid]['observation']
        self.body = self.base[self.obs['path']]
        self.tree = {'lookup.tsv':self.base['lookup.tsv'], self.obs['path']:self.body}
        self.now = [epoch(self.generation)]*3

    def test_all_final_recipe_bytes_and_selected_assets(self):
        for item in self.rows:
            with self.subTest(path=item['path']):
                path = ROOT/item['path']
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),item['candidate_sha256'])
                body = (ROOT/item['evidence']/'body.json').read_bytes()
                selected = subprocess.run(['sh','-c',selector_script(path)],
                    input=body,capture_output=True,check=True,timeout=10).stdout.decode().strip()
                self.assertEqual(selected,item['selected'])


if __name__ == '__main__':
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument('--only',action='append')
    args,remaining=parser.parse_known_args()
    LargeLifecycle.only=set(args.only or [])
    unittest.main(argv=[sys.argv[0],*remaining])
