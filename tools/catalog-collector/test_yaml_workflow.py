"""Offline proposal wiring: trusted preflight, scope, token handoff and job gates."""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import yaml
from storage import canonical
import yaml_workflow as workflow
from yaml_adapter import IncompleteBootstrap

ROOT = Path(__file__).resolve().parents[2]


class Workflow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        revision = subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
        raw = (ROOT/'docs/track/release-catalog/design/yaml-manifest.json').read_bytes()
        policy = (ROOT/'tools/catalog-collector/yaml-policy.json').read_bytes()
        self.scope = dict(sources=None,page_size=100,page_limit=1,reconcile=False)
        context = dict(repository='mareklangiewicz/AM',repository_id='1',event='workflow_dispatch',
            ref='refs/heads/main-marek',sha=revision,workflow_sha=revision,
            approved_revision=revision,run_id='10',run_attempt='1',previous_publication='',
            manifest_sha256=hashlib.sha256(raw).hexdigest(),
            yaml_policy_sha256=hashlib.sha256(policy).hexdigest(),
            yaml_scope_sha256=hashlib.sha256(canonical(self.scope)).hexdigest())
        self.env = {'CTX_'+k.upper():v for k,v in context.items()}
        self.env.update(RUNNER_TEMP=self.tmp.name,YAML_SCOPE_JSON=canonical(self.scope).decode(),
                        YAML_WORKFLOW_TOKEN='fixture-token',YAML_ARTIFACT_ID='42',
                        YAML_ARTIFACT_DIGEST='a'*64)

    def test_validate_without_token_or_network(self):
        self.env.pop('YAML_WORKFLOW_TOKEN')
        with patch('yaml_workflow.fetch_prior') as prior, patch('yaml_workflow.publish') as publish:
            self.assertEqual(workflow.run('validate',ROOT,self.env),0)
        prior.assert_not_called(); publish.assert_not_called()

    def test_invalid_scope_refuses_before_token_or_remote(self):
        bad_scopes = [dict(self.scope,page_size=True),dict(self.scope,page_limit=0),
            dict(self.scope,reconcile=True),dict(self.scope,sources=['missing']),
            dict(self.scope,sources='123'),dict(self.scope,sources=[])]
        for scope in bad_scopes:
            env = dict(self.env,YAML_SCOPE_JSON=canonical(scope).decode(),
                       CTX_YAML_SCOPE_SHA256=hashlib.sha256(canonical(scope)).hexdigest())
            with self.subTest(scope=scope),patch('yaml_workflow.fetch_prior') as prior:
                with self.assertRaises(ValueError):
                    workflow.run('collect',ROOT,env)
                prior.assert_not_called()
                self.assertIn('YAML_WORKFLOW_TOKEN',env)

    def test_collect_pins_prior_and_propagates_scope_outcomes(self):
        for report, expected in ((dict(sources={'1':'ok'},not_attempted_repositories=[]),0),
            (dict(sources={'1':'failed'},not_attempted_repositories=[]),1),
            (dict(sources={},not_attempted_repositories=['1']),1)):
            env = dict(self.env)
            with patch('yaml_workflow.fetch_prior') as prior, patch(
                    'yaml_workflow.collect_stage',return_value=report) as collect,patch('builtins.print'):
                self.assertEqual(workflow.run('collect',ROOT,env),expected)
            self.assertEqual(prior.call_args.args[-1],Path(self.tmp.name)/'yaml-prior')
            self.assertEqual(collect.call_args.kwargs,dict(repo=Path(self.tmp.name)/'yaml-prior',**self.scope))
            self.assertNotIn('YAML_WORKFLOW_TOKEN',env)
        with patch('yaml_workflow.fetch_prior'),patch('yaml_workflow.collect_stage',
                side_effect=IncompleteBootstrap({'reason':'fixture'})),patch('builtins.print'):
            self.assertEqual(workflow.run('collect',ROOT,dict(self.env)),1)

    def test_publish_forwards_trusted_artifact_outputs(self):
        with patch('yaml_workflow.publish') as publish:
            self.assertEqual(workflow.run('publish',ROOT,self.env),0)
        self.assertEqual(publish.call_args.args[-4:],('42','a'*64,b'fixture-token',
                                                     Path(self.tmp.name)/'yaml-publication'))
        self.assertNotIn('YAML_WORKFLOW_TOKEN',self.env)

    def test_inactive_proposal_permission_and_success_gates(self):
        proposal = ROOT/'docs/track/release-catalog/design/catalog-yaml-publication.yml.proposed'
        doc = yaml.load(proposal.read_text(),Loader=yaml.BaseLoader)
        self.assertEqual(set(doc['on']),{'workflow_dispatch'})
        self.assertEqual(doc['permissions'],{})
        collect,publish = doc['jobs']['collect'],doc['jobs']['publish']
        self.assertEqual(collect['permissions'],{'contents':'read'})
        self.assertEqual(publish['permissions'],{'contents':'write','actions':'read'})
        self.assertEqual(publish['needs'],'collect')
        self.assertNotIn('always()',publish['if'])
        self.assertEqual(collect['outputs']['artifact_digest'],'${{ steps.package.outputs.artifact-digest }}')
        for job in (collect,publish):
            self.assertEqual(job['steps'][0]['with']['persist-credentials'],'false')
            self.assertEqual(job['steps'][1]['run'],'python3 -B tools/catalog-collector/yaml_workflow.py validate')
            self.assertNotIn('env',job['steps'][1])
            for step in job['steps']:
                if 'run' in step:
                    self.assertTrue(step['run'].startswith('python3 -B tools/catalog-collector/yaml_workflow.py '))
                    self.assertNotIn('${{',step['run'])
        self.assertFalse((ROOT/'.github/workflows/catalog-yaml-publication.yml').exists())


if __name__ == '__main__':
    unittest.main()
