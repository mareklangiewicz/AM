"""An app in apps.yaml without an installable recipe is collected and never installed.

The refusals of inconsistent enrollment are in test_enrollment.py."""
import contextlib
import io
import hashlib
import json
from pathlib import Path
import tempfile
import tarfile
import unittest
from unittest.mock import patch

import host_catalog
import pinned_recipes


class CatalogOnlyEnrollment(unittest.TestCase):
    def test_real_unmigrated_source_collects_but_is_excluded_from_installation(self):
        # One snapshot of enrollment and recipes at the pinned commit (ticket 28).
        pinned = pinned_recipes.shared_configuration()
        rows, sources = host_catalog.configuration(root=pinned)
        installed, _ = host_catalog.installation_configuration(root=pinned)
        row = next(row for row in rows if row['app'] == 'ageha-editor')
        self.assertNotIn('recipe', row)
        self.assertNotIn(row, installed)
        research = host_catalog.ROOT/'docs/track/release-catalog/research'
        receipt = json.loads((research/'next-ten-evidence.json').read_text())
        candidate = next(r for r in receipt['candidates'] if r['app'] == row['app'])
        archive = research/receipt['evidence_archive']
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),
                         receipt['evidence_archive_sha256'])
        with tempfile.TemporaryDirectory() as temporary, tarfile.open(archive) as saved:
            evidence = Path(temporary)
            body = saved.extractfile(row['app']+'/releases.json').read()
            self.assertEqual(hashlib.sha256(body).hexdigest(), candidate['releases_sha256'])
            rid = str(row['repository_id'])
            (evidence/(rid+'-releases.json')).write_bytes(body)
            (evidence/(rid+'-receipt.txt')).write_text(candidate['observed_at'][:19]+'Z')
            with patch.object(host_catalog, 'configuration', return_value=([row], {rid: row['repository']})), \
                    patch('urllib.request.urlopen', side_effect=AssertionError('network')), \
                    contextlib.redirect_stdout(io.StringIO()):
                acquired = {}
                report = host_catalog.collect({}, evidence, acquisitions=acquired)
            self.assertEqual([(r['repository_id'], r['status']) for r in report], [(row['repository_id'], 'ok')])
            self.assertEqual(len(acquired[rid]['releases']), candidate['release_count'])


if __name__ == '__main__':
    unittest.main()
