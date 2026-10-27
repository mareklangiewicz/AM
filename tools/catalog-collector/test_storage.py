"""Storage contracts against measured saved evidence and synthetic transitions."""
import copy
from datetime import datetime, timedelta
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from collector import Descriptor
from storage import apply, canonical, decode, digest, validate, INDEX_CAP, TREE_CAP
from publication import git, publish_local, lookup_local

ROOT = Path(__file__).resolve().parents[2]
REV = 'a' * 40
GEN = '2026-10-27T15:20:00+00:00'
LATER = '2026-10-27T15:21:00+00:00'


class StorageContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / 'docs/track/release-catalog/design/staged-manifest.json').read_bytes()
        archive = ROOT / 'docs/track/release-catalog/research/supervised-baseline-40529551070-evidence.tar.gz'
        with tarfile.open(archive) as tar:
            prefix = 'supervised-baseline-40529551070/'
            report = json.load(tar.extractfile(prefix + 'report.json'))
            cls.attempts = []
            for record in report['attempts']:
                a = {k: v for k, v in record.items() if k not in {'body_bytes', 'body_sha256'}}
                a['body'] = tar.extractfile(prefix + a['request_id'] + '.body').read()
                assert digest(a['body']) == record['body_sha256']
                cls.attempts.append(a)
        cls.base, _ = cls.advance(None, cls.attempts)
        cls.rid = cls.attempts[0]['request_id']
        cls.alias = json.loads(cls.raw)['sources'][0]['aliases'][0]

    @classmethod
    def advance(cls, previous, attempts, raw=None, generated=GEN):
        return apply(previous, raw or cls.raw, attempts, workflow_identity=1291019762,
                     generated_at=generated, revision=REV, run={'id': '1', 'attempt': '1'})

    def event(self, status, *, body=b'', outcome='response', headers=None, condition=None):
        a = copy.deepcopy(self.attempts[0])
        a.update(status=status, body=body, outcome=outcome, headers=headers or {}, condition=condition or {},
                 request_started_at=LATER, attempt_finished_at=LATER,
                 response_completed_at=LATER if outcome == 'response' else None)
        return a

    def test_saved_baseline_exact_bytes_measured_provenance_and_aliases(self):
        index = validate(self.base)
        self.assertEqual(len(index['entries']), 6)
        self.assertEqual(index['manifest_json'].encode(), self.raw)
        for a in self.attempts:
            entry = index['entries'][a['request_id']]
            self.assertEqual(entry['availability'], 'available')
            self.assertEqual(self.base[entry['observation']['path']], a['body'])
            self.assertEqual(entry['observation']['received_at'], a['response_completed_at'])
            self.assertEqual(entry['observation']['received_time_basis'], 'response-completed')
        self.assertTrue(index['aliases'][self.alias]['active'])

    def test_304_preserves_receipt_and_body_advances_only_validation(self):
        before = validate(self.base)['entries'][self.rid]
        a = self.event(304, condition=before['validators'])
        tree, _ = self.advance(self.base, [a], generated=LATER)
        after = validate(tree)['entries'][self.rid]
        self.assertEqual(after['observation']['received_at'], before['observation']['received_at'])
        self.assertEqual(after['observation']['validated_at'], LATER)
        self.assertEqual(tree['bodies/'+self.rid+'.json'], self.base['bodies/'+self.rid+'.json'])
        self.assertEqual(after['latest_attempt']['headers'], {})
        self.assertEqual(after['validators'], before['validators'])

    def test_304_without_exact_prior_or_on_unavailable_refuses(self):
        conditions = [{}, {'etag': 'wrong'}, validate(self.base)['entries'][self.rid]['validators']]
        for previous, condition in [(self.base, c) for c in conditions[:2]] + [(None, conditions[2])]:
            with self.assertRaises(ValueError):
                self.advance(previous, [self.event(304, condition=condition)], generated=LATER)
        removed, _ = self.advance(self.base, [self.event(404)], generated=LATER)
        with self.assertRaises(ValueError):
            self.advance(removed, [self.event(304, condition=conditions[2])], generated=LATER)

    def test_temporary_errors_retain_freshness_and_prior_availability(self):
        before = validate(self.base)['entries'][self.rid]
        for status, outcome, headers in [(None,'timeout',{}),(200,'truncated_response',{}),
                (429,'response',{}),(503,'response',{}),(403,'response',{'x-ratelimit-remaining':'0'})]:
            tree, _ = self.advance(self.base, [self.event(status, outcome=outcome, headers=headers)], generated=LATER)
            after = validate(tree)['entries'][self.rid]
            self.assertEqual(after['observation'], before['observation'])
            self.assertEqual(after['availability'], 'available')
        tree, _ = self.advance(None, [self.event(503)], generated=LATER)
        self.assertEqual(validate(tree)['entries'][self.rid]['availability'], 'unknown')

    def test_refusals_preserve_historical_body_without_serving_it(self):
        for status in (301,401,403,404,410):
            tree, _ = self.advance(self.base, [self.event(status)], generated=LATER)
            self.assertEqual(validate(tree)['entries'][self.rid]['availability'], 'unavailable')
            self.assertEqual(tree['bodies/'+self.rid+'.json'], self.base['bodies/'+self.rid+'.json'])
            again, _ = self.advance(tree, [self.event(503)], generated=LATER)
            self.assertEqual(validate(again)['entries'][self.rid]['availability'], 'unavailable')

    def test_public_shape_duplicate_keys_and_empty_list(self):
        for body in (b'{',b'{}',b'[NaN]',b'[{"id":1,"id":2}]',
                     b'[{"id":1,"tag_name":"v1","draft":true,"assets":[],"published_at":null}]'):
            tree, report = self.advance(self.base, [self.event(200, body=body)], generated=LATER)
            self.assertEqual(report[0]['outcome'], 'invalid_body')
            self.assertEqual(validate(tree)['entries'][self.rid]['availability'], 'unavailable')
        tree, _ = self.advance(self.base, [self.event(200,body=b' []\n')], generated=LATER)
        self.assertEqual(tree['bodies/'+self.rid+'.json'], b' []\n')

    def test_malformed_batch_is_atomic_and_does_not_mutate_inputs(self):
        original = copy.deepcopy(self.base)
        for mutation in ('duplicate','identity','future','out_of_order','condition','partial'):
            a = self.event(200,body=b'[]')
            if mutation=='identity': a['repository_id']=1
            if mutation=='future': a['response_completed_at']='2099-01-01T00:00:00+00:00'
            if mutation=='out_of_order': a['request_started_at']='2026-10-26T00:00:00+00:00'
            if mutation=='condition': a['condition']={'authorization':'secret'}
            if mutation=='partial': a.update(outcome='timeout',response_completed_at=None)
            batch = [a,a] if mutation=='duplicate' else [a]
            batch_before = copy.deepcopy(batch)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.advance(self.base,batch,generated=LATER)
            self.assertEqual(self.base,original)
            self.assertEqual(batch,batch_before)

    def test_removed_alias_tombstone_and_changed_descriptor_no_validators(self):
        m=json.loads(self.raw);m['sources'][0]['aliases']=[]
        tree,_=self.advance(self.base,[],raw=json.dumps(m).encode(),generated=LATER)
        self.assertFalse(validate(tree)['aliases'][self.alias]['active'])
        m=json.loads(self.raw);row=m['sources'][0]
        row['url']+='?page=2';row['request_id']=Descriptor(row['url']).request_id
        tree,_=self.advance(self.base,[],raw=json.dumps(m).encode(),generated=LATER)
        index=validate(tree)
        self.assertEqual(index['entries'][self.rid]['availability'],'retired')
        self.assertEqual(index['entries'][row['request_id']]['validators'],{})
        self.assertEqual(index['aliases'][self.alias]['request_id'],row['request_id'])

    def test_closed_tree_integrity_and_atomic_bounds(self):
        bad_cases=[{**self.base,'extra':b'x'}, {**self.base,'index.json':b'{}'},
                   {k:v for k,v in self.base.items() if k!='bodies/'+self.rid+'.json'}]
        for change in ('path','hash','time','manifest','schema'):
            tree=dict(self.base);index=decode(tree['index.json']);obs=index['entries'][self.rid]['observation']
            if change=='path':obs['path']='../outside'
            if change=='hash':obs['sha256']='0'*64
            if change=='time':obs['validated_at']='2099-01-01T00:00:00+00:00'
            if change=='manifest':index['manifest_sha256']='0'*64
            if change=='schema':index['schema_version']=2
            tree['index.json']=canonical(index);bad_cases.append(tree)
        for tree in bad_cases:
            with self.assertRaises(ValueError):validate(tree)
        for name,limit in [('INDEX_CAP',1),('TREE_CAP',1)]:
            with patch('storage.'+name,limit),self.assertRaises(ValueError):
                self.advance(self.base,[],generated=LATER)
        with self.assertRaises(ValueError):
            self.advance(None,[self.event(200,body=b'x'*8_000_001)],generated=LATER)

    def test_local_commits_pinned_reads_stale_parent_and_freshness(self):
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(['git','init','--quiet','--template=',directory],check=True)
            a=publish_local(directory,self.base,None)
            changed,_=self.advance(self.base,[self.event(200,body=b'[]\n')],generated=LATER)
            b=publish_local(directory,changed,a)
            old,_=lookup_local(directory,self.alias,a,now=LATER)
            new,_=lookup_local(directory,self.alias,b,now=LATER)
            self.assertNotEqual(old,new)
            with self.assertRaises(ValueError):publish_local(directory,changed,a)
            self.assertEqual(git(directory,'rev-parse','refs/heads/catalog').decode().strip(),b)
            obs=validate(self.base)['entries'][self.rid]['observation']
            edge=(datetime.fromisoformat(obs['validated_at'])+timedelta(seconds=86400)).isoformat()
            lookup_local(directory,self.alias,a,now=edge)
            later=(datetime.fromisoformat(edge)+timedelta(microseconds=1)).isoformat()
            with self.assertRaises(ValueError):lookup_local(directory,self.alias,a,now=later)
            consent=dict(commit=a,request_id=self.rid,sha256=obs['sha256'])
            lookup_local(directory,self.alias,a,now=later,stale_acceptance=consent)
            with self.assertRaises(ValueError):lookup_local(directory,self.alias,b,now='2026-10-29T00:00:00+00:00',stale_acceptance=consent)
            with self.assertRaises(ValueError):lookup_local(directory,self.alias,a,now='2026-10-26T00:00:00+00:00')
            git(directory,'remote','add','blocked','https://example.invalid/catalog')
            with self.assertRaises(ValueError):publish_local(directory,changed,b)


