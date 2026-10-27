"""Offline ZIP/provenance/conditional/CAS checks; local file Git transport only."""
import copy
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import test_storage as fixtures
from test_storage import REV, GEN, LATER
from storage import apply,canonical,digest,validate
from workflow_adapter import prepare
from delivery import unpack_artifact,verify_artifact,fetch_prior,publish,read_git_tree,REMOTE_REF
from publication import git,lookup_local


class DeliveryContract(unittest.TestCase):
    setUpClass=classmethod(fixtures.StorageContract.setUpClass.__func__)
    advance=classmethod(fixtures.StorageContract.advance.__func__)

    def context(self):
        return dict(repository='mareklangiewicz/AM',repository_id='1291019762',event='workflow_dispatch',
            ref='refs/heads/main-marek',sha=REV,workflow_sha=REV,approved_revision=REV,
            run_id='1',run_attempt='1',manifest_sha256=digest(self.raw),previous_publication='')

    def files(self,context=None,prior=None,attempts=None,generated=GEN):
        context=context or self.context();attempts=copy.deepcopy(attempts or self.attempts)
        tree,transitions=apply(prior,self.raw,attempts,workflow_identity=1291019762,
                              generated_at=generated,revision=REV,run={'id':'1','attempt':'1'})
        report=dict(context=context,run={'complete':True},attempts=[])
        files={'candidate/'+p:raw for p,raw in tree.items()}
        for a in attempts:
            raw=a['body'];record={k:v for k,v in a.items() if k!='body'}
            report['attempts'].append({**record,'body_bytes':len(raw),'body_sha256':digest(raw)})
            files[a['request_id']+'.body']=raw
        files['report.json']=canonical(report)
        files['storage-report.json']=canonical(dict(outcome='validated_candidate',transitions=transitions,
            files={p:{'bytes':len(raw),'sha256':digest(raw)} for p,raw in tree.items()}))
        return files,tree

    def test_zip_accepts_only_bounded_regular_allowlisted_files(self):
        files,_=self.files();stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for name,raw in files.items():z.writestr(name,raw)
        self.assertEqual(unpack_artifact(stream.getvalue()),files)
        for name in ('../escape','/absolute','candidate/../../x','script.py','candidate/extra'):
            stream=io.BytesIO()
            with zipfile.ZipFile(stream,'w') as z:z.writestr(name,b'x')
            with self.subTest(name=name),self.assertRaises(ValueError):unpack_artifact(stream.getvalue())
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as z:
            info=zipfile.ZipInfo('report.json');info.create_system=3;info.external_attr=0o120777<<16
            z.writestr(info,b'/etc/passwd')
        with self.assertRaises(ValueError):unpack_artifact(stream.getvalue())

    def test_directory_bound_applies_before_zip_member_allocation(self):
        import struct
        raw=struct.pack('<4s4H2IH',b'PK\x05\x06',0,0,101,101,0,0,0)
        with patch('delivery.zipfile.ZipFile') as parser, self.assertRaises(ValueError):
            unpack_artifact(raw)
        parser.assert_not_called()

    def test_provenance_recomputation_and_mutations(self):
        files,tree=self.files()
        self.assertEqual(verify_artifact(files,self.context(),self.raw,REV,None),tree)
        for name in ('context','body','candidate','extra','storage_report'):
            bad=dict(files)
            if name=='context':
                report=json.loads(bad['report.json']);report['context']['run_id']='2';bad['report.json']=canonical(report)
            if name=='body':bad[self.attempts[0]['request_id']+'.body']=b'[]'
            if name=='candidate':
                index=json.loads(bad['candidate/index.json']);index['run']['id']='2';bad['candidate/index.json']=canonical(index)
            if name=='extra':bad['extra']=b'x'
            if name=='storage_report':bad['storage-report.json']=b'{}'
            with self.subTest(name=name),self.assertRaises((ValueError,KeyError)):
                verify_artifact(bad,self.context(),self.raw,REV,None)

    def test_exact_prior_plan_conditions_and_304_publication(self):
        context=self.context();context['previous_publication']='b'*40
        value=prepare(context,self.raw,REV,self.base)
        self.assertTrue(all(r.condition for r in value.requests))
        attempts=[]
        for request in value.requests:
            old=next(a for a in self.attempts if a['request_id']==request.source.descriptor.request_id)
            attempts.append({**old,'status':304,'body':b'','headers':{},'condition':dict(request.condition),
                'request_started_at':LATER,'response_completed_at':LATER,'attempt_finished_at':LATER})
        files,tree=self.files(context,self.base,attempts,LATER)
        self.assertEqual(verify_artifact(files,context,self.raw,REV,self.base),tree)
        for rid,entry in validate(tree)['entries'].items():
            self.assertEqual(entry['observation']['received_at'],validate(self.base)['entries'][rid]['observation']['received_at'])
            self.assertEqual(entry['observation']['validated_at'],LATER)
        with self.assertRaises(ValueError):prepare(context,self.raw,REV,None)
        with self.assertRaises(ValueError):prepare(self.context(),self.raw,REV,self.base)

    def test_local_remote_bootstrap_repeat_and_changed_parent_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);remote=root/'remote.git'
            subprocess.run(['git','init','--bare','--quiet','--template=',str(remote)],check=True)
            files,tree=self.files()
            with patch('delivery.URL',str(remote)),patch('delivery.download_artifact',return_value=files):
                result=publish(self.context(),self.raw,REV,'1','a'*64,b'FIXTURE',root/'first')
            commit=result['commit']
            self.assertEqual(git(remote,'rev-parse',REMOTE_REF).decode().strip(),commit)
            for alias in validate(tree)['aliases']:
                raw,entry=lookup_local(remote,alias,commit,now=GEN)
                self.assertEqual(raw,tree[entry['observation']['path']])
            context=self.context();context['previous_publication']=commit
            with patch('delivery.URL',str(remote)):
                prior=fetch_prior(context,b'FIXTURE',root/'prior')
                self.assertEqual(prior,tree)
                with self.assertRaises(ValueError):fetch_prior(self.context(),b'FIXTURE',root/'wrong')
            # A second publication with identical bodies but a later generation.
            repeated=[]
            for a in self.attempts:
                entry=validate(tree)['entries'][a['request_id']]
                repeated.append({**a,'status':304,'body':b'','headers':{},'condition':entry['validators'],
                    'request_started_at':LATER,'response_completed_at':LATER,'attempt_finished_at':LATER})
            files2,tree2=self.files(context,tree,repeated,generated=LATER)
            with patch('delivery.URL',str(remote)),patch('delivery.download_artifact',return_value=files2):
                second=publish(context,self.raw,REV,'1','a'*64,b'FIXTURE',root/'second')
            self.assertEqual(second['parent'],commit)
            with patch('delivery.URL',str(remote)),self.assertRaises(ValueError):
                fetch_prior(context,b'FIXTURE',root/'stale')
            self.assertEqual(read_git_tree(remote,commit),tree)
            self.assertEqual(read_git_tree(remote,second['commit']),tree2)


if __name__=='__main__':unittest.main()
