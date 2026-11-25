"""Git observations never acquire synthetic release or asset identities."""
import base64
import hashlib
import json
import os
import subprocess
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

import git_observations as g
import host_catalog as host


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
            (folder/'git-sources.json').write_text(json.dumps({'123':dict(tags=False,branches={'master':['VERSION']})}))
            calls=[];replies=iter([[],*self.replies()])
            def response(rid,evidence,allowance,**kwargs):
                calls.append(kwargs.get('endpoint','releases'));return json.dumps(next(replies)).encode(),'2026-11-09T12:00:00Z'
            acquisitions={};metrics={}
            profile=dict(source_cap=1,request_cap=2,total_cap=100000,seconds_cap=900,reserve=100,response_cap=100000)
            with patch.object(host,'ROOT',root),patch.object(host,'configuration',return_value=([dict(app='example')],{'123':'owner/project'})),patch.object(host,'_response',side_effect=response):
                report=host.collect({},batch_size=1,metrics=metrics,acquisitions=acquisitions,profile=profile)
            self.assertEqual(len(calls),2)
            self.assertEqual(acquisitions,{})
            self.assertEqual(report[0]['reason'],'request_budget')
            self.assertEqual(metrics['requests'],2)
            self.assertEqual(metrics['stop_reason'],'request_limit')

    def test_tags_are_keyed_by_name_in_listing_order(self):
        raw=json.dumps([dict(name=name,commit=dict(sha=char*40)) for name,char in (('v2','a'),('v1','b'))]).encode()
        result=g.collect(dict(tags=True,branches={}),lambda *a:(raw,'2026-11-09T12:00:00Z'))
        self.assertEqual(result,dict(git_scope=dict(tags=True,tags_history_complete=True),
            git_refs={'refs/tags/v2':dict(commit='a'*40,position=0),'refs/tags/v1':dict(commit='b'*40,position=1)}))

    def test_duplicate_tag_names_never_choose_a_commit(self):
        raw=json.dumps([dict(name='v1',commit=dict(sha=char*40)) for char in ('a','b')]).encode()
        with self.assertRaises(ValueError):g.collect(dict(tags=True,branches={}),lambda *a:(raw,'2026-11-09T12:00:00Z'))


if __name__=='__main__':unittest.main()
