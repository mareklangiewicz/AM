"""Focused offline contract checks. No network transport is available."""
import copy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import unittest

from collector import (BODY_CAP, Chunk, Connected, Descriptor, End, Headers, Plan,
                       Prior, Refusal, Request, Source, collect, plan)

NOW = datetime(2026, 10, 27, 15, tzinfo=timezone.utc)
BODY = b' [ ]\n'  # intentionally preserve formatting
QUOTA = (('x-ratelimit-limit', '1000'), ('x-ratelimit-remaining', '900'),
         ('x-ratelimit-reset', '1793116800'))


class Clock:
    def __init__(self):
        self.seconds = 0
        self.wall_offset = 0

    def utcnow(self):
        return NOW + timedelta(seconds=self.seconds + self.wall_offset)

    def monotonic(self):
        return self.seconds


class Credential:
    def __init__(self):
        self.secret = 'FIXTURE-SECRET-DO-NOT-EMIT'

    def __repr__(self):
        raise AssertionError('credential must never be formatted')


def sources(count=6):
    return tuple(Source(Descriptor(f'https://api.github.com/repos/example/app{n}/releases'),
                        n + 100, 'docs/track/release-catalog/research/fixture.md#identity')
                 for n in range(count))


def response(status=200, body=BODY, headers=QUOTA, delay=1, condition=()):
    return [(0, Connected()), (0, Headers(status, headers, condition)),
            (delay, Chunk(body)), (0, End())]


class FakeTransport:
    def __init__(self, clock, scripts):
        self.clock, self.scripts, self.calls, self.closed = clock, scripts, [], 0

    def execute(self, request, credential, limits):
        index = len(self.calls)
        self.calls.append((request, limits))
        script = self.scripts[index] if index < len(self.scripts) else response()
        try:
            for delay, event in script:
                self.clock.seconds += delay
                if isinstance(event, Exception):
                    raise event
                yield event
        finally:
            self.closed += 1


