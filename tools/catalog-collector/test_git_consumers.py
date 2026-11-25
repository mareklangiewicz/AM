"""Native projections and actual shell reads of Git observations in raw catalog/ files."""
import os
from pathlib import Path
import subprocess
import unittest

import documents
import fixture_catalog
from publication import git
import test_yaml_manager_integration as integration

ROOT=Path(__file__).resolve().parents[2]
AT='2026-11-09T12:00:00Z'


class GitConsumers(unittest.TestCase):
    setUp=integration.YAMLManager.setUp
    script=integration.YAMLManager.script
    env=integration.YAMLManager.env
    calls=integration.YAMLManager.calls

    def snapshot(self,commit='b'*40):
        """catalog/ files: junest reads a branch file, trans and watched read tags."""
        tree={};apps={}
        for app,rid,repo in [('junest',25396290,'fsquillace/junest'),
                             ('trans',7997994,'soimort/translate-shell'),
                             ('watched',372085438,'mediaurl/mediaurl-js')]:
            doc=dict(repository_id=rid,repository=repo,observed_at=AT,history_complete=True,releases={})
            if app=='junest':
                doc['git_scope']=dict(tags=False,tags_history_complete=False)
                doc['git_refs']={'refs/heads/master':dict(commit=commit,files={'VERSION':dict(blob='c'*40,content='1.2\n')})}
            else:
                doc['git_scope']=dict(tags=True,tags_history_complete=True)
                doc['git_refs']={'refs/tags/'+tag:dict(commit=commit,position=i)
                                 for i,tag in enumerate(['irrelevant','v3alpha','v2','v1'])}
            apps[app]=dict(repository='repositories/'+app+'.yaml',x86_64='declaration')
            tree['catalog/repositories/'+app+'.yaml']=documents.encode('repository',doc)
        tree['catalog/apps.yaml']=documents.encode('apps',dict(apps=apps))
        return tree

    def prepare(self):
        self.repo=self.path/'remote.git';self.repo.mkdir();git(self.repo,'init','--bare','--quiet','--template=')
        self.tree=self.snapshot();fixture_catalog.publish(self.repo,self.tree);self.clock=AT

    def read(self,app,*args,extra=None):
        (self.path/'calls').unlink(missing_ok=True)
        return subprocess.run(['sh',str(self.module_dir/'catalog-yaml.am'),'x86_64/'+app,*args],
            env=dict(self.env(),**(extra or {})),capture_output=True,text=True)

    def test_shell_outputs_preserve_tag_filters(self):
        self.prepare()
        for app,option,expected in [('junest','--git-snapshot','b'*40+'\n1.2\n'),
                                     ('junest','--git-file','1.2\n'),
                                     ('junest','--git-commit','b'*40+'\n'),
                                     ('trans','--tag','v3alpha\n'),('watched','--tag','v2\n')]:
            with self.subTest(app=app,option=option):
                result=self.read(app,option);self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual(result.stdout,expected)

    def test_old_git_observation_warns_once_and_still_selects(self):
        self.prepare();self.clock='2026-11-24T12:00:01Z'  # 15 days after AT
        for app,option,expected in [('junest','--git-snapshot','b'*40+'\n1.2\n'),('trans','--tag','v3alpha\n')]:
            with self.subTest(app=app):
                result=self.read(app,option);self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual(result.stdout,expected)
                self.assertEqual(result.stderr.count('last seen 15 days ago'),1,result.stderr)

    def test_one_command_session_warns_about_an_app_once(self):
        self.prepare();self.clock='2026-11-24T12:00:01Z'
        session=self.path/'session';session.mkdir()
        first,second=(self.read('junest',option,extra=dict(AM_CATALOG_SESSION=str(session)))
                      for option in ('--git-commit','--git-file'))
        for result in (first,second):self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual((first.stderr+second.stderr).count('last seen 15 days ago'),1,first.stderr+second.stderr)
        other=self.read('trans','--tag',extra=dict(AM_CATALOG_SESSION=str(session)))
        self.assertEqual(other.stderr.count('last seen 15 days ago'),1,other.stderr)

    def test_git_observation_under_two_weeks_old_selects_without_a_warning(self):
        self.prepare();self.clock='2026-11-22T12:00:00Z'  # 13 days after AT
        result=self.read('junest','--git-commit');self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,'b'*40+'\n');self.assertEqual(result.stderr,'')

    def test_native_git_and_release_projections_across_awk_implementations(self):
        self.prepare();path=self.path/'source.yaml';path.write_bytes(self.tree['catalog/repositories/junest.yaml'])
        for command in (['mawk'],['gawk'],['busybox','awk']):
            for operation in ('git_facts','release_facts'):
                result=subprocess.run([*command,'-f',str(ROOT/'modules/catalog-tables.am'),
                    '-f',str(ROOT/'modules/catalog-parser.am'),str(path)],
                    env=dict(os.environ,AM_YAML_OPERATION=operation),capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stderr)
                if operation=='release_facts':self.assertEqual(result.stdout,'')
                else:
                    fields=result.stdout.rstrip('\n').split('\t')
                    self.assertEqual(fields[0:3],['"refs/heads/master"','"'+'b'*40+'"','"'+AT+'"'])
                    self.assertEqual(fields[4:],['"VERSION"','"'+'c'*40+'"','"1.2\\n"'])


if __name__=='__main__':unittest.main()
