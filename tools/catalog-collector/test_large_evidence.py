"""No-network resume, exact evidence integrity and oversized-response quota handling."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import large_evidence as live
from storage import digest


class LargeEvidence(unittest.TestCase):
    def test_saved_bytes_are_reused_without_retry_and_tampering_refuses(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root/'queue'; directory.mkdir()
            alias = 'https://api.github.com/repos/example/app'
            raw = json.dumps(dict(rows=[dict(identity_request=alias, alias=alias+'/releases'),
                                        dict(identity_request=alias, alias=alias+'/releases/latest')])).encode()
            (directory/'payload.json').write_bytes(raw)
            manifest = root/'docs/track/release-catalog/design/staged-manifest.json'
            manifest.parent.mkdir(parents=True); manifest.write_text('{}')
            calls = []
            def save(url, out, deadline, **kwargs):
                calls.append(url); out.mkdir()
                body, headers = b'[]', b'headers'
                report = dict(url=url, accepted=True, identity={'id':123}, status=200,
                    body_bytes=len(body), headers_bytes=len(headers), body_sha256=digest(body),
                    headers_sha256=digest(headers), public_headers={'x-ratelimit-remaining':'4000'})
                (out/'body.json').write_bytes(body); (out/'headers.txt').write_bytes(headers)
                (out/'report.json').write_text(json.dumps(report))
                return report
            def release(url, rid, out, deadline, **kwargs): return save(url, out, deadline)
            with patch.multiple(live, ROOT=root, DIRECTORY=directory, OUTPUT=directory/'live', PAYLOAD_HASH=digest(raw)), \
                    patch.object(live, 'audit'), patch.object(live, 'request', side_effect=save), \
                    patch.object(live, 'release_request', side_effect=release), \
                    patch.object(live.subprocess, 'run', return_value=SimpleNamespace(stdout=b'FAKE')), \
                    patch('builtins.print'):
                first = live.collect(); second = live.collect()
                self.assertEqual(len(calls),3)
                self.assertEqual(len(first['identities']),1)
                self.assertEqual(len(second['releases']),2)
                (directory/'live/release-0001/body.json').write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError,'saved_integrity'): live.collect()
                self.assertEqual(len(calls),3)

    def test_oversized_response_stays_refused_but_verified_quota_allows_next_source(self):
        report = dict(curl_exit=63, accepted=False)
        headers = b'HTTP/1.1 200 OK\r\nX-RateLimit-Remaining: 3500\r\n\r\n'
        self.assertFalse(live.quota_stop(report, headers))
        self.assertFalse(report['accepted'])
        self.assertTrue(live.quota_stop(report, b''))
        self.assertTrue(live.quota_stop(report, headers+headers))
        self.assertTrue(live.quota_stop(report, headers.replace(b'3500',b'99')))
