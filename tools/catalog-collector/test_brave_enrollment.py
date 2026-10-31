"""Eight-source candidate: genuine saved bytes, synthetic repeats, no HTTP."""
import copy
from datetime import datetime, timedelta
import io
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from collector import Descriptor, Refusal
from manifest import load_manifest
from storage import apply, canonical, digest, validate
from workflow_adapter import prepare, run
from delivery import unpack_artifact, verify_artifact, publish, read_git_tree, REMOTE_REF
from publication import git, publish_local
from reader import select, verify_body, StaleObservation
import test_delivery as delivery_tests
from test_shell_consumer import ShellFixture, PIN, epoch

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / 'docs/track/release-catalog/design'
RESEARCH = ROOT / 'docs/track/release-catalog/research'
RAW = (DESIGN / 'staged-manifest-brave.json').read_bytes()
ALIAS = 'https://api.github.com/repos/ivan-hc/Brave-appimage/releases'
REV = 'a' * 40  # synthetic source revision, not a rollout approval
GEN = '2026-10-31T22:15:00+00:00'
LATER = '2026-10-31T22:16:00+00:00'
PARENT = 'a113cd0aca3247111b6ba231f6a30b6477ac2c75'


def context(raw=RAW, prior=PARENT):
    return dict(repository='mareklangiewicz/AM', repository_id='1291019762',
                event='workflow_dispatch', ref='refs/heads/main-marek', sha=REV,
                workflow_sha=REV, approved_revision=REV, run_id='1', run_attempt='1',
                manifest_sha256=digest(raw), previous_publication=prior)


def retained_prior():
    raw = (RESEARCH / 'am-utils-live-20261031-evidence.tar.gz').read_bytes()
    assert digest(raw) == 'c95d6a6ca917e2153bdb3b094405578e3343514ee4052ff063b5b5eaf725ffc3'
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
        payload = archive.extractfile('collection.zip').read()
    assert digest(payload) == 'ebaf3218cd8d2e9621b4f11d5d5665795a2409fd79029b7627a088724b15d205'
    files = unpack_artifact(payload)
    tree = {p.removeprefix('candidate/'): raw for p, raw in files.items() if p.startswith('candidate/')}
    assert len(validate(tree)['entries']) == 7
    return tree


def initial_attempts(base):
    attempts = []
    for rid, entry in validate(base)['entries'].items():
        attempts.append(dict(request_id=rid, descriptor=entry['descriptor'],
            repository_id=entry['repository_id'], request_started_at=GEN,
            response_completed_at=GEN, attempt_finished_at=GEN, status=304,
            headers={}, body=b'', condition=entry['validators'], outcome='response'))
    evidence = RESEARCH / 'brave-release-20261031'
    report = json.loads((evidence / 'report.json').read_bytes())
    body = (evidence / 'body.json').read_bytes()
    assert report['accepted'] and digest(body) == report['body_sha256']
    attempts.append(dict(request_id=report['descriptor']['request_id'],
        descriptor={k: report['descriptor'][k] for k in ('url', 'api_version', 'accept')},
        repository_id=947512058, request_started_at=report['started_at'],
        response_completed_at=report['completed_at'], attempt_finished_at=GEN, status=200,
        headers=report['public_headers'], body=body, condition={}, outcome='response'))
    return attempts


