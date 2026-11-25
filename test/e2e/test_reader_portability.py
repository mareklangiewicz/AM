"""The installed catalog reader compiles under the host awk and refuses forbidden raw code points."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
READER = ROOT/'modules/catalog-reader.am'


class ReaderPortability(unittest.TestCase):
    def test_valid_unicode_and_forbidden_raw_codepoints(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'example.yaml'
            baseline = """$schema: "../../schemas/catalog.schema.yaml#/$defs/repository"
repository_id: 123
repository: "example/app"
observed_at: "2026-11-03T01:00:00Z"
history_complete: false
releases:
  "456":
    tag: "v2.0.0"
    title: "READER_TEST_VALUE"
    published_at: "2026-11-02T12:00:00Z"
    prerelease: false
    assets:
      "789":
        name: "John's app #1.AppImage"
        url: "https://github.com/example/app/releases/download/v2.0.0/app?x=a:b#part"
        size: 0
"""
            for key, valid in [('app',True),('café',True),('中文',True)]+[
                    ('x'+chr(code)+'y',False) for code in [*range(128,160),0x2028,0x2029,0xfffe,0xffff]]:
                with self.subTest(key=repr(key)):
                    path.write_text(baseline.replace('READER_TEST_VALUE',key))
                    run = subprocess.run(['sh',str(READER),'validate',str(path)],capture_output=True)
                    self.assertEqual(run.returncode == 0,valid,run.stderr)
                    self.assertEqual(run.stdout,b'')
