"""Git observations never acquire synthetic release or asset identities."""
import copy
import base64
import hashlib
import json
import subprocess
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

import contracts as c
from test_contracts import sample
import git_observations as g
import host_catalog as host


def key(name):return hashlib.sha256(name.encode()).hexdigest()


class GitContract(unittest.TestCase):
    def document(self):
        doc=sample();at=doc['collected_at'];branch='refs/heads/master';tag='refs/tags/v1'
        doc['git_scope']=dict(tags=True,tags_history_complete=True,branches={key(branch):branch})
        doc['git_refs']={key(tag):dict(name=tag,commit='a'*40,observed_at=at,position=0),
            key(branch):dict(name=branch,commit='b'*40,observed_at=at,
                files={key('VERSION'):dict(path='VERSION',blob='c'*40,observed_at=at,content='1.0\n')})}
        return doc

    def check(self,doc,valid=True):
        raw=c.encode(doc)
        if valid:c.decode(raw)
        else:
            with self.assertRaises(ValueError):c.decode(raw)
        js="import {parseDocument} from './tools/catalog-contract/reader.mjs';let s='';for await(const b of process.stdin)s+=b;try{parseDocument(s)}catch(e){console.error(e.message);process.exitCode=2}"
        result=subprocess.run(['node','--input-type=module','-e',js],input=raw,capture_output=True,cwd=c.ROOT)
        self.assertEqual(result.returncode,0 if valid else 2,result.stderr)
        for command in (['mawk'],['gawk'],['busybox','awk']):
            result=subprocess.run([*command,'-f',str(c.ROOT/'modules/catalog-contract-tables.am'),
                '-f',str(c.ROOT/'modules/catalog-contract-parser.am')],input=raw,capture_output=True,
                env={'PATH':'/usr/bin:/bin','LC_ALL':'C','AM_YAML_OPERATION':'validate'})
            self.assertEqual(result.returncode,0 if valid else 2,(command,result.stderr))

    def test_tag_and_commit_pinned_file_observations(self):self.check(self.document())

    def test_incomplete_or_inconsistent_scope_and_time_refuse(self):
        original=self.document()
        for change in ('missing_scope','missing_branch','duplicate_name','position_gap','file_traversal','future_file'):
            doc=copy.deepcopy(original);branch=doc['git_refs'][key('refs/heads/master')]
            if change=='missing_scope':del doc['git_scope']
            elif change=='missing_branch':del doc['git_refs'][key('refs/heads/master')]
            elif change=='duplicate_name':doc['git_refs']['d'*64]=copy.deepcopy(branch)
            elif change=='position_gap':doc['git_refs'][key('refs/tags/v1')]['position']=1
            elif change=='file_traversal':branch['files'][key('VERSION')]['path']='../VERSION'
            else:branch['files'][key('VERSION')]['observed_at']='2099-01-01T00:00:00Z'
            with self.subTest(change=change):self.check(doc,False)


class GitAcquisition(unittest.TestCase):
    def replies(self):
        content=b'1.0\n';blob=hashlib.sha1(b'blob 4\0'+content).hexdigest()
        return [dict(ref='refs/heads/master',object=dict(type='commit',sha='b'*40)),
                dict(type='file',path='VERSION',sha=blob,size=4,encoding='base64',content=base64.b64encode(content).decode())]

    def test_file_reads_bind_the_observed_commit_and_verify_blob_bytes(self):
        calls=[];replies=iter(self.replies())
        def fetch(kind,endpoint):calls.append(endpoint);return json.dumps(next(replies)).encode(),'2026-11-09T12:00:00Z'
        result=g.collect(dict(tags=False,branches={'master':['VERSION']}),fetch)
        self.assertEqual(calls[1],'contents/VERSION?ref='+'b'*40)
        file=next(iter(result['git_refs'][key('refs/heads/master')]['files'].values()))
        self.assertEqual(file['content'],'1.0\n')
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
                _,report=host.collect('a'*40,{},batch_size=1,metrics=metrics,acquisitions=acquisitions,native_v3=True,profile=profile)
            self.assertEqual(len(calls),2)
            self.assertEqual(acquisitions,{})
            self.assertEqual(report[0]['reason'],'request_budget')
            self.assertEqual(metrics['requests'],2)
            self.assertEqual(metrics['stop_reason'],'request_limit')

    def test_duplicate_tag_names_never_choose_a_commit(self):
        raw=json.dumps([dict(name='v1',commit=dict(sha=char*40)) for char in ('a','b')]).encode()
        with self.assertRaises(ValueError):g.collect(dict(tags=True,branches={}),lambda *a:(raw,'2026-11-09T12:00:00Z'))


if __name__=='__main__':unittest.main()
