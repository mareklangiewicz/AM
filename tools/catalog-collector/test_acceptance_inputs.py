"""Offline source binding and complete recipe-set checks before credential access."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import accept_large as acceptance
from storage import digest


class AcceptanceInputs(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.old=self.root/'old';self.new=self.root/'new'
        self.files={}
        def save(path,value):
            path.parent.mkdir(parents=True,exist_ok=True);raw=json.dumps(value).encode();path.write_bytes(raw)
            self.files[str(path.relative_to(self.root))]=raw
        save(self.old/'payload.json',dict(rows=[dict(recipes=[dict(path='old'),dict(path='new')])]))
        for package,name in ((self.old,'old'),(self.new,'new')):
            save(package/'prepared/inventory.json',{})
            save(package/'prepared/migration.json',dict(migrated=[dict(path=name)]))
        save(self.new/'queue.json',{})
        self.context=patch.multiple(acceptance,ROOT=self.root,PAYLOAD_HASH=digest((self.old/'payload.json').read_bytes()))
        self.context.start();self.addCleanup(self.context.stop)
        def git(root,command,target):
            self.assertEqual(root,self.root);self.assertEqual(command,'show');self.assertTrue(target.startswith('a'*40+':'))
            return self.files[target.split(':',1)[1]]
        self.mock=patch.object(acceptance,'git',side_effect=git);self.mock.start();self.addCleanup(self.mock.stop)

    def test_original_profile_retains_original_recipe_scope(self):
        _,_,migration=acceptance.reviewed_inputs(self.old,self.old,None,'a'*40)
        self.assertEqual([item['path'] for item in migration['migrated']],['old'])

    def test_exception_profile_includes_old_and_new_recipes(self):
        _,_,migration=acceptance.reviewed_inputs(self.new,self.old,self.old/'prepared/migration.json','a'*40)
        self.assertEqual([item['path'] for item in migration['migrated']],['new','old'])

    def test_changed_queue_refuses_before_token_or_network(self):
        (self.new/'queue.json').write_text('{"changed":true}')
        with self.assertRaisesRegex(ValueError,'acceptance_source_data_changed'):
            acceptance.reviewed_inputs(self.new,self.old,self.old/'prepared/migration.json','a'*40)

    def test_duplicate_old_new_recipe_refuses(self):
        path=self.new/'prepared/migration.json';raw=(self.old/'prepared/migration.json').read_bytes()
        path.write_bytes(raw);self.files[str(path.relative_to(self.root))]=raw
        with self.assertRaisesRegex(ValueError,'acceptance_duplicate_recipe'):
            acceptance.reviewed_inputs(self.new,self.old,self.old/'prepared/migration.json','a'*40)
