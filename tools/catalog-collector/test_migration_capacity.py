"""52-source offline contract, actual bodies and explicitly synthetic repeats."""
import copy
import io
import json
from pathlib import Path
import unittest
import subprocess
import tempfile
from unittest.mock import patch
import zipfile

from collector import Descriptor, Refusal
from identity_batch import ROOT
from storage import apply, canonical, digest, validate, TREE_CAP
from manifest import load_manifest
from delivery import verify_artifact, unpack_artifact, ZIP_CAP, read_git_tree
from publication import publish_local, git
from workflow_adapter import prepare
from reader import select, verify_body
from shell_lookup import epoch
from test_shell_consumer import ShellFixture, PIN
from test_brave_migration import accepted_brave_tree
import test_delivery as delivery_fixture
import test_collector as collector_fixture

DIRECTORY=ROOT/'docs/track/release-catalog/research/appimage-batch-20261102'
RAW=(DIRECTORY/'candidate-manifest.json').read_bytes()
GEN='2026-11-02T11:20:00+00:00'
LATER='2026-11-02T11:21:00+00:00'
REV='a'*40


def context(raw=RAW):
    return dict(repository='mareklangiewicz/AM',repository_id='1291019762',
                event='workflow_dispatch',ref='refs/heads/main-marek',sha=REV,
                workflow_sha=REV,approved_revision=REV,run_id='1',run_attempt='1',
                manifest_sha256=digest(raw),previous_publication='b'*40)


def initial_attempts(base):
    attempts=[]
    for rid,entry in validate(base)['entries'].items():
        attempts.append(dict(request_id=rid, descriptor=entry['descriptor'],
                             repository_id=entry['repository_id'],request_started_at=GEN,
                             response_completed_at=GEN,attempt_finished_at=GEN,status=304,
                             headers={},body=b'',condition=entry['validators'],outcome='response'))
    for row in json.loads((DIRECTORY/'batch.json').read_bytes())['releases']:
        if not row['accepted']: continue
        directory=ROOT/row['evidence'];r=json.loads((directory/'report.json').read_bytes())
        body=(directory/'body.json').read_bytes()
        assert digest(body)==r['body_sha256'] and digest((directory/'headers.txt').read_bytes())==r['headers_sha256']
        attempts.append(dict(request_id=r['descriptor']['request_id'],
                             descriptor={k:r['descriptor'][k] for k in ('url','api_version','accept')},
                             repository_id=row['repository_id'],request_started_at=r['started_at'],
                             response_completed_at=r['completed_at'],attempt_finished_at=GEN,
                             status=200,headers=r['public_headers'],body=body,condition={},outcome='response'))
    return attempts


def files(base, attempts, generated=GEN):
    helper=delivery_fixture.DeliveryContract();helper.raw=RAW
    artifact,tree=helper.files(context(),base,attempts,generated)
    for attempt in attempts:
        if attempt['outcome'] != 'response':
            artifact.pop(attempt['request_id']+'.body',None)
    return artifact,tree


