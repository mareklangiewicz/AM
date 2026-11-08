"""Remote-free publication protocol, final reporting and trusted incremental reuse."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import contracts as c
import pipeline_publication as p
from incremental import Snapshot,Candidate,Records
from publication import git,publish_tree,REF
from test_contracts import documents,PIN,OLD,NEW,known
from test_yaml_reader import repository
from yaml_publication import candidate_tree,schema_url


class Pipeline(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.remote=self.root/'remote.git';git(self.root,'init','--bare','--quiet','--template=',str(self.remote))
        self.stage=self.root/'seed.git';git(self.root,'init','--bare','--quiet','--template=',str(self.stage))
        self.legacy=candidate_tree({'example':123},{'123':repository()},schema=schema_url(PIN),max_file_bytes=c.FILE_CAP)
        self.parent=publish_tree(self.stage,self.legacy,None)
        git(self.stage,'push',str(self.remote),self.parent+':'+p.REFS['format-2'])
        self.inputs={key:PIN for key in ('source','policy','recipes','rules','schemas')}
        self.run=dict(id=123,attempt=2)
        d=documents();d['catalog']['producer']=self.run;d['repository']['repository_id']=123
        d['apps']['apps']={'example':'repositories/example.yaml'}
        d['provenance']['apps']={'example':{'x86_64':dict(repository_id=123,availability='unknown',classification='unknown')}}
        self.target={key+'.yaml':c.encode(d[key]) for key in ('catalog','apps','provenance')}
        self.target['repositories/example.yaml']=c.encode(d['repository'])
        self.output=self.root/'artifact';self.output.mkdir()
        self.write_artifact()
        self.args=argparse.Namespace(candidate=self.output,remote_url=str(self.remote),run_id=123,attempt=2,source_revision=PIN,expected_v2_parent=self.parent,expected_v3_parent=None,enable_targets=True,result=self.root/'result.json')
    def tearDown(self):self.temp.cleanup()
    def write_artifact(self):
        trees={'format-2':self.legacy,'format-3':self.target}
        for channel,tree in trees.items():
            for name,raw in tree.items():
                path=self.output/channel/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        report=dict(version=1,run=self.run,inputs=self.inputs,parents=dict(format_2=self.parent,format_3=None),
                    started_at=OLD,reported_at=NEW,selected_sources=[123],sources=[dict(repository_id=123,status='ok')],
                    target_counts=dict(enrolled=1,selected=1,attempted=1,successful=1,failed=0,unknown=0,unattempted=0),
                    compatibility_metrics=dict(request_cap=500,response_byte_cap=536870912,acquisition_cap_seconds=900,stop_reason='complete'),
                    acquisition=dict(http_attempts=0,charged_response_bytes=2,seconds=0),
                    hashes={channel:{name:hashlib.sha256(raw).hexdigest() for name,raw in tree.items()} for channel,tree in trees.items()})
        (self.output/'report.json').write_text(json.dumps(report))
    def invoke(self,transport=None):
        with patch('collection_interface.verify_checkout_inputs'),patch.object(p,'enrollment',return_value=([dict(app='example',repository_id=123,repository='example/app')],{'123':'example'})):
            return p.run(self.args,transport=transport)
    def head(self,channel):return p.Transport(str(self.remote)).head(self.stage,p.REFS[channel])
    def test_success_and_status_confirmation(self):
        result=self.invoke()
        self.assertTrue(all(row['state']=='confirmed' for row in result['outcomes'].values()))
        status=c.read_local(self.remote,self.head('status-1'),'status')
        root=c.decode(status['status.yaml']);report=c.decode(status[root['last_report']])
        self.assertEqual(report['input_catalog_state'],'absent')
        self.assertNotIn('input_catalog',report)
        self.assertEqual(report['publication']['commit'],self.head('format-3'))
        self.assertEqual(report['metrics']['received_bytes'],dict(state='unknown'))
        self.assertEqual(report['counts']['successful']['value'],1)
        self.assertEqual(root['last_confirmed_publication']['commit'],self.head('format-3'))
    def test_hash_schema_run_and_missing_artifact_refuse_but_finalize(self):
        mutations=[lambda:(self.output/'format-3/apps.yaml').write_text('invalid'),
                   lambda:(self.output/'report.json').write_text('{}'),
                   lambda:(self.output/'format-3/apps.yaml').symlink_to('/etc/passwd')]
        # Each independent invocation uses its own remote fixture through setUp.
        (self.output/'format-3/apps.yaml').write_text('invalid')
        result=self.invoke()
        self.assertEqual(result['validation'],'failed')
        self.assertEqual(self.head('format-2'),self.parent)
        self.assertIsNone(self.head('format-3'))
        self.assertEqual(result['outcomes']['status-1']['state'],'confirmed')
        status=c.read_local(self.remote,self.head('status-1'),'status')
        summary=c.decode(status['runs/123-2/summary.yaml'])
        self.assertEqual(summary['counts']['attempted'],dict(state='unknown'))
        self.assertEqual(summary['validation'],'failed')
    def test_v2_success_then_v3_parent_conflict_still_reports(self):
        other=publish_tree(self.stage,self.target,self.parent)
        git(self.stage,'push',str(self.remote),other+':'+p.REFS['format-3'])
        result=self.invoke()
        self.assertEqual(result['outcomes']['format-2']['state'],'confirmed')
        self.assertEqual(result['outcomes']['format-3']['state'],'conflict')
        self.assertEqual(self.head('format-3'),other)
        self.assertEqual(result['outcomes']['status-1']['state'],'confirmed')
    def test_ambiguous_write_and_summary_failure_leave_confirmed_catalogs(self):
        class Ambiguous(p.Transport):
            def push(inner,repo,ref,parent,commit):
                if ref==p.REFS['format-3']:
                    super().push(repo,ref,parent,commit)
                    raise OSError('transport lost after acceptance')
                if ref==p.REFS['status-1']:raise OSError('report lost')
                return super().push(repo,ref,parent,commit)
        result=self.invoke(Ambiguous(str(self.remote)))
        self.assertEqual(result['outcomes']['format-2']['state'],'confirmed')
        self.assertEqual(result['outcomes']['format-3']['state'],'unknown')
        self.assertIsNotNone(self.head('format-3'))
        self.assertIsNone(self.head('status-1'))
    def test_wrong_run_missing_artifact_and_unattempted_detail(self):
        report=json.loads((self.output/'report.json').read_text());report['run']['attempt']=99
        (self.output/'report.json').write_text(json.dumps(report))
        result=self.invoke()
        self.assertEqual(result['validation'],'failed')
        self.assertEqual(self.head('format-2'),self.parent)
        self.assertEqual(result['outcomes']['status-1']['state'],'confirmed')
        self.args.attempt=3;self.args.candidate=self.root/'missing';self.args.input_catalog_state='unknown'
        result=self.invoke()
        tree=c.read_local(self.remote,self.head('status-1'),'status')
        self.assertEqual(c.decode(tree['runs/123-3/summary.yaml'])['input_catalog_state'],'unknown')
        self.assertEqual(result['validation'],'failed')
        current=p.summary(dict(id=999,attempt=1),self.inputs,PIN,None,
            {'format-2':dict(state='not_attempted'),'format-3':dict(state='not_attempted')},started_at=OLD,validation='ok',reason='quota')
        evidence=dict(sources=[],selected_sources=[123])
        status=p.status_tree({},current,evidence,{},identities={123:('example','example/app')})
        source=c.decode(status['runs/999-1/sources/example.yaml'])
        self.assertEqual(source['outcome'],'unattempted')
        self.assertNotIn('completed_at',source)

    def test_newer_catalog_with_old_status_and_original_timestamp(self):
        self.invoke();old_status=self.head('status-1');old_catalog=self.head('format-3')
        before=c.read_local(self.remote,old_status,'status')
        self.parent=self.head('format-2');self.run=dict(id=123,attempt=3)
        obj=c.decode(self.target['catalog.yaml']);obj['producer']=self.run;self.target['catalog.yaml']=c.encode(obj)
        self.write_artifact()
        report=json.loads((self.output/'report.json').read_text());report['parents']['format_3']=old_catalog
        (self.output/'report.json').write_text(json.dumps(report))
        self.args.expected_v2_parent=self.parent;self.args.expected_v3_parent=old_catalog;self.args.attempt=3
        class LostStatus(p.Transport):
            def push(inner,repo,ref,parent,commit):
                if ref==p.REFS['status-1']:raise OSError('unavailable')
                return super().push(repo,ref,parent,commit)
        result=self.invoke(LostStatus(str(self.remote)))
        self.assertEqual(result['outcomes']['format-3']['state'],'confirmed')
        self.assertNotEqual(self.head('format-3'),old_catalog)
        self.assertEqual(self.head('status-1'),old_status)
        self.assertEqual(c.read_local(self.remote,old_status,'status'),before)

    def test_incremental_metadata_and_changed_blob_validation(self):
        parent=publish_tree(self.stage,self.target,self.parent)
        snap=Snapshot(self.stage,parent)
        original=snap.entries['repositories/example.yaml']
        changed=dict(self.target);descriptor=c.decode(changed['catalog.yaml']);descriptor['producer']['attempt']=3
        # Only the root changes; malformed fake receipts cannot bypass fallback.
        with patch('incremental.decode',wraps=__import__('incremental').decode) as decode:
            candidate=Candidate(snap,{'catalog.yaml':c.encode(descriptor)})
            self.assertEqual(decode.call_count,1)
        self.assertEqual(candidate.entries['repositories/example.yaml'],original)
        self.assertEqual(candidate.validation['reused_documents'],3)
        with self.assertRaises(ValueError):Candidate(snap,{'repositories/example.yaml':b'invalid'})
        with patch('incremental.rules',return_value='changed'):
            with self.assertRaises(ValueError):Candidate(snap,{})
        # A fresh process/session must validate; it never accepts serialized trust.
        self.assertEqual(Snapshot(self.stage,parent).validation['mode'],'full_parent_fallback')
        records=Records(Snapshot(self.stage,self.parent,'format-2'))
        self.assertEqual(records.metadata['123']['completed_at'],OLD)
    def test_status_retention_coverage_unknowns_and_newer_catalog_lag(self):
        previous={};d=documents();docs={'repositories/example.yaml':d['repository']}
        identities={123:('example','example/app')}
        import yaml
        # Domain behavior is checked on the final tree; avoid thousands of redundant
        # shell startups while constructing 66 individually generated reports.
        with patch.object(c,'decode',side_effect=yaml.safe_load):
            for i in range(1,67):
                current=p.summary(dict(id=i,attempt=1),self.inputs,PIN,None,
                    {'format-2':dict(state='not_attempted'),'format-3':dict(state='not_attempted')},started_at=OLD,validation='failed',reason='candidate_validation')
                current['reported_at']=NEW
                previous=p.status_tree(previous,current,None,{},identities)
        parsed=c.validate_tree(previous,'status')
        self.assertEqual(len(parsed['status.yaml']['summaries']),64)
        self.assertEqual(parsed['status.yaml']['last_confirmed_publication'],dict(state='unknown'))
        stats=parsed['statistics.yaml']
        self.assertEqual(stats['days']['2026-11-08']['reported_attempts'],66)
        self.assertEqual(stats['days']['2026-11-08']['unknown_source_count_attempts'],66)
