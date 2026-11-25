"""Bounded, partially failing acquisition runs over retained source metadata."""
import contextlib
import copy
import io
import json
import unittest
from unittest.mock import patch
import urllib.error

import host_catalog as collector

OLD = '2026-11-05T00:00:00Z'
NEW = '2026-11-06T00:00:00Z'


class BatchCollection(unittest.TestCase):
    def configuration(self, count=4):
        rows = [dict(app='app-'+str(i), repository_id=i, repository='owner/repo-'+str(i))
                for i in range(1, count+1)]
        return rows, {str(r['repository_id']): r['repository'] for r in rows}

    def previous(self, count=2):
        """Retained metadata of the parent snapshot, as Records.metadata gives it."""
        rows, _ = self.configuration(count)
        return {str(r['repository_id']): dict(repository_id=r['repository_id'],
            repository=r['repository'], attempted_at=OLD) for r in rows}

    def collect(self, prior, read, *, size=2, count=4, metrics=None):
        """The acquisition report and the acquired facts of one run."""
        acquired = {}
        with patch.object(collector, 'configuration', return_value=self.configuration(count)), \
                patch.object(collector, '_response', side_effect=read), \
                patch.object(collector, 'utc', return_value=NEW), \
                contextlib.redirect_stdout(io.StringIO()):
            report = collector.collect(prior, batch_size=size, metrics=metrics, acquisitions=acquired)
        return report, acquired

    def test_unattempted_sources_lead_and_a_failure_acquires_nothing(self):
        previous = self.previous()
        original = copy.deepcopy(previous)
        calls = []
        def read(rid, evidence, allowance, *, rate=None):
            calls.append(rid)
            return (b'[]' if rid == '3' else b'{invalid', NEW)
        report, acquired = self.collect(previous, read)
        self.assertEqual(calls, ['3', '4'])
        self.assertEqual(previous, original)
        self.assertEqual(set(acquired), {'3'})
        self.assertEqual(acquired['3']['releases'], {})
        self.assertEqual([(r['repository_id'], r['status']) for r in report], [(3, 'ok'), (4, 'failed')])
        self.assertEqual(report[1]['reason'], 'invalid_response')

    def test_existing_transport_failure_keeps_success_and_auth_failure_stops_requests(self):
        previous = self.previous(4)
        original = copy.deepcopy(previous)
        calls = []
        def read(rid, evidence, allowance, *, rate=None):
            calls.append(rid)
            raise urllib.error.HTTPError('https://api.github.com/', 429, 'rate', {}, None)
        report, acquired = self.collect(previous, read)
        self.assertEqual(calls, ['1'])
        self.assertEqual(acquired, {})
        self.assertEqual(previous, original)
        self.assertEqual(report[0]['reason'], 'transport')
        self.assertEqual(report[0]['http_status'], 429)

    def test_128_source_enrollment_only_attempts_52_and_rejects_unsafe_scope(self):
        calls = []
        def read(rid, evidence, allowance, *, rate=None):
            calls.append(rid)
            return b'[]', NEW
        report, acquired = self.collect({}, read, size=52, count=128)
        self.assertEqual(calls, list(map(str, range(1, 53))))
        self.assertEqual(len(acquired), 52)
        self.assertEqual(len(report), 52)
        for size in (0, collector.REQUEST_CAP+1, True):
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
        def read(rid, evidence, allowance, *, rate=None):
            calls.append((rid, allowance))
            return b'[]', NEW
        metrics = {}
        with patch.object(collector, 'TOTAL_CAP', 2):
            report, acquired = self.collect(previous, read, metrics=metrics)
        self.assertEqual(calls, [('1', 2)])
        self.assertEqual(set(acquired), {'1'})
        self.assertEqual(len(report), 1)
        self.assertEqual(metrics['stop_reason'], 'byte_limit')
        self.assertEqual(metrics['response_bytes'], 2)
        self.assertEqual(metrics['unattempted_sources'], 3)

    def test_reviewed_arduloops_transfer_keeps_numeric_identity_and_retained_facts(self):
        # Real rollout parent: Records exposes repository identity as metadata.
        rid = '1369127769'
        before = dict(repository_id=int(rid), repository='alex-pokydin/ArduLoops',
                      attempted_at=OLD)
        original = copy.deepcopy(before)
        previous = {rid: before}
        current = 'ArduLoops/ArduLoops'
        configuration = ([dict(app='arduloops', repository_id=int(rid), repository=current)],
                         {rid: current})
        with patch.object(collector, 'configuration', return_value=configuration), \
                patch.object(collector, '_response', return_value=(b'[]', NEW)) as read:
            acquired = {}
            report = collector.collect(previous, batch_size=1, acquisitions=acquired)
            self.assertEqual(read.call_args.args[0], rid)
            self.assertEqual(report[0]['status'], 'ok')
            self.assertIn(rid, acquired)
            self.assertEqual(previous[rid], original)
            read.side_effect = OSError('upstream unavailable')
            acquired = {}
            with contextlib.redirect_stdout(io.StringIO()):
                report = collector.collect(previous, batch_size=1, acquisitions=acquired)
            self.assertEqual(report[0]['status'], 'failed')
            self.assertEqual(acquired, {})
            self.assertEqual(previous[rid], original)
            # The approval is directional and specific to this ID and pair.
            for bad in (dict(before, repository_id=1),
                        dict(before, repository='unverified/ArduLoops')):
                with self.assertRaisesRegex(ValueError, 'identity mismatch'):
                    collector.collect({rid: bad}, batch_size=1, acquisitions={})
            with patch.object(collector, 'configuration', return_value=([], {rid: before['repository']})):
                with self.assertRaisesRegex(ValueError, 'identity mismatch'):
                    collector.collect({rid: dict(before, repository=current)}, batch_size=1, acquisitions={})

    def test_native_oversized_response_does_not_starve_later_sources(self):
        configuration = self.configuration(2)
        for total, expected in ((20, ['1', '2']), (5, ['1'])):
            with self.subTest(total=total):
                calls = []
                def read(rid, evidence, allowance, *, rate=None):
                    calls.append(rid)
                    self.assertEqual(allowance, 4)
                    return (b'xxxxx' if rid == '1' else b'[]'), NEW
                with patch.object(collector, 'configuration', return_value=configuration), \
                        patch.object(collector, '_response', side_effect=read), \
                        patch.object(collector, 'RESPONSE_CAP', 4), \
                        patch.object(collector, 'TOTAL_CAP', total), \
                        contextlib.redirect_stdout(io.StringIO()):
                    # No document is created for a failed new source, so the
                    # same source leads the following rotation too (live Wekan).
                    for attempt in range(2):
                        calls.clear()
                        acquired = {}; metrics = {}
                        report = collector.collect({}, batch_size=2, acquisitions=acquired, metrics=metrics)
                        self.assertEqual(calls, expected)
                        self.assertNotIn('1', acquired)
                        self.assertEqual(metrics['response_bytes'], 7 if total == 20 else 5)
                        if total == 20:
                            self.assertIn('2', acquired)
                            self.assertEqual(report[0]['reason'], 'invalid_response')
                        else:
                            self.assertEqual(acquired, {})
                            self.assertEqual(metrics['stop_reason'], 'byte_limit')

    def test_partial_transport_failures_cannot_bypass_the_shared_response_budget(self):
        previous = self.previous(4)
        class Reply:
            status = 200
            headers = {}
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
                patch.object(collector, '_open', side_effect=lambda request: Reply(request)) as get, \
                patch.object(collector, 'utc', return_value=NEW), \
                patch.object(collector, 'TOTAL_CAP', 4), patch.object(collector, 'RESPONSE_CAP', 2), \
                contextlib.redirect_stdout(output):
            acquired = {}
            report = collector.collect(previous, batch_size=4, acquisitions=acquired)
        self.assertEqual(get.call_count, 2)
        self.assertEqual([row['status'] for row in report], ['failed', 'failed'])
        self.assertGreater(sum(row['response_budget_charge'] for row in report), 4)
        self.assertEqual(acquired, {})
        self.assertNotIn('private upstream', output.getvalue())

    def test_elapsed_budget_preserves_sources_that_have_not_been_attempted(self):
        previous = self.previous(4)
        calls = []
        def read(rid, evidence, allowance, *, rate=None):
            calls.append(rid)
            return b'[]', NEW
        with patch.object(collector, 'ACQUISITION_SECONDS', 1), \
                patch.object(collector.time, 'monotonic', side_effect=[0, 0, 2, 2]):
            report, acquired = self.collect(previous, read)
        self.assertEqual(calls, ['1'])
        self.assertEqual(len(report), 1)
        self.assertEqual(set(acquired), {'1'})

    def test_primary_reserve_preserves_unattempted_sources_without_sleeping(self):
        previous = self.previous(4)
        metrics = {}
        def read(rid, evidence, allowance, *, rate=None):
            rate.update(limit=1000, remaining=100, used=900, reset=200, resource='core')
            return b'[]', NEW
        with patch.object(collector.time, 'time', return_value=100):
            report, acquired = self.collect(previous, read, metrics=metrics)
        self.assertEqual(len(report), 1)
        self.assertEqual(set(acquired), {'1'})
        self.assertEqual(metrics['requests'], 1)
        self.assertEqual(metrics['stop_reason'], 'primary_rate_reserve')
        self.assertEqual(metrics['rate_last']['remaining'], 100)

    def test_expired_primary_window_allows_another_request(self):
        metrics = {}
        def read(rid, evidence, allowance, *, rate=None):
            rate.update(remaining=100, reset=99)
            return b'[]', NEW
        with patch.object(collector.time, 'time', return_value=100):
            report, _ = self.collect({}, read, metrics=metrics)
        self.assertEqual(len(report), 2)
        self.assertEqual(metrics['stop_reason'], 'request_limit')

    def test_failed_attempts_are_not_counted_as_successes(self):
        metrics = {}
        def read(rid, evidence, allowance, *, rate=None):
            raise OSError('unavailable')
        report, acquired = self.collect(self.previous(4), read, size=1, metrics=metrics)
        self.assertEqual((metrics['attempted_sources'], metrics['successful_sources']), (1, 0))
        self.assertEqual(acquired, {})

    def test_response_and_http_error_headers_are_sanitized_and_reported(self):
        metrics = {}
        headers = {'X-RateLimit-Limit':'1000', 'X-RateLimit-Remaining':'0',
                   'X-RateLimit-Reset':'200', 'X-RateLimit-Resource':'core',
                   'Retry-After':'60', 'Authorization':'private-token',
                   'X-RateLimit-Used':'private-token'}
        def read(rid, evidence, allowance, *, rate=None):
            raise urllib.error.HTTPError('https://api.github.com/', 429, 'private-token', headers, None)
        report, _ = self.collect(self.previous(4), read, metrics=metrics)
        self.assertEqual(metrics['stop_reason'], 'http_429')
        self.assertEqual(metrics['requests'], 1)
        self.assertEqual(metrics['rate_last'], dict(limit=1000, remaining=0, reset=200,
            resource='core', retry_after_seconds=60))
        self.assertNotIn('private-token', json.dumps((metrics, report)))

    def test_transport_captures_success_headers_without_returning_secrets(self):
        class Reply:
            status = 200
            headers = {'X-RateLimit-Limit':'1000','X-RateLimit-Remaining':'999',
                       'X-RateLimit-Reset':'200', 'Set-Cookie':'private-token'}
            def __init__(self, request): self.url = request.full_url
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, size): return b'[]'
        rate = {}
        with patch.object(collector, '_open', side_effect=lambda request: Reply(request)):
            body, received = collector._response('1', None, 100, rate=rate)
        self.assertEqual(body, b'[]')
        self.assertEqual(rate, dict(limit=1000, remaining=999, reset=200))

    def test_redirect_does_not_forward_credentials_or_make_a_second_request(self):
        import urllib.response
        calls = []
        class Handler(collector.urllib.request.HTTPSHandler):
            def https_open(self, request):
                calls.append(request.full_url)
                response = urllib.response.addinfourl(io.BytesIO(b''),
                    {'Location':'https://elsewhere.invalid/'}, request.full_url, 302)
                response.msg = 'Found'
                return response
        opener = collector.urllib.request.build_opener(collector.NoRedirect(), Handler())
        with patch.object(collector, '_open', side_effect=opener.open):
            with self.assertRaises(urllib.error.HTTPError) as caught:
                collector._response('1', None, 100)
        self.assertEqual(caught.exception.code, 302)
        caught.exception.close()
        self.assertEqual(calls, ['https://api.github.com/repositories/1/releases?per_page=100&page=1'])

    def test_large_batch_stops_at_500_without_advertising_unattempted_sources(self):
        metrics = {}
        def read(rid, evidence, allowance, *, rate=None): return b'[]', NEW
        report, acquired = self.collect({}, read, size=500, count=650, metrics=metrics)
        self.assertEqual(len(report), 500)
        self.assertEqual(metrics['unattempted_sources'], 150)
        self.assertEqual(metrics['successful_sources'], 500)
        self.assertEqual(metrics['stop_reason'], 'request_limit')
        self.assertEqual(len(acquired), 500)
        self.assertNotIn('501', acquired)


if __name__ == '__main__':
    unittest.main()
