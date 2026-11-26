"""Git observations never acquire synthetic release or asset identities."""
import base64
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import git_observations as g
import host_catalog as host
import pinned_recipes


ROOT=Path(__file__).resolve().parents[2]


class GitReaders(unittest.TestCase):
    def test_chunk_boundaries_preserve_escaped_file_output_in_every_native_reader(self):
        import documents
        content=('x'*4094+'\\"\n')*18  # escapes straddle the reader's 4 KiB decode chunks
        at='2026-11-09T12:00:00Z'
        doc=dict(repository_id=25396290,repository='fsquillace/junest',observed_at=at,history_complete=True,releases={},
                 git_scope=dict(tags=False,tags_history_complete=False),
                 git_refs={'refs/heads/master':dict(commit='b'*40,files={'VERSION':dict(blob='c'*40,content=content)})})
        raw=documents.encode('repository',doc)
        for command in (['mawk'],['gawk'],['busybox','awk']):
            env=dict(os.environ,LC_ALL='C',AM_YAML_OPERATION='git_facts',
                AM_YAML_RECIPE='x86_64/junest',AM_YAML_REPOSITORY='25396290',
                AM_YAML_OUTPUT='git-file',AM_YAML_NOW=at)
            facts=subprocess.run([*command,'-f',str(ROOT/'modules/catalog-tables.am'),
                '-f',str(ROOT/'modules/catalog-parser.am')],input=raw,capture_output=True,env=env)
            self.assertEqual(facts.returncode,0,facts.stderr)
            result=subprocess.run([*command,'-f',str(ROOT/'modules/catalog-yaml-policy.am')],input=facts.stdout,capture_output=True,env=env)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(result.stdout.decode(),content)


class GitAcquisition(unittest.TestCase):
    def replies(self):
        content=b'1.0\n';blob=self.blob=hashlib.sha1(b'blob 4\0'+content).hexdigest()
        return [dict(ref='refs/heads/master',object=dict(type='commit',sha='b'*40)),
                dict(type='file',path='VERSION',sha=blob,size=4,encoding='base64',content=base64.b64encode(content).decode())]

    def test_file_reads_bind_the_observed_commit_and_verify_blob_bytes(self):
        calls=[];replies=iter(self.replies())
        def fetch(kind,endpoint):calls.append(endpoint);return json.dumps(next(replies)).encode(),'2026-11-09T12:00:00Z'
        result=g.collect(dict(tags=False,branches={'master':['VERSION']}),fetch)
        self.assertEqual(calls[1],'contents/VERSION?ref='+'b'*40)
        self.assertEqual(result,dict(git_scope=dict(tags=False,tags_history_complete=False),
            git_refs={'refs/heads/master':dict(commit='b'*40,files={'VERSION':dict(blob=self.blob,content='1.0\n')})}))
        bad=self.replies();bad[1]['sha']='c'*40;replies=iter(bad)
        with self.assertRaises(ValueError):g.collect(dict(tags=False,branches={'master':['VERSION']}),fetch)

    def test_extra_requests_share_budget_and_failed_source_has_no_acquisition(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);folder=root/'tools/catalog-collector';folder.mkdir(parents=True)
            calls=[];replies=iter([[],*self.replies()])
            def response(rid,evidence,allowance,**kwargs):
                calls.append(kwargs.get('endpoint','releases'));return json.dumps(next(replies)).encode(),'2026-11-09T12:00:00Z'
            acquisitions={};metrics={}
            profile=dict(source_cap=1,request_cap=2,total_cap=100000,seconds_cap=900,reserve=100,response_cap=100000)
            with patch.object(host,'ROOT',root),patch.object(host,'configuration',return_value=([dict(app='example')],{'123':'owner/project'})),patch.object(host,'_response',side_effect=response),\
                    patch.object(g,'configuration',return_value={'123':dict(tags=False,branches={'master':['VERSION']})}):
                report=host.collect({},batch_size=1,metrics=metrics,acquisitions=acquisitions,profile=profile)
            self.assertEqual(len(calls),2)
            self.assertEqual(acquisitions,{})
            self.assertEqual(report[0]['reason'],'request_budget')
            self.assertEqual(metrics['requests'],2)
            self.assertEqual(metrics['stop_reason'],'request_limit')

    def test_scopes_come_from_the_recipes_git_selections(self):
        # Ticket 29: what to read from Git is what the recipes select by.
        def row(recipe,rid,**selection):
            return dict(recipe=recipe,repository_id=rid,**selection)
        rows=[row('x86_64/a',1,selection='git-tag',tag_pattern='^v'),
              row('x86_64/b',2,selection='git-file',git_ref='refs/heads/main',git_file='VERSION'),
              row('x86_64/b.select-2',2,selection='git-file',git_ref='refs/heads/main',git_file='other.json'),
              row('x86_64/c',3,selection='git-branch',git_ref='refs/heads/dev'),
              row('x86_64/d',4,selection='release'),row('x86_64/e',5)]
        with patch('recipe_declarations.url_policy_rows',return_value=rows[:3]),\
                patch('recipe_declarations.recipe_rows',return_value=rows[3:]):
            self.assertEqual(g.configuration(Path('unused')),{
                '1':dict(tags=True,branches={}),'2':dict(tags=False,branches={'main':['VERSION','other.json']}),
                '3':dict(tags=False,branches={'dev':[]})})
        with patch('recipe_declarations.url_policy_rows',return_value=[
                row('x86_64/f',6,selection='git-file',git_ref='refs/heads/b%d'%n,git_file='F') for n in range(5)]),\
                patch('recipe_declarations.recipe_rows',return_value=[]),self.assertRaises(ValueError):
            g.configuration(Path('unused'))

    def test_the_pinned_recipes_select_from_five_git_sources(self):
        scopes=g.configuration(pinned_recipes.shared_configuration())
        self.assertEqual(scopes,{
            '25396290':dict(tags=False,branches={'master':['VERSION']}),'7997994':dict(tags=True,branches={}),
            '372085438':dict(tags=True,branches={}),'649170660':dict(tags=False,branches={'desktop':['linux_installer.sh']}),
            '903233225':dict(tags=False,branches={'main':['version-history.json']})})

    def test_tags_are_keyed_by_name_in_listing_order(self):
        raw=json.dumps([dict(name=name,commit=dict(sha=char*40)) for name,char in (('v2','a'),('v1','b'))]).encode()
        result=g.collect(dict(tags=True,branches={}),lambda *a:(raw,'2026-11-09T12:00:00Z'))
        self.assertEqual(result,dict(git_scope=dict(tags=True,tags_history_complete=True),
            git_refs={'refs/tags/v2':dict(commit='a'*40,position=0),'refs/tags/v1':dict(commit='b'*40,position=1)}))

    def test_duplicate_tag_names_never_choose_a_commit(self):
        raw=json.dumps([dict(name='v1',commit=dict(sha=char*40)) for char in ('a','b')]).encode()
        with self.assertRaises(ValueError):g.collect(dict(tags=True,branches={}),lambda *a:(raw,'2026-11-09T12:00:00Z'))


if __name__=='__main__':unittest.main()
