"""Local-only legacy-to-shards delivery, artifact tamper and parent conflict."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import test_delivery as fixtures
from test_shards import fixture
from test_storage import REV, LATER
from storage import canonical, digest, validate
from shard_delivery import inventory, publish, read_shard
from publication import git, publish_local
from delivery import REMOTE_REF
from shards import root_index


class ShardDelivery(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.trees, _ = fixture()
        self.inv = dict(schema=1, shards={})
        for name, tree in self.trees.items():
            raw = validate(tree)['manifest_json'].encode()
            path = f'docs/track/release-catalog/research/appimage-next-large-batch-20261102/prepared/manifest-{name}.json'
            out = self.root/path; out.parent.mkdir(parents=True, exist_ok=True); out.write_bytes(raw)
            self.inv['shards'][name] = dict(path=path, sha256=digest(raw))
        self.raw = canonical(self.inv)
        self.remote = self.root/'remote.git'
        subprocess.run(['git','init','--bare','--quiet','--template=',str(self.remote)],check=True)
        self.parent = publish_local(self.remote, self.trees['00'], None)
        git(self.remote, 'update-ref', REMOTE_REF, self.parent)
        self.context = dict(repository='mareklangiewicz/AM',repository_id='1291019762',
            event='workflow_dispatch',ref='refs/heads/main-marek',sha=REV,workflow_sha=REV,
            approved_revision=REV,run_id='1',run_attempt='1',inventory_sha256=digest(self.raw),
            previous_publication=self.parent)
        self.files = {}
        for name, tree in self.trees.items():
            old = validate(tree)
            ctx = dict(self.context, manifest_sha256=digest(old['manifest_json'].encode()))
            if name != '00': ctx['previous_publication'] = ''
            attempts = [dict(request_id=rid, descriptor=entry['descriptor'], repository_id=entry['repository_id'],
                request_started_at=LATER, response_completed_at=LATER, attempt_finished_at=LATER,
                status=200, headers={}, body=tree[entry['observation']['path']], condition={}, outcome='response')
                for rid, entry in old['entries'].items()]
            helper = fixtures.DeliveryContract(); helper.raw = old['manifest_json'].encode()
            self.files[name], _ = helper.files(ctx, tree if name=='00' else None, attempts, LATER)
        self.artifacts = {name:dict(id=name, digest='a'*64) for name in self.trees}

    def run_publish(self, target, context=None):
        def download(ctx, artifact_id, sha, token, *, artifact_name):
            self.assertEqual(artifact_name, f'restricted-catalog-1-1-{artifact_id}')
            return self.files[artifact_id]
        with patch('shard_delivery.URL',str(self.remote)), patch('delivery.URL',str(self.remote)), \
                patch('shard_delivery.download_artifact',side_effect=download):
            return publish(context or self.context, self.raw, REV, self.root, self.artifacts,
                           b'FIXTURE', self.root/target)

    def test_legacy_bootstrap_exact_git_bytes_and_repeat(self):
        result = self.run_publish('first')
        self.assertEqual(git(self.remote,'rev-parse',REMOTE_REF).decode().strip(), result['commit'])
        self.assertEqual(git(self.remote,'show','-s','--format=%P',result['commit']).decode().strip(),self.parent)
        for name in self.trees:
            shard = read_shard(self.remote, result['commit'], name)
            self.assertEqual(set(validate(shard)['entries']),set(validate(self.trees[name])['entries']))
        # Reuse same-run fixture data with an updated exact parent and provenance.
        context = dict(self.context, previous_publication=result['commit'])
        for name, files in self.files.items():
            report = json.loads(files['report.json'])
            report['context']['previous_publication'] = result['commit']
            files['report.json'] = canonical(report)
        second = self.run_publish('second', context)
        self.assertEqual(second['parent'],result['commit'])

    def test_tamper_or_stale_parent_never_advances_remote(self):
        original = self.files['01']['candidate/index.json']
        self.files['01']['candidate/index.json'] = original+b' '
        with self.assertRaises(ValueError): self.run_publish('tampered')
        self.assertEqual(git(self.remote,'rev-parse',REMOTE_REF).decode().strip(),self.parent)
        self.files['01']['candidate/index.json'] = original
        self.run_publish('first')
        with self.assertRaisesRegex(ValueError,'publication_parent_changed'):
            self.run_publish('stale')

    def test_inventory_digest_path_and_alias_conflicts_refuse_before_transport(self):
        for mutation in ('digest', 'path', 'duplicate'):
            value = copy.deepcopy(self.inv)
            if mutation == 'digest': value['shards']['00']['sha256'] = 'b'*64
            if mutation == 'path': value['shards']['00']['path'] = '../escape'
            if mutation == 'duplicate':
                source = self.root/value['shards']['00']['path']
                target = self.root/value['shards']['01']['path']
                target.write_bytes(source.read_bytes())
                value['shards']['01']['sha256'] = digest(target.read_bytes())
            raw = canonical(value)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                inventory(dict(self.context, inventory_sha256=digest(raw)), raw, REV, self.root)
