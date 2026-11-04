"""Offline transport-to-YAML seam checks; never instantiate network transport."""
from datetime import datetime, timezone
import json
from pathlib import Path
import unittest
import sys

# Historical fixture builders remain test-only dependencies.
sys.path.append(str(Path(__file__).resolve().parents[1]/'catalog-yaml-prototype'))

import yaml_adapter as adapter
from test_collector import Clock, Credential, FakeTransport, QUOTA, response
from bounded_experiment import release
from experiment import repository
from yaml_publication import decode_document

ROOT = Path(__file__).resolve().parents[2]
RAW = (ROOT/'docs/track/release-catalog/design/staged-manifest.json').read_bytes()
REV = '125a2ff9d'  # Resolve the actual reviewed source, rather than a fixture schema URL.


class ClockNow(Clock):
    def utcnow(self):
        from datetime import timedelta
        return datetime(2026, 11, 4, 13, tzinfo=timezone.utc) + timedelta(seconds=self.seconds)


class YamlAdapter(unittest.TestCase):
    def setUp(self):
        import subprocess
        self.revision = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', REV]).decode().strip()
        self.value = adapter.list_plan(RAW, 1, sources=['262342594', '16408992'])
        self.repositories = {}
        for request in self.value.requests:
            rid = str(request.source.repository_id)
            obj = repository()
            obj.update(repository_id=int(rid), schema=adapter.schema_url(self.revision))
            self.repositories[rid] = obj
        self.apps = {'obsidian': 262342594, 'nvim': 16408992}

    def run_candidate(self, scripts):
        clock = ClockNow()
        transport = FakeTransport(clock, scripts)
        tree, report = adapter.collect_one_page(self.value, transport, clock, Credential(),
            workflow_identity=1, apps=self.apps, repositories=self.repositories,
            source_revision=self.revision, max_file_bytes=2*1024*1024)
        decoded = {key: decode_document(raw, 2*1024*1024) for key, raw in tree.items()}
        return decoded, report, transport

    def test_real_manifest_deduplicates_endpoint_variants(self):
        value = adapter.list_plan(RAW, 1)
        count = len({r['repository_id'] for r in json.loads(RAW)['sources']})
        self.assertEqual(len(value.requests), count)
        self.assertLess(count, 52)
        self.assertTrue(all(r.prior is None and not r.condition and
                           r.source.descriptor.url == adapter.list_url(r.source.repository_id, 100)
                           for r in value.requests))

    def test_receipts_partial_retention_and_unselected_source(self):
        self.repositories['123'] = repository()
        self.repositories['123']['schema'] = adapter.schema_url(self.revision)
        link = '<' + adapter.list_url(262342594, 100, 2) + '>; rel="next"'
        tree, report, transport = self.run_candidate([
            response(body=json.dumps([release()]).encode(), headers=QUOTA+(('link', link),)),
            response()])
        result = tree['repositories/262342594.yaml']
        self.assertEqual(result['observed_at'], '2026-11-04T13:00:01Z')
        self.assertEqual(result['releases']['456'], self.repositories['262342594']['releases']['456'])
        self.assertIn('457', result['releases'])
        self.assertFalse(result['last_success']['history_complete'])
        self.assertTrue(tree['repositories/16408992.yaml']['last_success']['history_complete'])
        self.assertEqual(tree['repositories/123.yaml'], self.repositories['123'])
        self.assertEqual(tree['apps.yaml']['apps'], self.apps)
        self.assertEqual(len(transport.calls), 2)
        self.assertEqual(set(report['sources'].values()), {'ok'})

    def test_malformed_pagination_preserves_facts(self):
        tree, report, _ = self.run_candidate([response(headers=QUOTA+(('link', '<https://evil.test/>; rel="next"'),))])
        result = tree['repositories/262342594.yaml']
        self.assertEqual(result['collection']['reason'], 'invalid_response')
        for key in ('releases', 'observed_at', 'last_success'):
            self.assertEqual(result[key], self.repositories['262342594'][key])
        self.assertEqual(report['sources']['16408992'], 'ok')

    def test_rate_stop_leaves_unattempted_state_unchanged(self):
        tree, report, transport = self.run_candidate([response(status=429, body=b'{}')])
        self.assertEqual(tree['repositories/262342594.yaml']['collection']['reason'], 'rate_limited')
        self.assertEqual(tree['repositories/16408992.yaml'], self.repositories['16408992'])
        self.assertEqual(report['not_attempted_repositories'], ['16408992'])
        self.assertEqual(len(transport.calls), 1)

    def test_bad_inputs_refuse_before_transport(self):
        for bad in (['unknown'], [], ['16408992', '16408992']):
            with self.assertRaises(ValueError):
                adapter.list_plan(RAW, 1, sources=bad)
        del self.repositories['16408992']
        clock = ClockNow()
        transport = FakeTransport(clock, [])
        with self.assertRaises(ValueError):
            adapter.collect_one_page(self.value, transport, clock, Credential(),
                workflow_identity=1, apps=self.apps, repositories=self.repositories,
                source_revision=self.revision, max_file_bytes=2*1024*1024)
        self.assertEqual(transport.calls, [])

    def test_link_targets_and_relations(self):
        attempt = dict(repository_id=123, descriptor=dict(url=adapter.list_url(123, 100)))
        target = adapter.list_url(123, 100, 2)
        for link in (f'<{target}>; rel="next", <{target}>; rel="last"',
                     '<https://api.github.com/repositories/123/releases?page=2&per_page=100>; rel="next"'):
            self.assertTrue(adapter.has_next(dict(attempt, headers={'link': link}), page_size=100))
        for link in (f'<{target}>; rel="next", <{target}>; rel="next"',
                     f'<{adapter.list_url(123, 100, 3)}>; rel="next"',
                     f'<{target}&page=3>; rel="next"',
                     f'<{target}#fragment>; rel="next"',
                     f'<{adapter.list_url(124, 100, 2)}>; rel="next"',
                     f'<{target}>; rel="last"',
                     f'<{target}>; rel="unknown"', ''):
            with self.subTest(link=link), self.assertRaises(ValueError):
                adapter.has_next(dict(attempt, headers={'link': link}), page_size=100)
        self.assertFalse(adapter.has_next(attempt, page_size=100))


