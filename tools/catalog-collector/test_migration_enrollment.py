"""Offline seven-source preparation. Saved bodies; synthetic repeat events, no HTTP."""
import copy
from datetime import datetime, timedelta
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from collector import Descriptor, Refusal
from storage import apply, canonical, digest, validate
from manifest import load_manifest
from workflow_adapter import prepare, preflight, run
from reader import select, verify_body, StaleObservation
from delivery import unpack_artifact, verify_artifact, publish, read_git_tree, REMOTE_REF
from publication import git
import test_storage as saved
import test_delivery as delivery_tests
from test_shell_consumer import ShellFixture, PIN, epoch

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / 'docs/track/release-catalog/design'
EVIDENCE = ROOT / 'docs/track/release-catalog/research/am-utils-release-20261028'
RAW = (DESIGN / 'staged-manifest-am-utils.json').read_bytes()
ALIAS = 'https://api.github.com/repos/ivan-hc/am-utils/releases'
GEN = '2026-10-28T19:20:31+00:00'
LATER = '2026-10-28T19:21:31+00:00'
REV = saved.REV  # synthetic approved source revision in offline tests only


def context(raw=RAW, prior='b'*40):
    return dict(repository='mareklangiewicz/AM', repository_id='1291019762',
                event='workflow_dispatch', ref='refs/heads/main-marek', sha=REV,
                workflow_sha=REV, approved_revision=REV, run_id='1', run_attempt='1',
                manifest_sha256=digest(raw), previous_publication=prior)


def initial_attempts(base):
    # Prior six observations are genuine retained baseline bytes. Repeat 304s
    # and their times are test events, never claimed as real upstream responses.
    attempts = []
    for rid, entry in validate(base)['entries'].items():
        attempts.append(dict(request_id=rid, descriptor=entry['descriptor'],
            repository_id=entry['repository_id'], request_started_at=GEN,
            response_completed_at=GEN, attempt_finished_at=GEN, status=304,
            headers={}, body=b'', condition=entry['validators'], outcome='response'))
    report = json.loads((EVIDENCE / 'report.json').read_bytes())
    body = (EVIDENCE / 'body.json').read_bytes()
    assert digest(body) == report['body_sha256']
    row = json.loads(RAW)['sources'][-1]
    attempts.append(dict(request_id=row['request_id'],
        descriptor={k: report['descriptor'][k] for k in ('url','api_version','accept')},
        repository_id=row['repository_id'], request_started_at=report['started_at'],
        response_completed_at=report['completed_at'], attempt_finished_at=GEN,
        status=200, headers=report['public_headers'], body=body, condition={}, outcome='response'))
    return attempts


def advance(prior, attempts, generated=GEN):
    return apply(prior, RAW, attempts, workflow_identity=1291019762,
                 generated_at=generated, revision=REV, run={'id':'1','attempt':'1'})


