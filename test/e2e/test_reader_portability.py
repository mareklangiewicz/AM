"""Reader compilation and forbidden-codepoint checks, including native Termux awk."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
READER = ROOT/'modules/catalog-yaml-reader.am'


class ReaderPortability(unittest.TestCase):
    def test_valid_unicode_and_forbidden_raw_codepoints(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'apps.yaml'
            baseline = """format: 2
schema: "https://raw.githubusercontent.com/example/AM/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/docs/catalog-format-v2.md"
repository_id: 123
repository: "example/app"
collection:
  attempted_at: "2026-11-03T00:59:00Z"
  page_size: 100
  page_limit: 1
  reconcile: false
  status: "ok"
last_success:
  completed_at: "2026-11-03T01:00:00Z"
  page_size: 100
  page_limit: 1
  reconcile: false
  pages_fetched: 1
  history_complete: false
observed_at: "2026-11-03T01:00:00Z"
releases:
  "456":
    observed_at: "2026-11-03T00:59:30Z"
    tag: "v2.0.0"
    title: "READER_TEST_VALUE"
    url: "https://github.com/example/app/releases/tag/v2.0.0"
    published_at: "2026-11-02T12:00:00Z"
    prerelease: false
    assets:
      "789":
        name: "John's app #1.AppImage"
        url: "https://github.com/example/app/releases/download/v2.0.0/app?x=a:b#part"
        size: 0
        content_type: ""
"""
            for key, valid in [('app',True),('café',True),('中文',True)]+[
                    ('x'+chr(code)+'y',False) for code in [*range(128,160),0x2028,0x2029,0xfffe,0xffff]]:
                with self.subTest(key=repr(key)):
                    path.write_text(baseline.replace('READER_TEST_VALUE',key))
                    run = subprocess.run(['sh',str(READER),'validate',str(path)],capture_output=True)
                    self.assertEqual(run.returncode == 0,valid,run.stderr)
                    self.assertEqual(run.stdout,b'')