class CollectorContract(unittest.TestCase):
    def run_batch(self, scripts=(), value=None, credential=None, clock=None):
        clock = clock or Clock()
        transport = FakeTransport(clock, scripts)
        attempts, report = collect(value or plan(sources(), 1), transport, clock,
                                   credential or Credential(), workflow_identity=1)
        self.assertEqual(transport.closed, len(transport.calls))
        return attempts, report, transport

    def test_exact_bytes_six_serial_attempts_and_times(self):
        attempts, report, transport = self.run_batch()
        self.assertEqual(len(transport.calls), 6)
        self.assertTrue(report['complete'])
        self.assertEqual(report['elapsed_seconds'], 6)
        self.assertEqual(report['received_bytes'], 6 * len(BODY))
        for n, attempt in enumerate(attempts):
            self.assertEqual(attempt['body'], BODY)
            self.assertEqual(attempt['request_started_at'], (NOW + timedelta(seconds=n)).isoformat())
            self.assertEqual(attempt['response_completed_at'], (NOW + timedelta(seconds=n+1)).isoformat())
            self.assertEqual(attempt['attempt_finished_at'], attempt['response_completed_at'])
            limits = transport.calls[n][1]
            self.assertEqual(limits.connect_deadline, n + 10)
            self.assertEqual(limits.request_deadline, n + 30)
            self.assertEqual(limits.batch_deadline, 300)

    def test_own_repository_name_numeric_and_alias_exclusion(self):
        for url, aliases in [
            ('https://api.github.com/repos/example/renamed/releases', ()),
            ('https://api.github.com/repositories/1/releases', ()),
            ('https://api.github.com/repos/example/renamed/releases',
             ('https://api.github.com/repositories/1/releases',))]:
            source = replace(sources(1)[0], descriptor=Descriptor(url), repository_id=1, aliases=aliases)
            with self.subTest(url=url, aliases=aliases), self.assertRaises(Refusal):
                plan((source,), 1)

    def test_preflight_revalidation_zero_calls(self):
        invalid = [Plan(2, ()), Plan(True, (Request(sources(1)[0]),)), Plan(1, tuple(Request(s) for s in sources(7))),
                   Plan(1, (Request(replace(sources(1)[0], repository_id=1)),)),
                   Plan(1, (Request(replace(sources(1)[0], repository_id=None)),))]
        clock = Clock()
        for value in invalid:
            transport = FakeTransport(clock, [])
            with self.subTest(value=type(value)), self.assertRaises(Refusal):
                collect(value, transport, clock, Credential(), workflow_identity=1)
            self.assertEqual(transport.calls, [])

    def test_missing_conflicting_or_unreviewed_identity(self):
        first, second = sources(2)
        invalid = [(replace(first, identity_evidence=''),),
                   (replace(first, repository_id=True),),
                   (replace(first, descriptor=Descriptor('https://api.github.com/repositories/999/releases')),),
                   (first, replace(second, descriptor=Descriptor(first.descriptor.url + '/latest'), repository_id=999)),
                   (first, replace(second, aliases=(first.descriptor.url,))),
                   (replace(first, descriptor=Descriptor('https://example.com/releases')),),
                   (replace(first, descriptor=Descriptor(first.descriptor.url + '?token=secret')),)]
        for manifest in invalid:
            with self.subTest(manifest=len(manifest)), self.assertRaises(Refusal):
                plan(manifest, 1)

    def test_prior_integrity_and_no_mutation_on_malformed_plan(self):
        s = sources(1)[0]
        prior = Prior(s.descriptor, BODY, hashlib.sha256(BODY).hexdigest(), NOW.isoformat(), (('etag', 'v1'),))
        previous = {s.descriptor.request_id: prior}
        original = copy.deepcopy(previous)
        self.assertEqual(plan((s,), 1, previous).requests[0].condition, (('etag', 'v1'),))
        for bad in [replace(prior, sha256='bad'), replace(prior, descriptor=Descriptor(s.descriptor.url+'/latest')),
                    replace(prior, validators=(('authorization', 'secret'),)),
                    replace(prior, validated_at='not a time')]:
            with self.assertRaises(Refusal):
                plan((s,), 1, {s.descriptor.request_id: bad})
        self.assertEqual(previous, original)

    def test_matching_304_has_no_retry_and_preserves_previous(self):
        s = sources(1)[0]
        prior = Prior(s.descriptor, BODY, hashlib.sha256(BODY).hexdigest(), NOW.isoformat(), (('etag', 'v1'),))
        previous = {s.descriptor.request_id: prior}
        value = plan((s,), 1, previous)
        attempts, report, transport = self.run_batch([response(304, b'', condition=(('etag','v1'),))], value)
        self.assertEqual(attempts[0]['body'], b'')
        self.assertEqual(attempts[0]['condition'], {'etag': 'v1'})
        self.assertEqual(previous[s.descriptor.request_id], prior)
        self.assertEqual(len(transport.calls), 1)
        self.assertTrue(report['complete'])

    def test_missing_actual_conditional_evidence_refuses(self):
        s = sources(1)[0]
        prior = Prior(s.descriptor, BODY, hashlib.sha256(BODY).hexdigest(), NOW.isoformat(), (('etag','v1'),))
        value = plan((s,),1,{s.descriptor.request_id:prior})
        attempts, report, transport = self.run_batch([response(304,b'')],value)
        self.assertEqual(report['stop_reason'],'protocol_refusal')
        self.assertEqual(attempts[0]['condition'],{})
        self.assertIsNone(attempts[0]['response_completed_at'])
        self.assertEqual(len(transport.calls),1)

    def test_304_missing_or_unavailable_prior_refuses(self):
        values = [plan(sources(1), 1)]
        s = sources(1)[0]
        p = Prior(s.descriptor, BODY, hashlib.sha256(BODY).hexdigest(), NOW.isoformat(), (('etag','v1'),), 'unavailable')
        values.append(plan((s,), 1, {s.descriptor.request_id:p}))
        for value in values:
            attempts, report, transport = self.run_batch([response(304, b'')], value)
            self.assertEqual(report['stop_reason'], 'protocol_refusal')
            self.assertIsNone(attempts[0]['response_completed_at'])
            self.assertEqual(len(transport.calls), 1)

    def test_storage_owns_content_validation_and_state_is_not_modified(self):
        for body in (b'[]', b'{not valid JSON', b'[{"draft":true}]'):
            attempts, report, _ = self.run_batch([response(body=body)],plan(sources(1),1))
            self.assertEqual(attempts[0]['body'],body)
            self.assertTrue(report['complete'])  # transfer complete, not observation acceptance

    def test_redirect_is_inert_and_never_followed(self):
        attempts, _, transport = self.run_batch([response(301, headers=QUOTA+(('location','https://elsewhere.invalid/'),))])
        self.assertEqual(len(transport.calls), 6)
        self.assertEqual(attempts[0]['status'], 301)
        self.assertNotEqual(transport.calls[1][0].source.descriptor.url, attempts[0]['headers']['location'])
        self.assertEqual(attempts[0]['body'], BODY)  # inert, not an observation

    def test_quota_auth_and_missing_header_stops(self):
        cases = [(429, QUOTA, 'rate_limit'), (403, QUOTA, 'authentication_refused'),
                 (401, QUOTA, 'authentication_refused'),
                 (200, (), 'quota_headers_missing_or_invalid'),
                 (200, QUOTA+(('retry-after','60'),), 'rate_limit'),
                 (200, (('x-ratelimit-limit','1000'),('x-ratelimit-remaining','100'),('x-ratelimit-reset','1')), 'quota_reserve'),
                 (403, (('x-ratelimit-remaining','0'),), 'rate_limit'),
                 (200, (('x-ratelimit-limit','1000'),('x-ratelimit-remaining','1001'),('x-ratelimit-reset','1')), 'quota_headers_missing_or_invalid')]
        for status, headers, reason in cases:
            with self.subTest(status=status, reason=reason):
                attempts, report, transport = self.run_batch([response(status, headers=headers)])
                self.assertEqual(report['stop_reason'], reason)
                self.assertEqual(len(transport.calls), 1)
                self.assertEqual(len(report['not_attempted']), 5)
                self.assertEqual(attempts[0]['outcome'], 'response')

    def test_consecutive_failures_and_reset(self):
        _, report, transport = self.run_batch([response(503), response(500)])
        self.assertEqual(report['stop_reason'], 'consecutive_failures')
        self.assertEqual(len(transport.calls), 2)
        _, report, transport = self.run_batch([response(503), response(404), response(503), response(200)])
        self.assertTrue(report['all_attempted'])
        self.assertEqual(len(transport.calls), 6)
        _, report, transport = self.run_batch([[(0, OSError('secret'))], [(0, OSError('secret'))]])
        self.assertEqual(len(transport.calls), 2)
        self.assertEqual(report['stop_reason'], 'consecutive_failures')

    def test_connect_overall_and_batch_deadlines(self):
        cases = [('connect', [(10, Connected())]),
                 ('slow-stream', [(0,Connected()),(0,Headers(200,QUOTA)), *[(6,Chunk(b'x')) for _ in range(6)],(0,End())]),
                 ('batch', [(300,Connected())])]
        for name, script in cases:
            with self.subTest(name=name):
                attempts, report, _ = self.run_batch([script, script])
                self.assertEqual(attempts[0]['outcome'], 'timeout')
                self.assertEqual(attempts[0]['body'], b'')
                self.assertIsNone(attempts[0]['response_completed_at'])
                if name == 'batch':
                    self.assertEqual(report['stop_reason'], 'batch_deadline')
                if name == 'slow-stream':
                    self.assertEqual(report['elapsed_seconds'], 60)
                    self.assertEqual(report['received_bytes'], 10)

    def test_truncated_and_partial_response_have_no_completion(self):
        cases = [[(0,Connected()),(0,Headers(200,QUOTA)),(1,Chunk(b'partial'))],
                 response(headers=QUOTA+(('content-length','99'),))]
        for script in cases:
            attempts, _, _ = self.run_batch([script, script])
            self.assertIsNone(attempts[0]['response_completed_at'])
            self.assertEqual(attempts[0]['body'], b'')

    def test_body_bounds_and_header_bounds(self):
        attempts, _, _ = self.run_batch([response(body=b'x'*BODY_CAP)], plan(sources(1),1))
        self.assertEqual(len(attempts[0]['body']), BODY_CAP)
        for script in [response(body=b'x'*(BODY_CAP+1)),
                       response(headers=QUOTA+(('etag','x'*8193),)),
                       response(headers=QUOTA+(('discarded','x'*64000),)),
                       response(headers=QUOTA+(('ETag','a'),('etag','b')))]:
            attempts, report, transport = self.run_batch([script])
            self.assertEqual(report['stop_reason'], 'protocol_refusal')
            self.assertEqual(attempts[0]['body'], b'')
            self.assertEqual(len(transport.calls), 1)

    def test_credentials_never_formatted_or_exception_text_emitted(self):
        credential = Credential()
        for error in [RuntimeError(credential.secret), Refusal(credential.secret)]:
            attempts, report, _ = self.run_batch([[(0,error)],[(0,error)]], credential=credential)
            self.assertNotIn(credential.secret, repr((attempts,report)))
        headers = QUOTA+(('authorization','fixture-secret'),('set-cookie','fixture-secret'))
        attempts, _, _ = self.run_batch([response(headers=headers)])
        self.assertNotIn('fixture-secret', repr(attempts))
        clock, transport = Clock(), FakeTransport(Clock(), [])
        for cred in [None, 'generic-GH_TOKEN', b'token']:
            with self.assertRaises(Refusal):
                collect(plan(sources(1),1),transport,clock,cred,workflow_identity=1)
        self.assertEqual(transport.calls, [])

    def test_future_prior_zero_calls_and_clock_regression(self):
        s = sources(1)[0]
        p = Prior(s.descriptor,BODY,hashlib.sha256(BODY).hexdigest(),(NOW+timedelta(seconds=1)).isoformat())
        clock = Clock(); transport = FakeTransport(clock,[])
        with self.assertRaises(Refusal):
            collect(plan((s,),1,{s.descriptor.request_id:p}),transport,clock,Credential(),workflow_identity=1)
        self.assertEqual(transport.calls, [])
        attempts, report, _ = self.run_batch([[(-1,Connected())]])
        self.assertEqual(report['stop_reason'], 'clock_refusal')
        self.assertIsNone(attempts[0]['response_completed_at'])


if __name__ == '__main__':
    unittest.main()
