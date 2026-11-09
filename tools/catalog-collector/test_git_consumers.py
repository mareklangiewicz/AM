"""Native projections and actual shell reads of commit-pinned Git observations."""
import os
import subprocess
import unittest

import contracts as c
from publication import git,publish_tree
from test_git_observations import key
import test_yaml_manager_integration as integration

AT='2026-11-09T12:00:00Z'
PIN='a'*40


class GitConsumers(unittest.TestCase):
    setUp=integration.YAMLManager.setUp
    script=integration.YAMLManager.script
    env=integration.YAMLManager.env
    calls=integration.YAMLManager.calls

    def snapshot(self,commit='b'*40):
        tree={};apps={}
        for app,rid,repo in [('junest',25396290,'fsquillace/junest'),
                             ('trans',7997994,'soimort/translate-shell'),
                             ('watched',372085438,'mediaurl/mediaurl-js')]:
            doc=c.source(None,dict(received_at=AT,releases={},history_complete=True),
                         rid=rid,repository=repo,revision=PIN)
            if app=='junest':
                name='refs/heads/master'
                doc['git_scope']=dict(tags=False,tags_history_complete=False,branches={key(name):name})
                doc['git_refs']={key(name):dict(name=name,commit=commit,observed_at=AT,
                    files={key('VERSION'):dict(path='VERSION',blob='c'*40,observed_at=AT,content='1.2\n')})}
            else:
                doc['git_scope']=dict(tags=True,tags_history_complete=True,branches={})
                doc['git_refs']={key('refs/tags/'+tag):dict(name='refs/tags/'+tag,commit=commit,
                    observed_at=AT,position=i) for i,tag in enumerate(['irrelevant','v3alpha','v2','v1'])}
            path='repositories/'+app+'.yaml';apps[app]=path;tree[path]=c.encode(doc)
        tree['catalog.yaml']=c.encode(dict(c.header('catalog',PIN),
            inputs={k:PIN for k in ('source','policy','recipes','rules','schemas')},
            producer=dict(id=1,attempt=1),retention='32-plus-stable-exact-tag-v1'))
        tree['apps.yaml']=c.encode(dict(c.header('apps',PIN),apps=apps))
        tree.update(c.partition_provenance(apps,{app:{'x86_64':dict(repository_id=rid,
            availability='unknown',classification='unknown')} for app,rid in
            [('junest',25396290),('trans',7997994),('watched',372085438)]},PIN))
        c.validate_tree(tree)
        return tree

    def prepare(self):
        self.repo=self.path/'remote.git';self.repo.mkdir();git(self.repo,'init','--bare','--quiet','--template=')
        self.tree=self.snapshot();self.pin=publish_tree(self.repo,self.tree,None);self.clock=AT

    def read(self,app,*args,extra=None):
        (self.path/'calls').unlink(missing_ok=True)
        return subprocess.run(['sh',str(self.module_dir/'catalog-yaml.am'),'x86_64/'+app,*args],
            env=dict(self.env(),**(extra or {})),capture_output=True,text=True)

    def test_shell_outputs_preserve_tag_filters_and_snapshot_pin(self):
        self.prepare()
        for app,option,expected in [('junest','--git-snapshot','b'*40+'\n1.2\n'),
                                     ('junest','--git-file','1.2\n'),
                                     ('junest','--git-commit','b'*40+'\n'),
                                     ('trans','--tag','v3alpha\n'),('watched','--tag','v2\n')]:
            with self.subTest(app=app,option=option):
                result=self.read(app,option);self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual(result.stdout,expected)
        tip=publish_tree(self.repo,self.snapshot('d'*40),self.pin)
        (self.path/'move-to').write_text(tip+'\n')
        result=self.read('junest','--git-snapshot')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,'b'*40+'\n1.2\n')
        self.assertTrue(all('/'+self.pin+'/' in call[-1] for call in self.calls()
                            if 'raw.githubusercontent.com' in call[-1]))

    def test_stale_git_observation_refuses_without_payload_or_output(self):
        self.prepare();self.clock='2026-11-12T12:00:00Z'
        for app,option in [('junest','--git-snapshot'),('trans','--tag'),('watched','--tag')]:
            result=self.read(app,option);self.assertNotEqual(result.returncode,0)
            self.assertEqual(result.stdout,'');self.assertIn('fresh_non_asset_observation_required',result.stderr)
        self.assertFalse((self.path/'downloads').exists())

    def test_native_git_and_release_projections_across_awk_implementations(self):
        self.prepare();path=self.path/'source.yaml';path.write_bytes(self.tree['repositories/junest.yaml'])
        for command in (['mawk'],['gawk'],['busybox','awk']):
            for operation in ('git_facts','release_facts'):
                result=subprocess.run([*command,'-f',str(c.ROOT/'modules/catalog-contract-tables.am'),
                    '-f',str(c.ROOT/'modules/catalog-contract-parser.am'),str(path)],
                    env=dict(os.environ,AM_YAML_OPERATION=operation),capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stderr)
                if operation=='release_facts':self.assertEqual(result.stdout,'')
                else:
                    fields=result.stdout.rstrip('\n').split('\t')
                    self.assertEqual(fields[1:4],['"refs/heads/master"','"'+'b'*40+'"','"'+AT+'"'])
                    self.assertEqual(fields[5:],[ '"VERSION"','"'+'c'*40+'"','"1.2\\n"'])


if __name__=='__main__':unittest.main()