class MigrationCapacity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=accepted_brave_tree()
        cls.attempts=initial_attempts(cls.base)

    def test_preserves_all_eight_and_refuses_unreviewed_53_before_credentials(self):
        manifest=json.loads(RAW)
        self.assertEqual(manifest['sources'][:8],json.loads(validate(self.base)['manifest_json'])['sources'])
        value=prepare(context(),RAW,REV,self.base)
        self.assertEqual(len(value.requests),52)
        self.assertTrue(all(r.condition for r in value.requests[:8]))
        self.assertTrue(all(not r.condition for r in value.requests[8:]))
        new=copy.deepcopy(manifest['sources'][-1]);new['url']+='?page=2'
        new['request_id']=Descriptor(new['url']).request_id;new['aliases']=[]
        manifest['sources'].append(new);raw=canonical(manifest)
        with patch('workflow_adapter.SupervisedTransport') as transport, patch('workflow_adapter.Token') as token:
            with self.assertRaises(ValueError): prepare(context(raw),raw,REV,self.base)
            transport.assert_not_called();token.assert_not_called()

    def test_full_tree_artifact_recomputation_and_every_reference_reader(self):
        artifact,tree=files(self.base,self.attempts)
        self.assertEqual(verify_artifact(artifact,context(),RAW,REV,self.base),tree)
        self.assertLess(sum(map(len,tree.values())),TREE_CAP)
        index=validate(tree)
        self.assertEqual(len(index['entries']),52)
        for alias in index['aliases']:
            entry,_=select(tree['index.json'],alias,PIN,now=GEN)
            self.assertEqual(verify_body(tree[entry['observation']['path']],entry),tree[entry['observation']['path']])
        output=io.BytesIO()
        with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as archive:
            for path,raw in artifact.items(): archive.writestr(path,raw)
        self.assertLess(len(output.getvalue()),ZIP_CAP)
        self.assertEqual(unpack_artifact(output.getvalue()),artifact)

    def test_local_git_parent_exact_tree_and_stale_parent_refusal(self):
        _,tree=files(self.base,self.attempts)
        with tempfile.TemporaryDirectory() as directory:
            remote=Path(directory)/'remote.git'
            subprocess.run(['git','init','--bare','--quiet','--template=',str(remote)],check=True)
            parent=publish_local(remote,self.base,None)
            commit=publish_local(remote,tree,parent)
            self.assertEqual(git(remote,'show','-s','--format=%P',commit).decode().strip(),parent)
            self.assertEqual(read_git_tree(remote,commit),tree)
            with self.assertRaisesRegex(Refusal,'stale_parent'):
                publish_local(remote,tree,parent)

    def test_failed_new_source_refuses_and_repeat_preserves_age(self):
        artifact,tree=files(self.base,self.attempts)
        entries=validate(tree)['entries']
        repeated=[dict(a,status=304,headers={},body=b'',condition=entries[a['request_id']]['validators'],
                       request_started_at=LATER,response_completed_at=LATER,attempt_finished_at=LATER)
                  for a in self.attempts]
        artifact,repeated_tree=files(tree,repeated,LATER)
        self.assertEqual(verify_artifact(artifact,context(),RAW,REV,tree),repeated_tree)
        for rid,entry in entries.items():
            self.assertEqual(validate(repeated_tree)['entries'][rid]['observation']['received_at'],entry['observation']['received_at'])
        repeated[-1].update(status=None,outcome='timeout',response_completed_at=None)
        artifact,failed=files(tree,repeated,LATER)
        self.assertEqual(validate(failed)['entries'][repeated[-1]['request_id']]['observation'],entries[repeated[-1]['request_id']]['observation'])
        with self.assertRaisesRegex(Refusal,'incomplete_publication'):
            verify_artifact(artifact,context(),RAW,REV,tree)

    def test_52_fast_requests_fit_and_slow_batch_stops_at_unchanged_300_seconds(self):
        value=collector_fixture.plan(collector_fixture.sources(52),1)
        clock=collector_fixture.Clock()
        transport=collector_fixture.FakeTransport(clock,[])
        attempts,report=collector_fixture.collect(value,transport,clock,object(),workflow_identity=1)
        self.assertEqual(len(attempts),52)
        self.assertTrue(report['complete'])
        self.assertEqual(report['elapsed_seconds'],52)
        self.assertTrue(all(limits.batch_deadline==300 for _,limits in transport.calls))
        # A 10-second/request batch reaches 300 seconds before all 52 complete.
        clock=collector_fixture.Clock()
        transport=collector_fixture.FakeTransport(clock,[collector_fixture.response(delay=10)]*52)
        attempts,report=collector_fixture.collect(value,transport,clock,object(),workflow_identity=1)
        self.assertFalse(report['complete'])
        self.assertEqual(report['stop_reason'],'batch_deadline')
        self.assertLess(len(attempts),52)


class MigrationCapacityShell(ShellFixture):
    @classmethod
    def setUpClass(cls):
        base=accepted_brave_tree()
        _,cls.base=files(base,initial_attempts(base))
        cls.index=validate(cls.base)
        cls.rid=next(iter(cls.index['entries']))
        cls.obs=cls.index['entries'][cls.rid]['observation']

    def test_all_44_new_aliases_through_real_pinned_shell_reader(self):
        import subprocess
        self.now=[epoch(GEN)]*3
        self.stage()
        for row in json.loads((DIRECTORY/'batch.json').read_bytes())['releases']:
            if not row['accepted']: continue
            with self.subTest(alias=row['alias']):
                (self.path/'calls').write_text('')
                result=subprocess.run(['sh',str(ROOT/'modules/catalog.am'),row['alias'],'--commit',PIN],
                                      env=self.env(),cwd=self.path,capture_output=True)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual(result.stdout.rstrip(b'\n'),(ROOT/row['evidence']/'body.json').read_bytes().rstrip(b'\n'))


if __name__=='__main__':unittest.main()
