#!/usr/bin/env python3
"""Offline synthetic replay only: python tools/catalog-collector/replay.py."""
from datetime import datetime, timedelta, timezone
import hashlib
import json

from collector import (Chunk, Connected, Descriptor, End, Headers, Prior, Source,
                       collect, plan)


class FixtureClock:
    def __init__(self):
        self.seconds = 0

    def utcnow(self):
        return datetime(2026, 10, 27, 15, tzinfo=timezone.utc) + timedelta(seconds=self.seconds)

    def monotonic(self):
        return self.seconds


class FixtureCredential:
    """No actual secret, credential lookup or provenance assertion."""

    def __repr__(self):
        return '<opaque fixture credential>'


class FixtureTransport:
    def __init__(self, clock, slow=False):
        self.clock, self.slow, self.calls = clock, slow, 0

    def execute(self, request, credential, limits):
        self.calls += 1
        yield Connected()
        yield Headers(304 if request.condition else 200, (
            ('x-ratelimit-limit', '1000'), ('x-ratelimit-remaining', '900'),
            ('x-ratelimit-reset', '1793116800'), ('etag', 'fixture-v1')), request.condition)
        if not request.condition:
            for chunk in ([b' '] * 6 if self.slow else [b' []\n']):
                self.clock.seconds += 6 if self.slow else 1
                yield Chunk(chunk)
        yield End()


def main():
    manifest = tuple(Source(
        Descriptor(f'https://api.github.com/repos/fixture/app{n}/releases'),
        n + 100, 'docs/track/release-catalog/research/fixture.md#synthetic-id') for n in range(6))
    reports = {}
    previous = {}
    for name, prior, slow in [('baseline', {}, False), ('conditional', previous, False),
                              ('slow-stream', {}, True)]:
        clock = FixtureClock()
        if name == 'conditional':
            clock.seconds = 60
        transport = FixtureTransport(clock, slow)
        attempts, report = collect(plan(manifest, 1, prior), transport, clock,
                                   FixtureCredential(), workflow_identity=1)
        reports[name] = {'run': report, 'transport_calls': transport.calls, 'attempts': [
            {**{k: v for k, v in a.items() if k != 'body'},
             'body_bytes': len(a['body']), 'body_sha256': hashlib.sha256(a['body']).hexdigest()}
            for a in attempts]}
        if name == 'baseline':
            for source, attempt in zip(manifest, attempts):
                previous[source.descriptor.request_id] = Prior(
                    source.descriptor, attempt['body'], hashlib.sha256(attempt['body']).hexdigest(),
                    attempt['response_completed_at'], (('etag', 'fixture-v1'),))
    print(json.dumps({'synthetic': True, 'network_transport_available': False,
                      'scenarios': reports}, indent=2))


if __name__ == '__main__':
    main()
