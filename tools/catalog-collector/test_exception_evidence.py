"""Offline numeric redirect-target trust-boundary checks; fake curl only."""
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from exception_batch import numeric_identity
from identity_batch import OWN_REPOSITORY_ID, fetch


class NumericIdentityEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def fake_curl(self, value=None, *, redirect=False):
        if value is None:
            value = dict(id=123, full_name='MovedOwner/NewName', private=False,
                         visibility='public')
        body = json.dumps(value).encode()
        headers = (b'HTTP/1.1 301 Moved\r\nLocation: https://api.github.com/repositories/456\r\n'
                   if redirect else b'HTTP/1.1 200 OK\r\n')
        headers += b'Content-Length: '+str(len(body)).encode()+b'\r\n\r\n'
        curl = self.root/'fake-curl'
        curl.write_text('#!/usr/bin/python3\nimport os,sys,json\n'
                        f'open({str(self.root/"argv.json")!r},"w").write(json.dumps(sys.argv))\n'
                        'fd=int(sys.argv[sys.argv.index("--dump-header")+1].rsplit("/",1)[1])\n'
                        f'os.write(fd,{headers!r})\n'
                        f'os.write(1,{body!r})\n')
        curl.chmod(0o700)
        return str(curl)

    def test_numeric_destination_accepts_renamed_public_repository_and_keeps_exact_evidence(self):
        report = numeric_identity('https://api.github.com/repositories/123', 123,
                                  self.root/'accepted', time.monotonic()+2,
                                  curl=self.fake_curl())
        self.assertTrue(report['accepted'])
        self.assertEqual(report['identity']['full_name'], 'MovedOwner/NewName')
        self.assertEqual(report['identity']['id'], 123)
        self.assertEqual(report, json.loads((self.root/'accepted/report.json').read_text()))
        argv = json.loads((self.root/'argv.json').read_text())
        self.assertEqual(argv[-1], 'https://api.github.com/repositories/123')
        self.assertEqual(argv[argv.index('--max-redirs')+1], '0')
        self.assertNotIn('--location', argv)
        self.assertNotIn('--retry', argv)

    def test_public_id_binding_refuses_mismatches_without_accepting_response(self):
        for index, fields in enumerate((dict(id=456), dict(id=True), dict(private=True),
                                       dict(visibility='private'), dict(full_name='bad/name/extra'),
                                       dict(full_name='mareklangiewicz/AM'))):
            with self.subTest(fields=fields):
                value = dict(id=123, full_name='owner/repo', private=False, visibility='public')
                value.update(fields)
                report = numeric_identity('https://api.github.com/repositories/123', 123,
                                          self.root/f'refused-{index}', time.monotonic()+2,
                                          curl=self.fake_curl(value))
                self.assertFalse(report['accepted'])
                self.assertEqual(report['refusal'], 'numeric_identity_mismatch')

    def test_numeric_url_and_own_repository_refused_before_transport(self):
        for url, repository_id in (
                ('https://api.github.com/repositories/123', 456),
                ('https://api.github.com/repositories/0', 0),
                ('https://api.github.com/repositories/True', True),
                (f'https://api.github.com/repositories/{OWN_REPOSITORY_ID}', OWN_REPOSITORY_ID)):
            with self.subTest(url=url), patch('identity_batch.subprocess.Popen') as spawn:
                with self.assertRaisesRegex(ValueError, 'numeric_identity_url'):
                    numeric_identity(url, repository_id, self.root/'forbidden', time.monotonic()+2)
                spawn.assert_not_called()

    def test_fetch_numeric_grammar_remains_closed_before_transport(self):
        for suffix in ('0123', '0', '-1', '123/', '123?x=1', '123/issues', '123/releases/1',
                       '123/releases?per_page=0', '123%2freleases'):
            with self.subTest(suffix=suffix), patch('identity_batch.subprocess.Popen') as spawn:
                with self.assertRaisesRegex(ValueError, 'evidence_url_refused'):
                    fetch('https://api.github.com/repositories/'+suffix, self.root/'forbidden',
                          time.monotonic()+2, validate_value=lambda *args: {})
                spawn.assert_not_called()

    def test_second_redirect_is_retained_and_refused(self):
        report = numeric_identity('https://api.github.com/repositories/123', 123,
                                  self.root/'redirect', time.monotonic()+2,
                                  curl=self.fake_curl(redirect=True))
        self.assertFalse(report['accepted'])
        self.assertEqual(report['status'], 301)
        self.assertEqual(report['public_headers']['location'],
                         'https://api.github.com/repositories/456')
        self.assertTrue((self.root/'redirect/body.json').is_file())


if __name__ == '__main__':
    unittest.main()
