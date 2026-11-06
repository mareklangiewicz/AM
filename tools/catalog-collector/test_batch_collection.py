"""Real retained snapshots across bounded, partially failing collection runs."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

import host_catalog as collector
from publication import git, publish_tree
from retention import refresh
from yaml_publication import candidate_tree, load_local, schema_url, tree_documents

OLD = '2026-11-05T00:00:00Z'
NEW = '2026-11-06T00:00:00Z'
SCHEMA = schema_url('a'*40)
LIMITS = dict(max_files=1024, max_tree_bytes=1073741824, max_file_bytes=collector.FILE_CAP)


class BatchCollection(unittest.TestCase):
    def configuration(self, count=4):
        rows = [dict(app='app-'+str(i), repository_id=i, repository='owner/repo-'+str(i))
                for i in range(1, count+1)]
        return rows, {str(r['repository_id']): r['repository'] for r in rows}

    def previous(self, count=2):
        rows, _ = self.configuration(count)
        return {str(r['repository_id']): refresh(dict(format=2, schema=SCHEMA,
            repository_id=r['repository_id'], repository=r['repository']),
            [dict(received_at=OLD, releases={'123':dict(tag='v1',
                url='https://github.com/'+r['repository']+'/releases/tag/v1',
                published_at=OLD, prerelease=False, assets={})},
                bytes=2, seconds=0, has_next=False)],
            attempted_at=OLD) for r in rows}

    def collect(self, prior, read, *, size=2, count=4):
        with patch.object(collector, 'configuration', return_value=self.configuration(count)), \
                patch.object(collector, '_response', side_effect=read), \
                patch.object(collector, 'utc', return_value=NEW), \
                contextlib.redirect_stdout(io.StringIO()):
            return collector.collect('b'*40, prior, batch_size=size)

    def test_new_failure_does_not_advertise_app_and_untouched_bytes_survive_publication(self):
        previous = self.previous()
        original = copy.deepcopy(previous)
        calls = []
        def read(rid, evidence, allowance):
            calls.append(rid)
            return (b'[]' if rid == '3' else b'{invalid', NEW)
        tree, report = self.collect(previous, read)
        apps, repositories = tree_documents(tree, LIMITS)
        self.assertEqual(calls, ['3', '4'])
        self.assertEqual(previous, original)
        self.assertEqual(apps, {'app-1':1, 'app-2':2, 'app-3':3})
        self.assertEqual(repositories['4']['collection']['status'], 'failed')
        self.assertNotIn('last_success', repositories['4'])
        self.assertEqual([r['status'] for r in report], ['ok', 'failed'])
        old_tree = candidate_tree({'app-1':1, 'app-2':2}, previous,
            schema=SCHEMA, max_file_bytes=collector.FILE_CAP)
        for rid in ('1', '2'):
            self.assertEqual(tree['repositories/'+rid+'.yaml'], old_tree['repositories/'+rid+'.yaml'])
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            git(repo, 'init', '--bare', '--quiet', '--template=')
            parent = publish_tree(repo, old_tree, None)
            pin = publish_tree(repo, tree, parent)
            self.assertEqual(load_local(repo, pin, max_file_bytes=collector.FILE_CAP)[0], apps)
            self.assertEqual(load_local(repo, parent, max_file_bytes=collector.FILE_CAP)[0], {'app-1':1,'app-2':2})
        # Failed attempts move behind unattempted/older attempts, preventing a
        # broken source from repeatedly consuming the first slot.
        calls.clear()
        self.collect(repositories, read)
        self.assertEqual(calls, ['1', '2'])

    def test_existing_transport_failure_keeps_success_and_auth_failure_stops_requests(self):
        previous = self.previous(4)
        calls = []
        def read(rid, evidence, allowance):
            calls.append(rid)
            raise urllib.error.HTTPError('https://api.github.com/', 429, 'rate', {}, None)
        tree, report = self.collect(previous, read)
        apps, repositories = tree_documents(tree, LIMITS)
        self.assertEqual(calls, ['1'])
        self.assertEqual(len(apps), 4)
        for field in ('last_success', 'observed_at', 'releases'):
            self.assertEqual(repositories['1'][field], previous['1'][field])
        for rid in ('2', '3', '4'):
            self.assertEqual(repositories[rid], previous[rid])
        self.assertEqual(report[0]['reason'], 'transport')

    def test_128_source_enrollment_only_attempts_52_and_rejects_unsafe_scope(self):
        calls = []
        def read(rid, evidence, allowance):
            calls.append(rid)
            return b'[]', NEW
        tree, report = self.collect({}, read, size=52, count=128)
        apps, repositories = tree_documents(tree, LIMITS)
        self.assertEqual(calls, list(map(str, range(1, 53))))
        self.assertEqual(len(apps), 52)
        self.assertEqual(len(report), 52)
        for size in (0, 53, True):
            with self.assertRaisesRegex(ValueError, 'batch size'):
                self.collect({}, read, size=size)
        with self.assertRaisesRegex(ValueError, 'discard retained'):
            self.collect(self.previous(5), read)
        previous = self.previous()
        previous['1']['repository'] = 'different/source'
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            self.collect(previous, read)

    def test_total_response_budget_stops_without_touching_remaining_sources(self):
        previous = self.previous(4)
        calls = []
        def read(rid, evidence, allowance):
            calls.append((rid, allowance))
            return b'[]', NEW
        with patch.object(collector, 'TOTAL_CAP', 2):
            tree, report = self.collect(previous, read)
        _, repositories = tree_documents(tree, LIMITS)
        self.assertEqual(calls, [('1', 2)])
        self.assertEqual(repositories['2'], previous['2'])
        self.assertEqual(len(report), 1)

    def test_partial_transport_failures_cannot_bypass_the_shared_response_budget(self):
        previous = self.previous(4)
        class Reply:
            status = 200
            def __init__(self, request):
                self.url = request.full_url
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self, size):
                raise OSError('private upstream diagnostic must not be logged')
        output = io.StringIO()
        with patch.object(collector, 'configuration', return_value=self.configuration()), \
                patch.object(collector.urllib.request, 'urlopen', side_effect=lambda request, **kw: Reply(request)) as get, \
                patch.object(collector, 'utc', return_value=NEW), \
                patch.object(collector, 'TOTAL_CAP', 4), patch.object(collector, 'RESPONSE_CAP', 2), \
                contextlib.redirect_stdout(output):
            tree, report = collector.collect('b'*40, previous, batch_size=4)
        _, repositories = tree_documents(tree, LIMITS)
        self.assertEqual(get.call_count, 2)
        self.assertEqual([row['status'] for row in report], ['failed', 'failed'])
        self.assertGreater(sum(row['response_budget_charge'] for row in report), 4)
        self.assertEqual(repositories['3'], previous['3'])
        self.assertEqual(repositories['4'], previous['4'])
        self.assertNotIn('private upstream', output.getvalue())


if __name__ == '__main__':
    unittest.main()
