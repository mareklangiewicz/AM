"""Catalog-only identities publish without recipe conversion or client policies."""
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

    def test_unmigrated_app_shares_source_and_publishes_without_policy(self):
        baseline, sources = host_catalog.configuration(root=pinned_recipes.shared_configuration())
        sample = baseline[0]
        extra = dict(app='catalog-only-example', repository_id=sample['repository_id'],
                     repository=sample['repository'])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root/'tools/catalog-collector'
            config.mkdir(parents=True)
            (config/'collection-recipes.txt').write_text(sample['recipe']+'\n')
            manifest = config/'collection-apps.json'
            manifest.write_text(json.dumps([extra]))
            with patch.object(host_catalog, 'ROOT', root), \
                    patch.object(host_catalog, 'recipe_rows', return_value=[sample]):
                rows, configured = host_catalog.configuration()
                self.assertEqual(rows, [sample, extra])
                self.assertEqual(configured, {str(sample['repository_id']): sample['repository']})
                evidence = root/'evidence'; evidence.mkdir()
                rid = str(sample['repository_id'])
                (evidence/(rid+'-releases.json')).write_text('[]')
                (evidence/(rid+'-receipt.txt')).write_text('2026-11-06T12:00:00Z')
                with patch('urllib.request.urlopen', side_effect=AssertionError('network')), \
                        contextlib.redirect_stdout(io.StringIO()):
                    acquired = {}
                    report = host_catalog.collect({}, evidence, acquisitions=acquired)
                # Both apps share one source: it is fetched once.
                self.assertEqual(len(report), 1)
                self.assertEqual(set(acquired), {rid})
                for bad in ([extra, extra], [dict(extra, repository_id=True)],
                            [dict(extra, repository='$(command)/repo')],
                            [dict(extra, repository='different/source')],
                            [dict(extra, app=sample['app'])],
                            [dict(extra, asset_pattern='.*')], {}):
                    manifest.write_text(json.dumps(bad))
                    with self.subTest(bad=bad), self.assertRaises(ValueError):
                        host_catalog.configuration()
                manifest.write_text(json.dumps([dict(app='extra-'+str(i),
                    repository_id=i+1, repository='owner/repo-'+str(i)) for i in range(host_catalog.SOURCE_CAP+1)]))
                with self.assertRaisesRegex(ValueError, 'manifest scope'):
                    host_catalog.configuration()


if __name__ == '__main__':
    unittest.main()
