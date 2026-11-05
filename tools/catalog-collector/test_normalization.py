#!/usr/bin/env python3
"""Acceptance for offline bounded JSON acquisition and normalization."""
import json
import pathlib
import tempfile
import time
import unittest
from bounded import FixtureBudget, collect_files, normalize
from test_yaml_reader import Experiment, repository

ATTEMPT = '2026-11-04T00:00:00Z'


def release(rid=457):
    return dict(id=rid, draft=False, tag_name='v3', name='café\n\u2028',
                html_url='https://github.com/example/app/releases/tag/v3',
                published_at='2026-11-03T00:00:00Z', prerelease=True,
                assets=[dict(id=790, name='app', browser_download_url='https://example.com/app',
                             size=0, content_type='', digest=None)])


class Bounded(unittest.TestCase):
    accepted = Experiment.accepted
    run_reader = Experiment.run_reader

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.old = repository()
        self.n = 0

    def page(self, raw=None, text=None, next=False):
        self.n += 1
        path = pathlib.Path(self.directory.name) / str(self.n)
        path.write_bytes(text if text is not None else json.dumps(raw if raw is not None else [release()], ensure_ascii=False).encode())
        return dict(path=path, has_next=next)

    def collect(self, pages, **kw):
        result = collect_files(self.old, pages, attempted_at=ATTEMPT, **kw)
        self.accepted(result)
        return result

    def rollback(self, result, reason):
        self.assertEqual(result['collection']['reason'], reason)
        for field in ('releases', 'last_success', 'observed_at'):
            self.assertEqual(result[field], self.old[field])

    def test_normalize_merge_and_finite_scope_is_lazy(self):
        good = self.page(next=True)
        result = self.collect([good, dict(path='/does/not/exist', has_next=False)])
        self.assertEqual(result['collection']['status'], 'ok')
        self.assertEqual(result['releases']['456'], self.old['releases']['456'])
        self.assertEqual(result['releases']['457']['title'], 'café\n\u2028')
        self.assertNotIn('digest', result['releases']['457']['assets']['790'])
        self.assertFalse(result['last_success']['history_complete'])

    def test_failures_after_first_page_rollback(self):
        first = self.page(next=True)
        cases = [self.page(text=b'{'), self.page(text=b'[{"id":1,"id":2}]'),
                 self.page(raw=[release(), release()]), self.page(text=b'\xff'),
                 dict(path='/does/not/exist', has_next=False)]
        for bad in cases:
            result = self.collect([first, bad], page_limit='all')
            self.rollback(result, 'transport' if str(bad['path']) == '/does/not/exist' else 'invalid_response')

    def test_request_and_byte_limits(self):
        first = self.page(next=True)
        second = self.page(raw=[release(458)])
        budget = FixtureBudget(requests=1)
        self.rollback(self.collect([first, second], page_limit='all', budget=budget), 'collection_limit')
        self.assertEqual(budget.used_requests, 1)
        size = first['path'].stat().st_size
        for budget in (FixtureBudget(response_bytes=size-1), FixtureBudget(total_bytes=size-1)):
            self.rollback(self.collect([first], budget=budget), 'collection_limit')
            self.assertEqual(budget.used_bytes, size)  # At most one detection byte.
        result = self.collect([first], budget=FixtureBudget(response_bytes=size, total_bytes=size))
        self.assertEqual(result['collection']['status'], 'ok')
        budget = FixtureBudget(total_bytes=size)
        self.rollback(self.collect([first, second], page_limit='all', budget=budget), 'collection_limit')
        self.assertEqual(budget.used_bytes, size+1)

    def test_elapsed_and_catalog_limits(self):
        page = self.page()
        budget = FixtureBudget(seconds=0.001)
        time.sleep(0.005)
        self.rollback(self.collect([page], budget=budget), 'collection_limit')
        self.assertEqual(budget.used_requests, 0)
        self.rollback(self.collect([page], max_catalog_bytes=1), 'collection_limit')
        self.rollback(self.collect([page], max_line_bytes=20), 'collection_limit')

    def test_reconciliation_and_drafts(self):
        draft = release(); draft['draft'] = True
        result = self.collect([self.page(raw=[draft])])
        self.assertEqual(result['releases'], self.old['releases'])
        result = self.collect([self.page(raw=[])], page_limit='all', reconcile=True)
        self.assertEqual(result['releases'], {})
        with self.assertRaises(ValueError):
            self.collect([], reconcile=True)

    def test_reject_unrepresentable_and_wrong_types(self):
        for key, value in [('id', True), ('id', 2**63), ('prerelease', 1),
                           ('published_at', '2026-02-30T00:00:00Z'),
                           ('tag_name', '\x00'), ('tag_name', '\ud800'),
                           ('html_url', 'http://example.com')]:
            raw = release(); raw[key] = value
            with self.assertRaises((ValueError, UnicodeError)):
                normalize([raw], 100)
        raw = release(); raw['assets'] *= 2
        with self.assertRaises(ValueError):
            normalize([raw], 100)
