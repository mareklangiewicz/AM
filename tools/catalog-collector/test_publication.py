"""Current collection/publication contract, using only disposable local Git."""
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import host_catalog
import publication
from bounded import normalize
from retention import refresh
from test_yaml_reader import repository, SCHEMA
from yaml_publication import load_local, publish_local, schema_url


class Publication(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.repo = self.path/'catalog.git'
        self.repo.mkdir()
        publication.git(self.repo, 'init', '--bare', '--quiet', '--template=')

    def publish(self, parent=None, obj=None):
        return publish_local(self.repo, {'app':123}, {'123':obj or repository()},
            schema=SCHEMA, max_file_bytes=2097152, expected_parent=parent)

    def tip(self):
        return publication.git(self.repo, 'rev-parse', publication.REF).decode().strip()

    def test_pinned_round_trip_exact_parent_and_remote_refusal(self):
        first = self.publish()
        changed = copy.deepcopy(repository())
        changed['releases']['456']['tag'] = 'v3'
        second = self.publish(first, changed)
        self.assertEqual(load_local(self.repo, first, max_file_bytes=2097152)[1]['123'], repository())
        self.assertEqual(load_local(self.repo, second, max_file_bytes=2097152)[1]['123'], changed)
        with self.assertRaisesRegex(ValueError, 'stale_parent'):
            self.publish(first)
        self.assertEqual(self.tip(), second)
        publication.git(self.repo, 'remote', 'add', 'origin', 'https://example.invalid/no-network')
        with self.assertRaisesRegex(ValueError, 'remote_publication'):
            self.publish(second)
        self.assertEqual(self.tip(), second)

    def test_invalid_document_and_history_limit_leave_tip_unchanged(self):
        first = self.publish()
        bad = repository(); bad['unexpected'] = True
        with self.assertRaises(ValueError):
            self.publish(first, bad)
        with patch.object(publication, 'HISTORY_CAP', 1):
            with self.assertRaisesRegex(ValueError, 'history_bound'):
                self.publish(first)
        self.assertEqual(self.tip(), first)
        with self.assertRaisesRegex(ValueError, 'invalid_prior_pin'):
            load_local(self.repo, 'HEAD', max_file_bytes=2097152)
        with self.assertRaisesRegex(ValueError, 'yaml_prior_byte_bound'):
            load_local(self.repo, first, max_file_bytes=1)

    def test_git_environment_ignores_injected_repository_config_and_credentials(self):
        with patch.dict(os.environ, {'GIT_DIR':'/not-the-repository',
                'GIT_INDEX_FILE':'/not-the-index','GIT_CONFIG_COUNT':'1',
                'GIT_CONFIG_KEY_0':'core.bare','GIT_CONFIG_VALUE_0':'false',
                'GH_TOKEN':'secret','GIT_ASKPASS':'/not-a-command'}):
            first = self.publish()
            self.assertEqual(load_local(self.repo,first,max_file_bytes=2097152)[0],{'app':123})
            env = publication.environment()
            self.assertNotIn('GH_TOKEN', env)
            self.assertNotIn('GIT_ASKPASS', env)
            self.assertNotIn('GIT_DIR', env)
            self.assertEqual(env['GIT_TERMINAL_PROMPT'],'0')

    def test_bounded_process_refuses_output_time_and_nonzero_exit(self):
        env = publication.environment()
        for code,cap,seconds in [('print("too long")',2,5),
                ('import time; time.sleep(5)',100,.05),('raise SystemExit(9)',100,5)]:
            with self.subTest(code=code), self.assertRaisesRegex(ValueError,'delivery_command_refusal'):
                publication.bounded([sys.executable,'-c',code],env=env,cap=cap,seconds=seconds)
        self.assertEqual(publication.bounded([sys.executable,'-c','print("ok")'],
            env=env,cap=3),b'ok\n')

    def test_current_workflow_collection_publish_and_failure_preserves_previous(self):
        rows, sources = host_catalog.configuration()
        previous = {}
        evidence = self.path/'responses'; evidence.mkdir()
        now = '2026-11-05T20:00:00Z'
        for rid, name in sources.items():
            seed = dict(format=2,schema=schema_url('a'*40),repository_id=int(rid),repository=name)
            previous[rid] = refresh(seed,[dict(received_at=now,releases={},has_next=False,
                bytes=2,seconds=0)],attempted_at=now,max_catalog_bytes=2097152)
            (evidence/(rid+'-releases.json')).write_text('[]')
            (evidence/(rid+'-receipt.txt')).write_text(now)
        first = publish_local(self.repo,{r['app']:r['repository_id'] for r in rows},previous,
            schema=schema_url('a'*40),max_file_bytes=2097152,expected_parent=None)
        report = self.path/'report.json'
        args = ['host_catalog.py','--repo',str(self.repo),'--parent',first,
                '--evidence',str(evidence),'--report',str(report)]
        with patch.object(sys,'argv',args), patch('urllib.request.urlopen',side_effect=AssertionError('network')), redirect_stdout(io.StringIO()):
            host_catalog.main()
        second = self.tip()
        self.assertEqual(json.loads(report.read_text())['pin'],second)
        apps, observed = load_local(self.repo,second,max_file_bytes=2097152)
        self.assertEqual(len(apps),len(rows));self.assertEqual(set(observed),set(sources))
        (evidence/(next(iter(sources))+'-releases.json')).write_text('[invalid')
        args[args.index('--parent')+1]=second
        with patch.object(sys,'argv',args), redirect_stdout(io.StringIO()), self.assertRaises(ValueError):
            host_catalog.main()
        self.assertEqual(self.tip(),second)
        workflow = (host_catalog.ROOT/'.github/workflows/catalog.yml').read_text()
        self.assertIn('tools/catalog-collector/host_catalog.py',workflow)
        self.assertNotIn('--bootstrap',workflow)