class ScopedYamlAdapter(unittest.TestCase):
    setUp = YamlAdapter.setUp

    def scoped(self, scripts, **options):
        clock = ClockNow()
        transport = FakeTransport(clock, scripts)
        plans = []
        def factory(value):
            plans.append(value)
            return transport
        arguments = dict(workflow_identity=1, apps=self.apps, repositories=self.repositories,
            source_revision=self.revision, max_file_bytes=2*1024*1024,
            max_run_requests=20, max_run_bytes=8_000_000, page_limit='all')
        arguments.update(options)
        tree, report = adapter.collect_scoped(self.value, factory, clock, Credential(), **arguments)
        decoded = {key: decode_document(raw, 2*1024*1024) for key, raw in tree.items()}
        return decoded, report, transport, plans

    def first(self, rid=457):
        link = '<' + adapter.list_url(262342594, 100, 2) + '>; rel="next"'
        return response(body=json.dumps([release(rid)]).encode(), headers=QUOTA+(('link', link),))

    def preserved(self, tree, rid='262342594'):
        result = tree['repositories/'+rid+'.yaml']
        self.assertEqual(result['collection']['status'], 'failed')
        for key in ('releases', 'observed_at', 'last_success'):
            self.assertEqual(result[key], self.repositories[rid][key])
        return result['collection']['reason']

    def test_all_pages_use_validated_plans_and_distinct_receipts(self):
        tree, report, transport, plans = self.scoped([
            self.first(), response(body=json.dumps([release(458)]).encode()), response()])
        result = tree['repositories/262342594.yaml']
        self.assertEqual(result['last_success']['pages_fetched'], 2)
        self.assertTrue(result['last_success']['history_complete'])
        self.assertEqual(result['observed_at'], '2026-11-04T13:00:02Z')
        self.assertEqual(result['releases']['457']['observed_at'], '2026-11-04T13:00:01Z')
        self.assertNotIn('observed_at', result['releases']['458'])
        self.assertEqual(plans[1].requests[0].source.descriptor.url, adapter.list_url(262342594,100,2))
        self.assertTrue(all(not p.requests[0].condition for p in plans))
        self.assertEqual(report['requests'], 3)
        self.assertEqual(transport.closed, 3)

    def test_finite_scope_never_fetches_next_page(self):
        tree, report, transport, _ = self.scoped([self.first(), response()], page_limit=1)
        self.assertEqual(report['requests'], 2)
        self.assertFalse(tree['repositories/262342594.yaml']['last_success']['history_complete'])
        self.assertEqual(transport.calls[1][0].source.repository_id, 16408992)

    def test_duplicate_later_release_rolls_back_without_third_page(self):
        tree, report, _, _ = self.scoped([self.first(), response(body=json.dumps([release()]).encode()), response()])
        self.assertEqual(self.preserved(tree), 'invalid_response')
        self.assertEqual(report['requests'], 3)

    def test_later_bad_body_rolls_back(self):
        tree, report, _, _ = self.scoped([self.first(), response(body=b'{'), response()])
        self.assertEqual(self.preserved(tree), 'invalid_response')
        self.assertEqual(report['sources']['16408992'], 'ok')

    def test_request_limit_does_not_invent_unattempted_time(self):
        tree, report, _, _ = self.scoped([self.first()], max_run_requests=1)
        self.assertEqual(self.preserved(tree), 'collection_limit')
        self.assertEqual(report['not_attempted_repositories'], ['16408992'])
        self.assertEqual(tree['repositories/16408992.yaml'], self.repositories['16408992'])
        self.assertEqual(report['requests'], 1)

    def test_byte_limit_on_later_page_rolls_back_and_closes_transport(self):
        size = len(json.dumps([release()]).encode())
        tree, report, transport, _ = self.scoped([self.first(), response(body=b'x'*20)],
                                                max_run_bytes=size+10)
        self.assertEqual(self.preserved(tree), 'collection_limit')
        self.assertEqual(report['requests'], 2)
        self.assertEqual(transport.closed, 2)
        self.assertGreater(report['received_bytes'], size+10)

    def test_shared_deadline_is_passed_to_existing_transport(self):
        tree, report, transport, _ = self.scoped([self.first(), response(delay=5)], run_seconds=3)
        self.assertEqual(self.preserved(tree), 'collection_limit')
        self.assertEqual(report['not_attempted_repositories'], ['16408992'])
        self.assertTrue(all(limits.batch_deadline == 3 and limits.request_deadline <= 3
                            and limits.connect_deadline <= 3 for _,limits in transport.calls))
        self.assertEqual(transport.closed, 2)

    def test_later_rate_stop_preserves_entire_source(self):
        tree, report, _, _ = self.scoped([self.first(), response(status=429,body=b'{}')])
        self.assertEqual(self.preserved(tree), 'rate_limited')
        self.assertEqual(report['not_attempted_repositories'], ['16408992'])
        self.assertEqual(report['stop_reason'], 'rate_limit')

    def test_source_request_cap_allows_other_sources(self):
        tree, report, _, _ = self.scoped([self.first(), response()], max_source_requests=1)
        self.assertEqual(self.preserved(tree), 'collection_limit')
        self.assertEqual(report['sources']['16408992'], 'ok')

    def test_two_server_failures_stop_before_third_source(self):
        import copy
        self.value = adapter.list_plan(RAW, 1, sources=['262342594', '16408992', '46124547'])
        extra = copy.deepcopy(self.repositories['16408992'])
        extra['repository_id'] = 46124547
        self.repositories['46124547'] = extra
        tree, report, _, _ = self.scoped([response(status=500), response(status=500)])
        self.assertEqual(report['stop_reason'], 'consecutive_failures')
        self.assertEqual(report['not_attempted_repositories'], ['46124547'])
        self.assertEqual(tree['repositories/46124547.yaml'], extra)

    def test_final_budgeted_request_can_complete_scope(self):
        tree, report, _, _ = self.scoped([response()], max_run_requests=1)
        self.assertEqual(report['sources'], {'262342594': 'ok'})
        self.assertEqual(report['not_attempted_repositories'], ['16408992'])
        self.assertTrue(tree['repositories/262342594.yaml']['last_success']['history_complete'])

    def test_explicit_all_reconciliation_waits_for_scope_success(self):
        tree, _, _, _ = self.scoped([self.first(), response(), response()], reconcile=True)
        self.assertNotIn('456', tree['repositories/262342594.yaml']['releases'])
        self.assertIn('457', tree['repositories/262342594.yaml']['releases'])
        tree, _, _, _ = self.scoped([self.first(), response(body=b'{'), response()], reconcile=True)
        self.preserved(tree)

    def test_invalid_budgets_refuse_before_factory(self):
        for options in (dict(max_run_requests=0), dict(max_run_bytes=True),
                        dict(run_seconds=float('nan')), dict(run_seconds=301),
                        dict(page_limit=1,reconcile=True)):
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.scoped([], **options)


if __name__ == '__main__':
    unittest.main()
