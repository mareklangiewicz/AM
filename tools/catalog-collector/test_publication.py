"""Current collection/publication contract, using only disposable local Git."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import publication

TREE = {'apps.yaml':b'apps', 'repositories/example.yaml':b'source'}


class Publication(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.repo = self.path/'catalog.git'
        self.repo.mkdir()
        publication.git(self.repo, 'init', '--bare', '--quiet', '--template=')

    def publish(self, parent=None, tree=TREE):
        return publication.publish_tree(self.repo, tree, parent)

    def show(self, commit, path):
        return publication.git(self.repo, 'show', commit+':'+path)

    def tip(self):
        return publication.git(self.repo, 'rev-parse', publication.REF).decode().strip()

    def test_pinned_round_trip_exact_parent_and_remote_refusal(self):
        first = self.publish()
        changed = dict(TREE, **{'repositories/example.yaml':b'changed'})
        second = self.publish(first, changed)
        self.assertEqual(self.show(first, 'repositories/example.yaml'), b'source')
        self.assertEqual(self.show(second, 'repositories/example.yaml'), b'changed')
        with self.assertRaisesRegex(ValueError, 'stale_parent'):
            self.publish(first)
        self.assertEqual(self.tip(), second)
        publication.git(self.repo, 'remote', 'add', 'origin', 'https://example.invalid/no-network')
        with self.assertRaisesRegex(ValueError, 'remote_publication'):
            self.publish(second)
        self.assertEqual(self.tip(), second)

    def test_delta_publication_reuses_blobs_and_exactly_replaces_tree(self):
        tree = {'apps.yaml':b'original', 'repositories/1.yaml':b'keep',
                'repositories/2.yaml':b'remove'}
        first = publication.publish_tree(self.repo, tree, None)
        replacement = {'apps.yaml':b'changed', 'repositories/1.yaml':b'keep',
                       'repositories/3.yaml':b'add'}
        with patch.object(publication, 'git', wraps=publication.git) as calls:
            second = publication.publish_tree(self.repo, replacement, first)
        writes = [call for call in calls.call_args_list
                  if call.args[1:4] == ('hash-object', '-w', '--stdin')]
        self.assertEqual(len(writes), 2)
        listing = publication.git(self.repo, 'ls-tree', '-r', '--name-only', second)
        self.assertEqual(set(listing.decode().splitlines()), set(replacement))
        for path, raw in replacement.items():
            self.assertEqual(publication.git(self.repo, 'show', second+':'+path), raw)
        with patch.object(publication, 'git', wraps=publication.git) as calls:
            third = publication.publish_tree(self.repo, replacement, second)
        self.assertFalse(any(call.args[1:4] == ('hash-object', '-w', '--stdin')
                             for call in calls.call_args_list))
        self.assertEqual(publication.git(self.repo,'rev-parse',third+'^{tree}'),
                         publication.git(self.repo,'rev-parse',second+'^{tree}'))
        self.assertEqual(publication.git(self.repo,'rev-parse',third+'^').decode().strip(),second)

    def test_history_limit_leaves_tip_unchanged(self):
        first = self.publish()
        with patch.object(publication, 'HISTORY_CAP', 1):
            with self.assertRaisesRegex(ValueError, 'history_bound'):
                self.publish(first)
        self.assertEqual(self.tip(), first)

    def test_history_guard_counts_compressed_growth_and_preserves_tip_on_overflow(self):
        publication.git(self.repo,'config','core.looseCompression','0')
        tree={'apps.yaml':b'a'*65536,'repositories/1.yaml':b'b'*65536}
        metrics={}
        with patch.object(publication,'HISTORY_CAP',32768):
            first=publication.publish_tree(self.repo,tree,None,metrics=metrics)
            self.assertGreater(metrics['snapshot_yaml_bytes'],metrics['history_cap'])
            self.assertLessEqual(metrics['history_object_bytes_after'],metrics['history_guard_bytes'])
            self.assertLessEqual(metrics['history_guard_bytes'],metrics['history_cap'])
            before=metrics['history_object_bytes_after']
            # A no-op tree reuses its blobs instead of charging them again.
            replay={}
            second=publication.publish_tree(self.repo,tree,first,metrics=replay)
            self.assertEqual(replay['new_blob_storage_upper_bound_bytes'],0)
            self.assertGreaterEqual(replay['history_object_bytes_after'],before)
            with self.assertRaisesRegex(ValueError,'history_bound'):
                publication.publish_tree(self.repo,dict(tree,**{'repositories/2.yaml':os.urandom(32768)}),second)
            self.assertEqual(self.tip(),second)
            # Even a faulty estimate cannot authorize an over-cap ref advance.
            with patch.object(publication.zlib,'compress',return_value=b''):
                with self.assertRaisesRegex(ValueError,'history_bound'):
                    publication.publish_tree(self.repo,dict(tree,**{'repositories/2.yaml':os.urandom(32768)}),second)
            self.assertEqual(self.tip(),second)

    def test_git_environment_ignores_injected_repository_config_and_credentials(self):
        with patch.dict(os.environ, {'GIT_DIR':'/not-the-repository',
                'GIT_INDEX_FILE':'/not-the-index','GIT_CONFIG_COUNT':'1',
                'GIT_CONFIG_KEY_0':'core.bare','GIT_CONFIG_VALUE_0':'false',
                'GH_TOKEN':'secret','GIT_ASKPASS':'/not-a-command'}):
            first = self.publish()
            self.assertEqual(self.show(first,'apps.yaml'),b'apps')
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

