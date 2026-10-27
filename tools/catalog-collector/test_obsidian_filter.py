"""Execute only Obsidian's explicit read-only mode, with offline consumer IO."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

import test_consumer as consumer_tests

PIN = consumer_tests.PIN

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / 'programs/x86_64/obsidian'


class ObsidianFilter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Reuse measured six-source evidence through the actual verified consumer.
        consumer_tests.ConsumerContract.setUpClass()
        case = consumer_tests.ConsumerContract()
        case.setUp()
        cls.body, cls.metadata = case.read(commit=PIN)

    def invoke(self, body, status=0, options=()):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / 'body').write_bytes(body)
            (path / 'python3').write_text(
                '#!' + sys.executable + '\n'
                'import json, pathlib, sys\n'
                'p = pathlib.Path(__file__).parent\n'
                '(p / "args").write_text(json.dumps(sys.argv[1:]))\n'
                'sys.stdout.buffer.write((p / "body").read_bytes())\n'
                f'sys.exit({status})\n')
            (path / 'python3').chmod(0o755)
            # Any accidental installer entry fails before touching installed state.
            for command in ('mkdir', 'wget', 'chmod', 'mv', 'rm', 'ln', 'curl', 'cat'):
                guard = path / command
                guard.write_text('#!/bin/sh\nprintf forbidden >&2\nexit 99\n')
                guard.chmod(0o755)
            result = subprocess.run(
                ['/bin/sh', str(APP), '--catalog-version', *options], cwd=tmp,
                env={**os.environ, 'PATH': tmp + ':/usr/bin:/bin'}, capture_output=True)
            args = json.loads((path / 'args').read_text())
            self.assertEqual(sorted(p.name for p in path.iterdir()),
                             sorted(['body', 'args', 'python3', 'mkdir', 'wget', 'chmod',
                                     'mv', 'rm', 'ln', 'curl', 'cat']))
            return result, args

    def test_verified_saved_response_matches_existing_installer_and_updater_filter(self):
        # Extract the original pipelines as data; never run either installer body.
        filters = re.findall(r'version=\$\(curl[^|]+\| (.*)\)', APP.read_text())
        self.assertEqual(len(filters), 2)
        self.assertEqual(filters[0], filters[1])
        expected = subprocess.run(['/bin/sh', '-c', filters[0]], input=self.body,
                                  capture_output=True, check=True).stdout
        self.assertTrue(expected.strip())
        result, args = self.invoke(self.body, options=('--commit', PIN, '--metadata', 'receipt.json'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, expected)
        self.assertEqual(args, ['-B', str(ROOT / 'tools/catalog-collector/consumer.py'),
                               consumer_tests.ConsumerContract.alias, '--commit', PIN, '--metadata', 'receipt.json'])
        self.assertFalse(result.stderr)

    def test_consumer_failure_discards_even_partial_output_and_never_falls_back(self):
        result, _ = self.invoke(self.body, status=1)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b'')
        self.assertNotIn(b'forbidden', result.stderr)

    def test_empty_or_wrong_arch_selection_refuses(self):
        for body in (b'[]', b'[{"browser_download_url":"https://example.com/arm64.AppImage"}]'):
            with self.subTest(body=body):
                result, _ = self.invoke(body)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, b'')
                self.assertEqual(result.stderr, b'Error getting link\n')

    def test_exact_stale_consent_is_forwarded_without_implicit_override(self):
        options = ('--accept-stale', PIN, self.metadata['request_id'], self.metadata['sha256'])
        result, args = self.invoke(self.body, options=options)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(args[-4:], list(options))