class MigrationEnrollment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        saved.StorageContract.setUpClass()
        cls.base = saved.StorageContract.base
        cls.six_raw = saved.StorageContract.raw
        cls.raw = RAW
        cls.attempts = initial_attempts(cls.base)

    def files(self, attempts=None, generated=GEN, prior=None):
        return delivery_tests.DeliveryContract.files(self, context(), self.base if prior is None else prior,
                                      self.attempts if attempts is None else attempts, generated)

    def test_exact_six_preserved_seven_planned_and_eighth_refused(self):
        six = json.loads(self.six_raw)
        seven = json.loads(RAW)
        self.assertEqual(seven['sources'][:6], six['sources'])
        self.assertEqual(len(load_manifest(self.six_raw,1291019762).requests),6)
        value = prepare(context(),RAW,REV,self.base)
        self.assertEqual(len(value.requests),7)
        self.assertTrue(all(r.condition for r in value.requests[:6]))
        self.assertEqual(value.requests[-1].condition,())
        self.assertEqual(value.requests[-1].source.aliases,(ALIAS,))
        for count in (5,8):
            bad = copy.deepcopy(seven)
            if count == 5:
                bad['sources'] = bad['sources'][:5]
            else:
                row=copy.deepcopy(bad['sources'][-1])
                row['url'] += '?page=2'
                row['request_id']=Descriptor(row['url']).request_id
                row['aliases']=[]
                bad['sources'].append(row)
            raw=canonical(bad)
            with self.subTest(count=count), patch('workflow_adapter.SupervisedTransport') as worker, patch('workflow_adapter.Token') as token:
                with self.assertRaises(Refusal):
                    run(context(raw),raw,REV,b'FIXTURE','unused')
                worker.assert_not_called()
                token.assert_not_called()
        # The old manifest hash cannot approve the seventh-source candidate.
        with self.assertRaisesRegex(Refusal,'unapproved_manifest'):
            preflight(context(self.six_raw),RAW,REV)

    def test_first_observation_keeps_old_bodies_and_readers_remain_pinned(self):
        before=validate(self.base)
        tree, transitions=advance(self.base, self.attempts)
        after=validate(tree)
        self.assertEqual([t['outcome'] for t in transitions].count('validated'),6)
        self.assertEqual(transitions[-1]['outcome'],'observed')
        for rid,old in before['entries'].items():
            new=after['entries'][rid]
            self.assertEqual(new['availability'],'available')
            self.assertEqual(new['observation']['received_at'],old['observation']['received_at'])
            self.assertEqual(new['observation']['validated_at'],GEN)
            self.assertEqual(tree[old['observation']['path']],self.base[old['observation']['path']])
        for alias in after['aliases']:
            entry,meta=select(tree['index.json'],alias,PIN,now=GEN)
            self.assertEqual(verify_body(tree[entry['observation']['path']],entry),
                             tree[entry['observation']['path']])
        entry,_=select(tree['index.json'],ALIAS,PIN,now=GEN)
        self.assertEqual(verify_body((EVIDENCE/'body.json').read_bytes(),entry),self.attempts[-1]['body'])
        bad=copy.deepcopy(entry);bad['observation']['sha256']='0'*64
        with self.assertRaises(Refusal):verify_body(self.attempts[-1]['body'],bad)
        edge=(datetime.fromisoformat(entry['observation']['validated_at'])+timedelta(hours=48)).isoformat()
        select(tree['index.json'],ALIAS,PIN,now=edge)
        stale=(datetime.fromisoformat(edge)+timedelta(microseconds=1)).isoformat()
        with self.assertRaises(StaleObservation) as refusal:
            select(tree['index.json'],ALIAS,PIN,now=stale)
        select(tree['index.json'],ALIAS,PIN,now=stale,stale_acceptance=refusal.exception.acceptance)
        with self.assertRaises(StaleObservation):
            select(tree['index.json'],ALIAS,'c'*40,now=stale,stale_acceptance=refusal.exception.acceptance)

    def test_workflow_stages_seven_artifacts_without_replacing_operational_manifest(self):
        operational=(DESIGN/'staged-manifest.json').read_bytes()
        self.assertEqual(operational,self.six_raw)
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'out'
            with patch('workflow_adapter.SupervisedTransport'), patch('workflow_adapter.collect',
                    return_value=(copy.deepcopy(self.attempts),{'complete':True})), patch('workflow_adapter.Clock.utcnow',
                    return_value=datetime.fromisoformat(GEN)):
                self.assertTrue(run(context(),RAW,REV,b'FIXTURE',output,previous_tree=self.base))
            files={p.relative_to(output).as_posix():p.read_bytes() for p in output.rglob('*') if p.is_file()}
            expected,_=advance(self.base,self.attempts)
            self.assertEqual(verify_artifact(files,context(),RAW,REV,self.base),expected)
        self.assertEqual((DESIGN/'staged-manifest.json').read_bytes(),operational)

    def test_new_failure_retains_six_and_is_not_publishable(self):
        for kind in ('failure','invalid','missing'):
            attempts=copy.deepcopy(self.attempts)
            if kind=='missing':attempts.pop()
            elif kind=='failure':attempts[-1].update(status=503,body=b'')
            else:attempts[-1]['body']=b'{}'
            files,tree=self.files(attempts)
            after=validate(tree)
            for rid,entry in validate(self.base)['entries'].items():
                self.assertEqual(tree[entry['observation']['path']],self.base[entry['observation']['path']])
                self.assertTrue(after['aliases'][entry['descriptor']['url']]['active'])
            with self.subTest(kind=kind),self.assertRaisesRegex(Refusal,'incomplete_publication'):
                verify_artifact(files,context(),RAW,REV,self.base)

    def test_repeat_304_and_failure_do_not_invent_receipt_or_validation(self):
        tree,_=advance(self.base,self.attempts)
        entries=validate(tree)['entries']
        attempts=[]
        for a in self.attempts:
            entry=entries[a['request_id']]
            attempts.append({**a,'status':304,'headers':{},'body':b'',
                'condition':entry['validators'],'request_started_at':LATER,
                'response_completed_at':LATER,'attempt_finished_at':LATER})
        repeated,_=advance(tree,attempts,LATER)
        for rid,entry in entries.items():
            now=validate(repeated)['entries'][rid]['observation']
            self.assertEqual(now['received_at'],entry['observation']['received_at'])
            self.assertEqual(now['validated_at'],LATER)
        failed=copy.deepcopy(attempts)
        failed[-1].update(status=None,outcome='timeout',response_completed_at=None)
        candidate,_=advance(tree,failed,LATER)
        rid=attempts[-1]['request_id']
        self.assertEqual(validate(candidate)['entries'][rid]['observation'],entries[rid]['observation'])
        for mutation in ('condition','descriptor','oversized'):
            bad=copy.deepcopy(attempts)
            if mutation=='condition':bad[-1]['condition']={}
            elif mutation=='descriptor':bad[-1]['descriptor']['url']+='?page=2'
            else:bad[-1].update(status=200,body=b'x'*8_000_001)
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):advance(tree,bad,LATER)

    def test_zip_recomputation_local_publication_and_unchanged_bounds(self):
        files,tree=self.files()
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED) as archive:
            for path,raw in files.items():archive.writestr(path,raw)
        unpacked=unpack_artifact(stream.getvalue())
        self.assertEqual(verify_artifact(unpacked,context(),RAW,REV,self.base),tree)
        # Byte bound still refuses, including when seven valid sources fit counts.
        with patch('storage.TREE_CAP',sum(map(len,tree.values()))-1),self.assertRaises(Refusal):
            advance(self.base,self.attempts)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);remote=root/'remote.git'
            subprocess.run(['git','init','--bare','--quiet','--template=',str(remote)],check=True)
            # Seed the exact old six-source tree locally, then use the real
            # publisher with its network boundary directed to a temporary bare repo.
            from publication import publish_local
            parent=publish_local(remote,self.base,None)
            git(remote,'update-ref',REMOTE_REF,parent)
            ctx=context(prior=parent)
            report=json.loads(files['report.json']);report['context']=ctx
            files['report.json']=canonical(report)
            with patch('delivery.URL',str(remote)),patch('delivery.download_artifact',return_value=files):
                result=publish(ctx,RAW,REV,'1','a'*64,b'FIXTURE',root/'publish')
            self.assertEqual(result['parent'],parent)
            self.assertEqual(read_git_tree(remote,parent),self.base)
            self.assertEqual(read_git_tree(remote,result['commit']),tree)
            with patch('delivery.URL',str(remote)),self.assertRaises(ValueError):
                publish(ctx,RAW,REV,'1','a'*64,b'FIXTURE',root/'stale')


