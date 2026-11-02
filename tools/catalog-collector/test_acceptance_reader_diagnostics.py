"""Retain exact shell-reader refusal diagnostics without weakening byte checks."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from accept_large import shell_reader_check


class ReaderDiagnostics(unittest.TestCase):
    def test_transport_failure_is_retained_before_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            shell=SimpleNamespace(returncode=1,stdout=b'',stderr=b'AM catalog: HTTP refusal\n')
            with self.assertRaisesRegex(ValueError,'acceptance_shell_reader'):
                shell_reader_check(shell,b'expected','alias','a'*40,directory)
            record=json.loads(next(Path(directory).glob('shell-reader-*.json')).read_bytes())
            self.assertFalse(record['matched']);self.assertEqual(record['returncode'],1)
            self.assertEqual(record['stderr'],'AM catalog: HTTP refusal\n')

    def test_successful_wrong_body_still_refuses_and_exact_body_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            shell=SimpleNamespace(returncode=0,stdout=b'wrong',stderr=b'')
            with self.assertRaisesRegex(ValueError,'acceptance_shell_reader'):
                shell_reader_check(shell,b'expected','alias','a'*40,directory)
            shell.stdout=b'expected'
            shell_reader_check(shell,b'expected','alias','a'*40,directory)
            record=json.loads(next(Path(directory).glob('shell-reader-*.json')).read_bytes())
            self.assertTrue(record['matched']);self.assertEqual(record['stdout_sha256'],record['expected_sha256'])
