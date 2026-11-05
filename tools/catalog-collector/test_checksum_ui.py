"""Offline checks of the actual manager verification function."""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ChecksumUI(unittest.TestCase):
    def verify(self, version, url=None, digest_matches=True, digest_available=True):
        with tempfile.TemporaryDirectory() as tmp:
            app = Path(tmp)
            (app / 'version').write_text(version + '\n')
            if url is not None:
                (app / 'download-url').write_text(url + '\n')
            (app / 'demo').write_bytes(b'payload')
            (app / 'AM-VERIFIED').write_text('old verification')
            source = (ROOT / 'APP-MANAGER').read_text()
            function = source.split('_use_verify() {', 1)[1].split('\n}\n', 1)[0]
            digest = hashlib.sha256(b'payload' if digest_matches else b'other').hexdigest() if digest_available else ''
            script = '_use_verify() {' + function + '\n}\n' + '''
_fit() { cat; }
curl() { printf '%s\\n' "$*" >> "$argpath/requests"; printf '%s' "$TEST_DIGEST"; }
argpath=$1
arg=demo
pure_arg=demo
WGETCMD=wget
TEST_DIGEST=$2
_use_verify
'''
            result = subprocess.run(['bash', '-c', script, 'test', tmp, digest],
                                    text=True, capture_output=True)
            marker = app / 'AM-VERIFIED'
            requests = app / 'requests'
            return result.stdout, marker.read_text() if marker.exists() else '', requests.read_text() if requests.exists() else ''

    def test_timestamp_uses_saved_url(self):
        output, marker, requests = self.verify('2026-11-02T00:00:00Z', 'https://example.org/demo.AppImage')
        self.assertIn('Checksum verified.', output)
        self.assertIn('SHA256:', marker)
        self.assertIn('https://example.org/demo.AppImage.zsync', requests)

    def test_saved_url_precedes_version(self):
        _, _, requests = self.verify('https://example.org/old.AppImage', 'https://example.org/new.AppImage')
        self.assertIn('new.AppImage.zsync', requests)
        self.assertNotIn('old.AppImage', requests)

    def test_legacy_version_url(self):
        output, _, _ = self.verify('https://example.org/demo.AppImage')
        self.assertIn('Checksum verified.', output)

    def test_missing_url(self):
        output, marker, requests = self.verify('2026-11-02T00:00:00Z')
        self.assertIn('missing download URL', output)
        self.assertEqual((marker, requests), ('', ''))

    def test_archive_does_not_claim_verification(self):
        for suffix in ('tar.gz', 'tar.xz', 'zip'):
            with self.subTest(suffix=suffix):
                output, marker, requests = self.verify('2026-11-02T00:00:00Z', 'https://example.org/demo.' + suffix)
                self.assertIn('extracted archive files are not verified', output)
                self.assertEqual((marker, requests), ('', ''))

    def test_legacy_archive_does_not_claim_verification(self):
        output, marker, requests = self.verify('https://example.org/demo.tar.gz')
        self.assertIn('extracted archive files are not verified', output)
        self.assertEqual((marker, requests), ('', ''))

    def test_missing_digest_is_not_verification(self):
        output, marker, requests = self.verify('2026-11-02T00:00:00Z', 'https://example.org/demo.AppImage', digest_available=False)
        self.assertNotIn('Checksum verified.', output)
        self.assertEqual(marker, '')
        self.assertIn('demo.AppImage.md5sum', requests)

    def test_mismatch_still_records_failure(self):
        output, marker, _ = self.verify('2026-11-02T00:00:00Z', 'https://example.org/demo.AppImage', False)
        self.assertIn('Checksum does not match', output)
        self.assertEqual(marker, 'Checksum failure')


if __name__ == '__main__':
    unittest.main()
