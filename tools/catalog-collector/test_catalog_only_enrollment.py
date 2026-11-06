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
from publication import git, publish_tree
from yaml_publication import load_local, publish_local, schema_url


class CatalogOnlyEnrollment(unittest.TestCase):
    def test_real_unmigrated_source_collects_but_is_excluded_from_installation(self):
        rows, sources = host_catalog.configuration()
        installed, _ = host_catalog.installation_configuration()
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
                tree, report = host_catalog.collect('a'*40, {}, evidence)
            from yaml_publication import tree_documents
            apps, documents = tree_documents(tree, dict(max_files=1024,
                max_tree_bytes=1073741824, max_file_bytes=host_catalog.FILE_CAP))
            self.assertEqual(apps, {row['app']: row['repository_id']})
            self.assertEqual(len(documents[rid]['releases']), candidate['release_count'])
            self.assertEqual(report[0]['response_sha256'], candidate['releases_sha256'])

    def test_unmigrated_app_shares_source_and_publishes_without_policy(self):
        baseline, sources = host_catalog.configuration()
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
                    tree, report = host_catalog.collect('a'*40, {}, evidence)
                self.assertEqual(len(report), 1)
                repo = root/'catalog.git'; repo.mkdir()
                git(repo, 'init', '--bare', '--quiet', '--template=')
                # Establish an exact parent with the existing app's collected facts.
                from yaml_publication import tree_documents
                _, documents = tree_documents(tree, dict(max_files=1024,
                    max_tree_bytes=1073741824, max_file_bytes=host_catalog.FILE_CAP))
                parent = publish_local(repo, {sample['app']: sample['repository_id']},
                    documents, schema=schema_url('a'*40),
                    max_file_bytes=host_catalog.FILE_CAP, expected_parent=None)
                pin = publish_tree(repo, tree, parent)
                apps, _ = load_local(repo, pin, max_file_bytes=host_catalog.FILE_CAP)
                self.assertEqual(apps[extra['app']], extra['repository_id'])
                self.assertEqual(apps[sample['app']], sample['repository_id'])
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
