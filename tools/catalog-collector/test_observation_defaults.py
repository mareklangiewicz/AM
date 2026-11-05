#!/usr/bin/env python3
"""Shared observation-default semantics; actual reader queries use effective times."""
import copy
import unittest
from test_yaml_reader import Experiment, document, repository
from retention import fresh, observation, refresh
from test_retention import ATTEMPT, SEEN, LATER, response


def implicit():
    obj = repository()
    obj['observed_at'] = obj['releases']['456'].pop('observed_at')
    return obj


def effective(obj):
    return {rid: observation(record, obj['observed_at']) for rid, record in obj['releases'].items()}


class Defaults(unittest.TestCase):
    accepted = Experiment.accepted
    run_reader = Experiment.run_reader

    def setUp(self):
        self.old = implicit()
        self.facts = copy.deepcopy(self.old['releases']['456'])

    def run_refresh(self, pages, **options):
        result = refresh(self.old, pages, attempted_at=ATTEMPT, **options)
        self.accepted(result)
        return result

    def test_default_change_materializes_untouched_implicit(self):
        before = copy.deepcopy(self.old)
        result = self.run_refresh([response({'457': self.facts})])
        self.assertEqual(result['observed_at'], SEEN)
        self.assertEqual(result['releases']['456']['observed_at'], before['observed_at'])
        self.assertNotIn('observed_at', result['releases']['457'])
        self.assertEqual(effective(result), {'456': before['observed_at'], '457': SEEN})
        self.assertEqual(self.old, before)
        # A second partial refresh must retain both old implicit and old explicit times.
        self.old = result
        next_result = self.run_refresh([response({'458': self.facts}, at=LATER)])
        self.assertEqual(effective(next_result), {'456': before['observed_at'], '457': SEEN, '458': LATER})
        self.assertNotIn('observed_at', next_result['releases']['458'])

    def test_reobservation_replaces_and_elides_override(self):
        self.old['releases']['457'] = dict(observed_at='2026-11-02T00:00:00Z', **self.facts)
        result = self.run_refresh([response({'456': self.facts, '457': self.facts})])
        self.assertTrue(all('observed_at' not in record for record in result['releases'].values()))
        self.assertEqual(effective(result), {'456': SEEN, '457': SEEN})
        # A same-time refresh needs no materialization for untouched records.
        self.old = result
        unchanged = self.run_refresh([response({'456': self.facts})])
        self.assertEqual(unchanged['releases'], result['releases'])

    def test_page_receipts_and_effective_reader_queries(self):
        result = self.run_refresh([response({'457': self.facts}),
                                   response({'458': self.facts}, at=LATER, next=False)], page_limit='all')
        self.assertEqual(result['observed_at'], LATER)
        self.assertEqual(result['releases']['457']['observed_at'], SEEN)
        self.assertNotIn('observed_at', result['releases']['458'])
        text = self.accepted(result)
        rows = self.run_reader(text, 'rows', 'releases', 'observed_at', 'prerelease')
        self.assertEqual(rows.returncode, 0)
        expected = effective(result)
        for line in rows.stdout.decode().splitlines():
            rid, observed, _ = line.split('\t')
            self.assertEqual(observed, '"'+expected[rid]+'"')
        for rid, observed in expected.items():
            query = self.run_reader(text, 'get', 'releases', rid, 'observed_at')
            self.assertEqual((query.returncode, query.stdout), (0, observed.encode()))
        for path in [('releases', '999', 'observed_at'), ('releases', '458', 'assets', '789', 'observed_at')]:
            missing = self.run_reader(text, 'get', *path)
            self.assertEqual((missing.returncode, missing.stdout), (3, b''))
        self.assertEqual(self.run_reader(text, 'get', 'observed_at').stdout, LATER.encode())

    def test_failures_preserve_default_and_stored_release_representation(self):
        before = copy.deepcopy(self.old)
        for options in [dict(page_limit='all', max_requests=1), dict(max_catalog_bytes=1),
                        dict(max_line_bytes=1), dict(max_response_bytes=1),
                        dict(page_limit='all', max_bytes=150), dict(page_limit='all', max_seconds=15)]:
            result = self.run_refresh([response({'457': self.facts}), response({'458': self.facts}, at=LATER, next=False)], **options)
            self.assertEqual(result['collection']['reason'], 'collection_limit')
            for field in ('observed_at', 'releases', 'last_success'):
                self.assertEqual(result[field], before[field])
        for pages in [[response({'457': self.facts}), response(error='transport')],
                      [response({'457': self.facts}), response({'457': self.facts}, at=LATER, next=False)]]:
            result = self.run_refresh(pages, page_limit='all')
            for field in ('observed_at', 'releases', 'last_success'):
                self.assertEqual(result[field], before[field])
        self.assertEqual(self.old, before)

    def test_empty_success_reconciliation_and_first_failure(self):
        result = self.run_refresh([response(next=False)])
        self.assertEqual(result['observed_at'], SEEN)
        self.assertEqual(effective(result), effective(self.old))
        reconciled = self.run_refresh([response(next=False)], page_limit='all', reconcile=True)
        self.assertEqual(reconciled['releases'], {})
        self.assertEqual(reconciled['observed_at'], SEEN)
        never = {k: self.old[k] for k in ('format', 'schema', 'repository_id', 'repository')}
        failed = refresh(never, [], attempted_at=ATTEMPT)
        self.accepted(failed)
        for field in ('observed_at', 'last_success', 'releases'):
            self.assertNotIn(field, failed)

    def test_selected_freshness_and_clock_regression(self):
        result = self.run_refresh([response({'457': self.facts})])
        self.assertFalse(fresh(result['releases']['456'], '2026-11-05T01:00:00Z', default=result['observed_at']))
        self.assertTrue(fresh(result['releases']['457'], '2026-11-05T01:00:00Z', default=result['observed_at']))
        self.old['observed_at'] = '2026-11-04T00:01:00Z'
        self.old['last_success']['completed_at'] = self.old['observed_at']
        failed = self.run_refresh([response({'457': self.facts})])
        self.assertEqual(failed['collection']['reason'], 'invalid_response')
        self.assertEqual(failed['observed_at'], self.old['observed_at'])
        self.assertEqual(failed['releases'], self.old['releases'])

    def test_reader_rejects_missing_or_redundant_or_invalid_defaults(self):
        for change in [lambda obj: obj.pop('observed_at'),
                       lambda obj: obj.update(observed_at='2026-11-04T00:00:00Z'),
                       lambda obj: obj.update(observed_at='2026-02-30T00:00:00Z'),
                       lambda obj: obj['releases']['456'].update(observed_at=obj['observed_at'])]:
            obj = implicit(); change(obj)
            run = self.run_reader(document(obj), 'rows', 'releases', 'observed_at')
            self.assertEqual((run.returncode, run.stdout), (2, b''))
        text = self.accepted(self.old)
        for command, args in [('get', ('releases', '456', 'observed_at')),
                              ('rows', ('releases', 'observed_at'))]:
            run = self.run_reader(text+'unknown: "suffix"\n', command, *args)
            self.assertEqual((run.returncode, run.stdout), (2, b''))
