"""Offline actual candidate install/update checks; temporary roots, inert binaries."""
import hashlib
import json
from pathlib import Path
import subprocess
import unittest

from exception_batch import DIRECTORY
from identity_batch import ROOT
from replay_exceptions import build
from shards import split
from storage import validate
from shell_lookup import epoch
from test_appimage_lifecycle import selector_script
import test_migration_batch as fixtures


class ExceptionLifecycle(fixtures.BatchLifecycle):
    expected_architectures={'x86_64','aarch64'}

    @classmethod
    def setUpClass(cls):
        cls.rows=json.loads((DIRECTORY/'prepared/migration.json').read_bytes())['migrated']
        cls.base,_,cls.generation=build()
        cls.entries={};cls.aliases={}
        for tree in split(cls.base).values():
            index=validate(tree);cls.entries.update(index['entries']);cls.aliases.update(index['aliases'])
        cls.rid=cls.aliases[cls.rows[0]['alias']]['request_id'];cls.obs=cls.entries[cls.rid]['observation']

    def activate(self,item):
        self.rid=self.aliases[item['alias']]['request_id'];self.obs=self.entries[self.rid]['observation']
        self.body=self.base[self.obs['path']]
        self.tree={'lookup.tsv':self.base['lookup.tsv'],self.obs['path']:self.body}
        self.now=[epoch(self.generation)]*3

    def test_final_recipe_hashes_and_actual_selections(self):
        for item in self.rows:
            with self.subTest(path=item['path']):
                path=ROOT/item['path'];self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),item['candidate_sha256'])
                self.activate(item)
                actual=subprocess.run(['sh','-c',selector_script(path)],input=self.body,capture_output=True,check=True,timeout=10).stdout.decode().strip()
                self.assertEqual(actual,item['selected'])


if __name__=='__main__': unittest.main()