class MigrationShellReader(ShellFixture):
    @classmethod
    def setUpClass(cls):
        MigrationEnrollment.setUpClass()
        cls.base,_=advance(MigrationEnrollment.base,MigrationEnrollment.attempts)
        cls.index=validate(cls.base)
        cls.rid=cls.index['aliases'][ALIAS]['request_id']
        cls.obs=cls.index['entries'][cls.rid]['observation']

    def test_seventh_alias_on_real_shell_reader_exact_stale_and_corruption(self):
        self.now=[epoch(GEN)]*3
        self.stage()
        # ShellFixture.invoke uses the original Obsidian alias; invoke the new
        # alias directly with the same controlled HTTP/clock fixtures.
        helper=ROOT/'modules/catalog.am'
        def invoke(extra=()):
            return subprocess.run(['sh',str(helper),ALIAS,'--commit',PIN,*extra],
                                  env=self.env(),cwd=self.path,capture_output=True)
        result=invoke();self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,(EVIDENCE/'body.json').read_bytes())
        self.now=[epoch('2026-10-30T19:20:31+00:00')]*3
        self.stage()
        result=invoke();self.assertNotEqual(result.returncode,0)
        result=invoke(['--accept-stale',PIN,self.rid,self.obs['sha256']])
        self.assertEqual(result.returncode,0,result.stderr)
        self.tree['bodies/'+self.rid+'.json']=b'[]';self.stage()
        self.assertNotEqual(invoke(['--accept-stale',PIN,self.rid,self.obs['sha256']]).returncode,0)


if __name__=='__main__':unittest.main()
