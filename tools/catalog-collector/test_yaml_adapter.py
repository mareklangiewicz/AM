"""Offline transport-to-YAML seam checks; never instantiate network transport."""
from datetime import datetime, timezone
import json
from pathlib import Path
import unittest

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


if __name__ == '__main__':
    unittest.main()
