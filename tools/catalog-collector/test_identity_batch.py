"""Offline request-boundary checks; fake curl never contacts a network."""
import json
import shutil
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

import identity_batch as batch


class IdentityBatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def fake_curl(self, *, body=None, headers=None, code=0, sleep=0):
        if body is None:
            body = json.dumps(dict(id=123, full_name='owner/repo', private=False,
                                   visibility='public')).encode()
        if headers is None:
            headers = b'HTTP/1.1 200 OK\r\nContent-Length: ' + str(len(body)).encode() + b'\r\n\r\n'
        script = self.root / 'curl'
        script.write_text('#!/usr/bin/python3\nimport os,sys,time\n'
                          'fd=int(sys.argv[sys.argv.index("--dump-header")+1].rsplit("/",1)[1])\n'
                          f'os.write(fd, {headers!r})\n'
                          f'os.write(1, {body!r})\n'
                          f'time.sleep({sleep!r})\n'
                          f'sys.exit({code!r})\n')
        script.chmod(0o700)
        return str(script)

    def get(self, **kwargs):
        return batch.request('https://api.github.com/repos/owner/repo', self.root / 'evidence',
                             time.monotonic() + 2, own_id=999, curl=self.fake_curl(**kwargs))

    def test_frozen_payload_and_fingerprints(self):
        self.assertEqual(len(batch.load_payload(check_recipes=False)['identity_requests']), 48)

    def test_changed_recipe_refused_before_requests(self):
        payload = batch.load_payload(check_recipes=False)
        first = self.root/payload['rows'][0]['recipes'][0]['path']
        first.parent.mkdir(parents=True)
        first.write_text('modified')
        with patch.object(batch, 'ROOT', self.root), self.assertRaisesRegex(ValueError, 'recipe_changed'):
            batch.load_payload()

    def test_explicit_credential_not_in_argv_environment_or_evidence(self):
        import subprocess
        spawn = subprocess.Popen
        seen = []
        secret = b'gho_fake_secret_123'
        def checked(command, **kwargs):
            self.assertNotIn(secret.decode(), repr(command))
            self.assertNotIn(secret.decode(), repr(kwargs['env']))
            self.assertTrue(any(arg.startswith('@/dev/fd/') for arg in command))
            seen.append(True)
            return spawn(command, **kwargs)
        with patch.object(batch.subprocess, 'Popen', checked):
            report = batch.request('https://api.github.com/repos/owner/repo', self.root/'evidence',
                                   time.monotonic()+2, own_id=999, curl=self.fake_curl(), token=secret)
        self.assertTrue(report['accepted'] and report['authentication'] and seen)
        for path in (self.root/'evidence').iterdir():
            self.assertNotIn(secret, path.read_bytes())

    def test_payload_tamper_before_requests(self):
        path = self.root / 'payload.json'
        path.write_text('{}')
        with patch.object(batch, 'PAYLOAD', path), self.assertRaisesRegex(ValueError, 'hash'):
            batch.load_payload()

    def test_valid_identity_retains_exact_evidence(self):
        report = self.get()
        self.assertTrue(report['accepted'])
        self.assertEqual(report, json.loads((self.root/'evidence/report.json').read_text()))
        self.assertEqual(report['body_bytes'], len((self.root/'evidence/body.json').read_bytes()))

    def test_identity_and_own_repository_refusals(self):
        for fields in (dict(id=999), dict(id=True), dict(full_name='other/repo'),
                       dict(private=True), dict(visibility='private')):
            with self.subTest(fields=fields):
                evidence = self.root/'evidence'
                if evidence.exists():
                    shutil.rmtree(evidence)
                identity = dict(id=123, full_name='owner/repo', private=False, visibility='public')
                identity.update(fields)
                self.assertFalse(self.get(body=json.dumps(identity).encode())['accepted'])

    def test_redirect_refused_and_saved(self):
        self.assertFalse(self.get(headers=b'HTTP/1.1 301 Moved\r\nLocation: https://example.com\r\n\r\n')['accepted'])

    def test_overflow_kills_and_retains_bounded_prefix(self):
        report = self.get(body=b'x' * 100000)
        self.assertFalse(report['accepted'])
        self.assertLessEqual(report['body_bytes'], 64001)

    def test_parent_deadline_interrupts_silent_child(self):
        started = time.monotonic()
        report = batch.request('https://api.github.com/repos/owner/repo', self.root/'evidence',
                               started + .15, own_id=999, curl=self.fake_curl(sleep=5))
        self.assertEqual(report['termination'], 'parent_deadline')
        self.assertLess(time.monotonic() - started, 1)

    def test_duplicate_json_and_framing_refused(self):
        self.assertFalse(self.get(body=b'{"id":1,"id":2}')['accepted'])
        shutil.rmtree(self.root/'evidence')
        self.assertFalse(self.get(headers=b'HTTP/1.1 200 OK\r\nContent-Length: 1\r\nTransfer-Encoding: chunked\r\n\r\n')['accepted'])

    def test_header_overflow_is_bounded(self):
        report = self.get(headers=b'HTTP/1.1 200 OK\r\nX-Filler: ' + b'x' * 100000)
        self.assertFalse(report['accepted'])
        self.assertLessEqual(report['headers_bytes'], 64001)

    def test_nonzero_exit_refused(self):
        self.assertFalse(self.get(code=7)['accepted'])

    def test_oversized_header_value_refused(self):
        self.assertFalse(self.get(headers=b'HTTP/1.1 200 OK\r\nX-Filler: ' + b'x' * 8193 + b'\r\n\r\n')['accepted'])

    def test_spawn_failure_stops_batch_and_retains_summary(self):
        def fail(*args, **kwargs):
            raise OSError('spawn failed')
        summary = batch.run_batch(dict(identity_requests=['first', 'second']), self.root/'batch',
                                  own_id=999, request_fn=fail)
        self.assertFalse(summary['accepted'])
        self.assertEqual(summary['completed'], [])
        self.assertIn('spawn failed', summary['failure'])

    def test_stop_on_failure_and_refuse_repeat(self):
        calls = []
        def fake(url, out, deadline, **kwargs):
            calls.append(url)
            return dict(accepted=len(calls) < 2)
        payload = dict(identity_requests=['first', 'second', 'third'])
        out = self.root/'batch'
        summary = batch.run_batch(payload, out, own_id=999, request_fn=fake)
        self.assertFalse(summary['accepted'])
        self.assertEqual(calls, ['first', 'second'])
        self.assertEqual(summary, json.loads((out/'batch.json').read_text()))
        with self.assertRaises(FileExistsError):
            batch.run_batch(payload, out, own_id=999, request_fn=fake)

    def test_batch_deadline_prevents_next_request(self):
        with patch.object(batch, 'BATCH_SECONDS', 0):
            def forbidden(*args, **kwargs):
                self.fail('transport must not start')
            summary = batch.run_batch(dict(identity_requests=['first']), self.root/'batch',
                                      own_id=999, request_fn=forbidden)
        self.assertIn('batch_deadline', summary['failure'])

    def test_all_successful_requests_recorded(self):
        payload = batch.load_payload(check_recipes=False)
        summary = batch.run_batch(payload, self.root/'batch', own_id=999,
                                  request_fn=lambda *a, **k: dict(accepted=True))
        self.assertTrue(summary['accepted'])
        self.assertEqual(len(summary['completed']), 48)


if __name__ == '__main__':
    unittest.main()