class BraveEnrollment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = retained_prior()
        cls.raw = RAW
        cls.attempts = initial_attempts(cls.base)

    def files(self, attempts=None, prior=None, generated=GEN, ctx=None):
        attempts = self.attempts if attempts is None else attempts
        files, tree = delivery_tests.DeliveryContract.files(self, ctx or context(), self.base if prior is None else prior,
                                                         attempts, generated)
        for attempt in attempts:
            if attempt['outcome'] != 'response': files.pop(attempt['request_id'] + '.body', None)
        return files, tree

    def test_preserves_seven_and_plans_only_eighth_without_validators(self):
        seven = json.loads((DESIGN / 'staged-manifest-am-utils.json').read_bytes())
        self.assertEqual(json.loads(RAW)['sources'][:7], seven['sources'])
        plan = prepare(context(), RAW, REV, self.base)
        self.assertEqual(len(plan.requests), 8)
        self.assertTrue(all(r.condition for r in plan.requests[:7]))
        self.assertEqual(plan.requests[-1].condition, ())
        self.assertEqual(plan.requests[-1].source.aliases, (ALIAS,))
        bad = json.loads(RAW)
        row = copy.deepcopy(bad['sources'][-1]); row['url'] += '?page=2'
        row['request_id'] = Descriptor(row['url']).request_id; row['aliases'] = []
        bad['sources'].append(row); raw = canonical(bad)
        with patch('workflow_adapter.SupervisedTransport') as worker, patch('workflow_adapter.Token') as token:
            with self.assertRaises(Refusal):
                run(context(raw), raw, REV, b'FIXTURE', 'unused', previous_tree=self.base)
            worker.assert_not_called(); token.assert_not_called()
        self.assertEqual(len(load_manifest((DESIGN / 'staged-manifest-am-utils.json').read_bytes(), 1291019762).requests), 7)

    def test_first_eighth_304_and_failed_missing_invalid_results_refuse_publication(self):
        for kind in ('304', 'failure', 'missing', 'invalid', 'oversized'):
            attempts = copy.deepcopy(self.attempts)
            if kind == '304': attempts[-1].update(status=304, body=b'', headers={})
            elif kind == 'failure': attempts[-1].update(status=503, body=b'')
            elif kind == 'missing': attempts.pop()
            elif kind == 'invalid': attempts[-1]['body'] = b'{}'
            else: attempts[-1]['body'] = b'x' * 8_000_001
            with self.subTest(kind=kind):
                try:
                    files, tree = self.files(attempts)
                except ValueError:
                    continue
                for rid, entry in validate(self.base)['entries'].items():
                    self.assertEqual(tree[entry['observation']['path']], self.base[entry['observation']['path']])
                with self.assertRaises(ValueError): verify_artifact(files, context(), RAW, REV, self.base)

    def test_zip_recomputes_and_all_aliases_read_with_unchanged_bounds(self):
        files, tree = self.files()
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for path, raw in files.items(): archive.writestr(path, raw)
        self.assertEqual(verify_artifact(unpack_artifact(stream.getvalue()), context(), RAW, REV, self.base), tree)
        index = validate(tree)
        self.assertEqual(len(index['entries']), 8)
        for alias in index['aliases']:
            entry, _ = select(tree['index.json'], alias, PIN, now=GEN)
            verify_body(tree[entry['observation']['path']], entry)
        for rid, old in validate(self.base)['entries'].items():
            obs = index['entries'][rid]['observation']
            self.assertEqual(obs['received_at'], old['observation']['received_at'])
            self.assertEqual(obs['validated_at'], GEN)
        with patch('storage.TREE_CAP', sum(map(len, tree.values())) - 1), self.assertRaises(Refusal): self.files()
        with patch('storage.INDEX_CAP', 1), self.assertRaises(Refusal): self.files()
        bad = dict(files); bad['candidate/lookup.tsv'] += b'corrupt'
        with self.assertRaises(ValueError): verify_artifact(bad, context(), RAW, REV, self.base)

    def test_repeat_failure_preserves_age_and_wrong_conditions_refuse(self):
        _, tree = self.files(); entries = validate(tree)['entries']
        attempts = [dict(a, status=304, headers={}, body=b'', condition=entries[a['request_id']]['validators'],
                        request_started_at=LATER, response_completed_at=LATER, attempt_finished_at=LATER)
                    for a in self.attempts]
        files, repeated = self.files(attempts, tree, LATER)
        verify_artifact(files, context(), RAW, REV, tree)
        for rid, entry in entries.items():
            obs = validate(repeated)['entries'][rid]['observation']
            self.assertEqual(obs['received_at'], entry['observation']['received_at'])
            self.assertEqual(obs['validated_at'], LATER)
        bad = copy.deepcopy(attempts); bad[-1].update(status=None, outcome='timeout', response_completed_at=None)
        files, failed = self.files(bad, tree, LATER)
        rid = bad[-1]['request_id']
        self.assertEqual(validate(failed)['entries'][rid]['observation'], entries[rid]['observation'])
        with self.assertRaisesRegex(Refusal, 'incomplete_publication'): verify_artifact(files, context(), RAW, REV, tree)
        bad = copy.deepcopy(attempts); bad[-1]['condition'] = {}
        with self.assertRaises(ValueError): self.files(bad, tree, LATER)

    def test_local_publication_exact_parent_and_stale_parent_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); remote = root / 'remote.git'
            subprocess.run(['git', 'init', '--bare', '--quiet', '--template=', str(remote)], check=True)
            parent = publish_local(remote, self.base, None); git(remote, 'update-ref', REMOTE_REF, parent)
            ctx = context(prior=parent); files, tree = self.files(ctx=ctx)
            with patch('delivery.URL', str(remote)), patch('delivery.download_artifact', return_value=files):
                result = publish(ctx, RAW, REV, '1', 'a' * 64, b'FIXTURE', root / 'publish')
                self.assertEqual(result['parent'], parent)
                self.assertEqual(read_git_tree(remote, result['commit']), tree)
                with self.assertRaises(ValueError): publish(ctx, RAW, REV, '1', 'a' * 64, b'FIXTURE', root / 'stale')


class BraveShellReader(ShellFixture):
    @classmethod
    def setUpClass(cls):
        BraveEnrollment.setUpClass()
        helper = BraveEnrollment(); helper.base = BraveEnrollment.base; helper.raw = RAW; helper.attempts = BraveEnrollment.attempts
        _, cls.base = helper.files()
        cls.index = validate(cls.base)
        cls.rid = cls.index['aliases'][ALIAS]['request_id']
        cls.obs = cls.index['entries'][cls.rid]['observation']

    def test_brave_pinned_shell_exact_stale_consent_and_corruption(self):
        self.now = [epoch(GEN)] * 3; self.stage()
        def invoke(extra=()):
            return subprocess.run(['sh', str(ROOT / 'modules/catalog.am'), ALIAS, '--commit', PIN, *extra],
                                  env=self.env(), cwd=self.path, capture_output=True)
        result = invoke(); self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, (RESEARCH / 'brave-release-20261031/body.json').read_bytes())
        edge = datetime.fromisoformat(self.obs['validated_at']) + timedelta(hours=48)
        self.now = [epoch(edge.isoformat())] * 3; self.stage()
        self.assertEqual(invoke().returncode, 0)
        self.now = [epoch((edge + timedelta(seconds=1)).isoformat())] * 3; self.stage()
        self.assertNotEqual(invoke().returncode, 0)
        consent = ['--accept-stale', PIN, self.rid, self.obs['sha256']]
        self.assertEqual(invoke(consent).returncode, 0)
        self.assertNotEqual(invoke(['--accept-stale', 'c' * 40, self.rid, self.obs['sha256']]).returncode, 0)
        self.tree['bodies/' + self.rid + '.json'] = b'[]'; self.stage()
        self.assertNotEqual(invoke(consent).returncode, 0)


if __name__ == '__main__': unittest.main()
