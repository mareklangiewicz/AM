"""Offline run-context, artifact-directory and retained-state staging contract."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from collector import Refusal
from storage import canonical
from test_collector import Credential, FakeTransport, response
from test_yaml_adapter import ClockNow, ROOT
import test_yaml_enrollment as enrollment_tests
from yaml_publication import decode_document, git, publish_local
from writer import document
import yaml_staging as staging

REV = subprocess.check_output(['git','-C',str(ROOT),'rev-parse','d422860de']).decode().strip()
POLICY = (ROOT/'tools/catalog-collector/yaml-policy.json').read_bytes()


class Staging(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        enrollment_tests.Enrollment.setUpClass()
        cls.raw = enrollment_tests.Enrollment.raw
        cls.recipes = enrollment_tests.Enrollment.small_recipes

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.repo = Path(self.directory.name)/'git'
        self.repo.mkdir()
        git(self.repo,'init','--bare')
        self.output = Path(self.directory.name)/'artifact'
        self.scope = dict(sources=None,page_size=100,page_limit=1,reconcile=False)
        self.context = dict(repository='mareklangiewicz/AM',repository_id='1',
            event='workflow_dispatch',ref='refs/heads/main-marek',sha=REV,workflow_sha=REV,
            approved_revision=REV,run_id='10',run_attempt='1',previous_publication='',
            manifest_sha256=hashlib.sha256(self.raw).hexdigest(),
            yaml_policy_sha256=hashlib.sha256(POLICY).hexdigest(),
            yaml_scope_sha256=hashlib.sha256(canonical(self.scope)).hexdigest())
        self.limits = staging.policy(POLICY)
        self.calls = []

    def produce(self,scripts=()):
        clock = ClockNow()
        transport = FakeTransport(clock,scripts)
        def factory(value):
            self.calls.append(value)
            return transport
        return staging.collect_stage(self.context,self.raw,REV,POLICY,self.recipes,
            factory,clock,Credential(),self.output,repo=self.repo,**self.scope)

    def verified(self, tree=None, receipt=None):
        if tree is None:
            tree, receipt = staging.read_staged(self.output,self.limits)
        return staging.verify(tree,receipt,self.context,self.raw,REV,POLICY,self.recipes,repo=self.repo)

    def test_producer_directory_round_trip_without_ref_update(self):
        report = self.produce()
        tree, receipt = staging.read_staged(self.output,self.limits)
        self.assertEqual(set(tree),{'apps.yaml','repositories/262342594.yaml','repositories/16408992.yaml'})
        self.assertEqual(self.verified(tree,receipt),tree)
        self.assertEqual(report['sources'],{'262342594':'ok','16408992':'ok'})
        self.assertEqual(git(self.repo,'for-each-ref'),b'')
        self.assertEqual(self.output.stat().st_mode & 0o777,0o700)
        self.assertEqual(set(p.name for p in self.output.iterdir()),{'candidate','receipt.json'})

    def test_context_and_policy_hash_refuse_before_factory(self):
        for key,bad in (('approved_revision','a'*40),('yaml_policy_sha256','b'*64),
                        ('manifest_sha256','c'*64),('yaml_scope_sha256','d'*64)):
            before = self.context[key]
            self.context[key] = bad
            with self.subTest(key=key),self.assertRaises(ValueError):
                self.produce()
            self.context[key] = before
        self.assertEqual(self.calls,[])
        self.assertFalse(self.output.exists())

    def test_strict_policy_refusals(self):
        for raw in (b'{"max_files":1,"max_files":2}',b'{}',
                    canonical(dict(self.limits,max_file_bytes=True)),
                    canonical(dict(self.limits,run_seconds=301)),
                    canonical(dict(self.limits,max_tree_bytes=0))):
            with self.subTest(raw=raw),self.assertRaises(ValueError):
                staging.policy(raw)

    def test_wrong_artifact_context_pin_scope_and_schema_refuse(self):
        self.produce()
        tree, receipt = staging.read_staged(self.output,self.limits)
        for mutate in (
            lambda r:r['context'].update(run_id='11'),
            lambda r:r['scope'].update(page_limit='all'),
            lambda r:r['report'].update(previous_publication='a'*40),
            lambda r:r['report']['enrollment'].update(source_revision='a'*40)):
            record = json.loads(receipt)
            mutate(record)
            with self.assertRaises(ValueError):
                self.verified(tree,canonical(record))
        changed = {p:b.replace(REV.encode(),b'a'*40) for p,b in tree.items()}
        with self.assertRaisesRegex(Refusal,'unapproved_yaml_schema'):
            self.verified(changed,receipt)

    def test_bad_structure_or_cross_file_reference_refuses(self):
        self.produce()
        tree, receipt = staging.read_staged(self.output,self.limits)
        changed = dict(tree)
        changed['apps.yaml'] = changed['apps.yaml'].replace(b'16408992',b'123')
        with self.assertRaises(ValueError):
            self.verified(changed,receipt)
        changed = dict(tree, **{'../outside':b'bad'})
        with self.assertRaises(ValueError):
            self.verified(changed,receipt)
        changed = dict(tree)
        changed['repositories/123.yaml'] = changed.pop('repositories/16408992.yaml')
        with self.assertRaises(ValueError):
            self.verified(changed,receipt)

    def test_closed_artifact_refuses_symlink_executable_and_extra_paths(self):
        self.produce()
        extra = self.output/'extra'
        extra.write_bytes(b'bad')
        with self.assertRaises(ValueError):
            staging.read_staged(self.output,self.limits)
        extra.unlink()
        target = self.output/'candidate/apps.yaml'
        target.chmod(0o700)
        with self.assertRaises(ValueError):
            staging.read_staged(self.output,self.limits)
        target.chmod(0o600)
        other = self.output/'candidate/repositories/1.yaml'
        other.symlink_to(target)
        with self.assertRaises(ValueError):
            staging.read_staged(self.output,self.limits)

    def test_size_and_file_count_bounds(self):
        self.produce()
        for limits in (dict(self.limits,max_files=1),dict(self.limits,max_tree_bytes=1),
                       dict(self.limits,max_receipt_bytes=1),dict(self.limits,max_file_bytes=1)):
            with self.subTest(limits=limits),self.assertRaises(ValueError):
                staging.read_staged(self.output,limits)

    def test_partial_write_removes_output_directory(self):
        with patch('pathlib.Path.write_bytes',side_effect=OSError('fixture disk full')):
            with self.assertRaises(OSError):
                self.produce()
        self.assertFalse(self.output.exists())

    def test_incomplete_bootstrap_creates_no_artifact(self):
        with self.assertRaisesRegex(Refusal,'incomplete_bootstrap'):
            self.produce([response(status=429)])
        self.assertFalse(self.output.exists())

    def test_failed_and_unattempted_prior_facts_cannot_be_changed(self):
        import shutil
        self.produce()
        tree, _ = staging.read_staged(self.output,self.limits)
        apps = decode_document(tree['apps.yaml'],self.limits['max_file_bytes'])['apps']
        repositories = {p.split('/')[1][:-5]:decode_document(b,self.limits['max_file_bytes'])
                        for p,b in tree.items() if p != 'apps.yaml'}
        pin = publish_local(self.repo,apps,repositories,
            schema=repositories['16408992']['schema'],max_file_bytes=self.limits['max_file_bytes'],
            expected_parent=None)
        shutil.rmtree(self.output)
        self.context['previous_publication'] = pin
        self.scope['sources'] = ['262342594']
        self.context['yaml_scope_sha256'] = hashlib.sha256(canonical(self.scope)).hexdigest()
        self.produce([response(body=b'{')])
        tree, receipt = staging.read_staged(self.output,self.limits)
        self.verified(tree,receipt)
        for rid in ('262342594','16408992'):
            changed = dict(tree)
            path = 'repositories/'+rid+'.yaml'
            obj = decode_document(tree[path],self.limits['max_file_bytes'])
            obj['repository'] = 'changed/name'
            # Failure must preserve identity/facts as well as times.
            changed[path] = document(obj).encode()
            if rid == '16408992':
                with self.assertRaisesRegex(Refusal,'yaml_unattempted_changed'):
                    self.verified(changed,receipt)
            else:
                obj['observed_at'] = '2026-11-04T12:59:59Z'
                changed[path] = document(obj).encode()
                with self.assertRaises(ValueError):
                    self.verified(changed,receipt)

    def test_new_source_revision_preserves_unselected_document_bytes(self):
        self.produce()
        before, _ = staging.read_staged(self.output,self.limits)
        from yaml_publication import tree_documents
        apps, repositories = tree_documents(before,self.limits)
        pin = publish_local(self.repo,apps,repositories,schema=repositories['16408992']['schema'],
            max_file_bytes=self.limits['max_file_bytes'],expected_parent=None)
        revision = 'b'*40
        self.context.update(previous_publication=pin,sha=revision,workflow_sha=revision,
                            approved_revision=revision)
        cases = (('success',(),['262342594'],POLICY),
                 ('failed',(response(body=b'{'),),['262342594'],POLICY),
                 ('unattempted',(),None,canonical(dict(self.limits,max_run_requests=1))))
        for name,scripts,sources,policy_raw in cases:
            with self.subTest(case=name):
                self.scope['sources'] = sources
                self.context['yaml_scope_sha256'] = hashlib.sha256(canonical(self.scope)).hexdigest()
                self.context['yaml_policy_sha256'] = hashlib.sha256(policy_raw).hexdigest()
                limits = staging.policy(policy_raw)
                output = Path(self.directory.name)/('new-source-'+name)
                clock = ClockNow()
                staging.collect_stage(self.context,self.raw,revision,policy_raw,self.recipes,
                    lambda value:FakeTransport(clock,scripts),clock,Credential(),output,
                    repo=self.repo,**self.scope)
                tree, receipt = staging.read_staged(output,limits)
                self.assertEqual(tree['repositories/16408992.yaml'],before['repositories/16408992.yaml'])
                changed = decode_document(tree['repositories/262342594.yaml'],limits['max_file_bytes'])
                if name == 'failed':
                    original = decode_document(before['repositories/262342594.yaml'],limits['max_file_bytes'])
                    self.assertEqual({k:v for k,v in changed.items() if k != 'collection'},
                                     {k:v for k,v in original.items() if k != 'collection'})
                else:
                    self.assertIn(revision.encode(),tree['repositories/262342594.yaml'])
                self.assertEqual(staging.verify(tree,receipt,self.context,self.raw,revision,policy_raw,
                                               self.recipes,repo=self.repo),tree)

    def test_existing_output_is_preserved(self):
        self.output.mkdir()
        (self.output/'keep').write_bytes(b'keep')
        with self.assertRaisesRegex(Refusal,'yaml_output_exists'):
            self.produce()
        self.assertEqual((self.output/'keep').read_bytes(),b'keep')
        self.assertEqual(self.calls,[])


if __name__ == '__main__':
    unittest.main()