class WorkflowStorageIntegration(unittest.TestCase):
    setUpClass = classmethod(StorageContract.setUpClass.__func__)
    advance = classmethod(StorageContract.advance.__func__)
    # Run only the additional workflow-specific tests, sharing saved fixtures.
    def test_workflow_writes_validated_tree_and_retains_inert_evidence(self):
        from workflow_adapter import run
        raw=self.raw;ctx=dict(repository='mareklangiewicz/AM',repository_id='1291019762',
            event='workflow_dispatch',ref='refs/heads/main-marek',sha=REV,workflow_sha=REV,
            approved_revision=REV,run_id='1',run_attempt='1',manifest_sha256=digest(raw))
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'out'
            attempts=copy.deepcopy(self.attempts)
            with patch('workflow_adapter.SupervisedTransport'), patch('workflow_adapter.collect',
                    return_value=(attempts,{'complete':True})), patch('workflow_adapter.Clock.utcnow',
                    return_value=datetime.fromisoformat(GEN)):
                self.assertTrue(run(ctx,raw,REV,b'FIXTURE',output))
            tree={p.relative_to(output/'candidate').as_posix():p.read_bytes()
                  for p in (output/'candidate').rglob('*') if p.is_file()}
            validate(tree)
            self.assertEqual(attempts,self.attempts)
            self.assertEqual(json.loads((output/'storage-report.json').read_bytes())['outcome'],'validated_candidate')
            for attempt in attempts:
                self.assertEqual((output/(attempt['request_id']+'.body')).read_bytes(),attempt['body'])

    def test_workflow_retains_evidence_on_storage_refusal(self):
        from workflow_adapter import run
        raw=self.raw;ctx=dict(repository='mareklangiewicz/AM',repository_id='1291019762',
            event='workflow_dispatch',ref='refs/heads/main-marek',sha=REV,workflow_sha=REV,
            approved_revision=REV,run_id='1',run_attempt='1',manifest_sha256=digest(raw))
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'out'
            with patch('workflow_adapter.SupervisedTransport'),patch('workflow_adapter.collect',
                    return_value=(copy.deepcopy(self.attempts),{'complete':True})),patch('storage.apply',side_effect=ValueError('refusal')):
                self.assertFalse(run(ctx,raw,REV,b'FIXTURE',output))
            self.assertTrue((output/'report.json').is_file())
            self.assertFalse((output/'candidate').exists())

class ArtifactBoundary(unittest.TestCase):
    setUpClass = classmethod(StorageContract.setUpClass.__func__)
    advance = classmethod(StorageContract.advance.__func__)
    def test_candidate_directory_refuses_extra_symlink_and_executable(self):
        from artifact_io import read_candidate
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name,raw in self.base.items():
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
            self.assertEqual(read_candidate(root),self.base)
            extra=root/'extra';extra.write_bytes(b'x')
            with self.assertRaises(ValueError):read_candidate(root)
            extra.unlink();extra.symlink_to(root/'index.json')
            with self.assertRaises(ValueError):read_candidate(root)
            extra.unlink();(root/'index.json').chmod(0o755)
            with self.assertRaises(ValueError):read_candidate(root)


if __name__=='__main__':unittest.main()
