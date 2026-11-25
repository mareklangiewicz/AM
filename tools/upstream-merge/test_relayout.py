"""The selection-equivalence check names every way a re-conversion can change
what a recipe selects.

Pinned Git objects: x86_64/zulip as a long recipe with its policy row at
cf6255fc3, and as the declaration ticket 33 converted it to at 082502f64.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import relayout as r

LONG_AT='cf6255fc399245395ad4fc7f247b778a12e0f201'
DECLARED_AT='082502f64c'
PATH='programs/x86_64/zulip'


def show(commit,path):
    return r.merge.git(r.ROOT,'show',commit+':'+path).stdout


def registry(commit):
    return [row for row in json.loads(show(commit,r.merge.REGISTRY)) if row['source_recipe']=='x86_64/zulip']


class Equivalence(unittest.TestCase):
    def setUp(self):
        self.before={PATH:show(LONG_AT,PATH)}
        self.policies=registry(LONG_AT)
        self.after=show(DECLARED_AT,PATH)
        self.assertEqual(len(self.policies),1)
        self.assertIn(b'# AM-RECIPE-DECLARATION 1\n',self.after)

    def check(self,after):
        return r.differences(self.before,self.policies,{PATH:after},[])

    def test_ticket_33s_conversion_of_zulip_selects_the_same(self):
        self.assertEqual(self.check(self.after),[])

    def test_each_changed_selection_field_is_named(self):
        mutants={
            'repository_id':(b'CATALOG_REPOSITORY_ID=60656871',b'CATALOG_REPOSITORY_ID=60656872'),
            'repository':(b'CATALOG_REPOSITORY=zulip/zulip-desktop',b'CATALOG_REPOSITORY=zulip/zulip-desktop2'),
            'channel':(b'CATALOG_CHANNEL=any',b'CATALOG_CHANNEL=stable'),
            'asset_pattern':(b"CATALOG_ASSET_PATTERN='^.*$'",b"CATALOG_ASSET_PATTERN='^.*AppImage$'"),
            'url_rules':(b'https.*mage$',b'https.*image$'),
            'catalog_app':(b'CATALOG_CHANNEL=any',b'CATALOG_CHANNEL=any\nCATALOG_APP=zulip-desktop'),
        }
        for field,(old,new) in mutants.items():
            with self.subTest(field):
                self.assertEqual(self.after.count(old),1)
                found=self.check(self.after.replace(old,new))
                self.assertEqual(len(found),1,found)
                self.assertIn('x86_64/zulip',found[0]);self.assertIn(field,found[0])

    def test_compiled_fields_a_declaration_would_drop_are_named(self):
        # Shapes long recipes' policy rows have (x86_64/cccp, watched, cursor).
        mutants={'selection':dict(selection='release'),
                 'tag_pattern':dict(selection='release',tag_pattern='[0-9]$'),
                 'tag_exclude':dict(selection='git-tag',tag_pattern='^v[0-9]',tag_exclude='alpha|next'),
                 'git_file':dict(selection='git-file',git_ref='refs/heads/main',git_file='VERSION')}
        for field,extra in mutants.items():
            with self.subTest(field):
                found=r.differences(self.before,[dict(self.policies[0],**extra)],{PATH:self.after},[])
                self.assertEqual(len(found),1,found);self.assertIn(field,found[0])

    def test_a_recipe_that_stops_selecting_is_named(self):
        found=r.differences(self.before,self.policies,{PATH:b'#!/bin/sh\necho plain\n'},[])
        self.assertEqual(len(found),1,found);self.assertIn('x86_64/zulip',found[0])


class Encoding(unittest.TestCase):
    def test_written_files_are_utf8_whatever_the_locale(self):
        with tempfile.TemporaryDirectory() as root:
            for command in (['init','-q'],['-c','user.name=t','-c','user.email=t@t','commit','-q','--allow-empty','-m','t']):
                subprocess.run(['git','-C',root,*command],check=True)
            head=r.merge.git(root,'rev-parse','HEAD').stdout.decode().strip()
            script=('import sys;sys.path.insert(0,sys.argv[1]);import relayout;'
                    'relayout.write(sys.argv[2],dict(ours=sys.argv[3],rows=[],files={"f":"za\\u017c\\u00f3\\u0142\\u0107"}))')
            env=dict(os.environ,LC_ALL='C',PYTHONUTF8='0',PYTHONCOERCECLOCALE='0')
            done=subprocess.run([sys.executable,'-B','-c',script,str(Path(r.__file__).parent),root,head],env=env,
                                capture_output=True,text=True,errors='replace')
            self.assertEqual(done.returncode,0,done.stderr)
            self.assertEqual((Path(root)/'f').read_bytes(),'zażółć'.encode())


class Layout(unittest.TestCase):
    def test_a_commit_shared_by_two_layouts_needs_the_path(self):
        with self.assertRaisesRegex(r.Problem,'AM-SAMPLE-AppImage-in-archive') as raised:
            r.chosen(r.convert.layouts(),'cf50304fc')
        self.assertIn('templates/AM-SAMPLE-AppImage,',str(raised.exception)+',')
        for path in ('templates/AM-SAMPLE-AppImage','templates/AM-SAMPLE-AppImage-in-archive'):
            self.assertEqual(r.chosen(r.convert.layouts(),'cf50304fc:'+path).path,path)


if __name__=='__main__':unittest.main()
