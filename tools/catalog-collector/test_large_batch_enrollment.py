"""Pinned batch collection from saved pages selects the historical assets."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import contracts
import host_catalog
import pinned_recipes


class LargeBatchEnrollment(unittest.TestCase):
    receipt_name = 'large-batch-evidence.json'
    baseline_revision = 'b61eb2733441d2dd5f998f350ce32a3da1ebc2f9'
    fell_back = {'x86_64/appimagetool','x86_64/appimageupdatetool','x86_64/satty'}

    @classmethod
    def setUpClass(cls):
        # Enrollment and recipes as one snapshot at the pinned commit: an upstream
        # merge rewrites both together (ticket 28).
        temporary = tempfile.TemporaryDirectory(prefix='pinned-configuration-')
        cls.addClassCleanup(temporary.cleanup)
        cls.configuration_root = pinned_recipes.configuration(temporary.name)

    def pinned(self):
        return patch.object(host_catalog, 'ROOT', self.configuration_root)

    def test_configured_collection_preserves_baseline_and_publishes_saved_batch(self):
        research = host_catalog.ROOT/'docs/track/release-catalog/research'
        receipt = json.loads((research/self.receipt_name).read_text())
        archive = research/receipt['evidence_archive']
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),
                         receipt['evidence_archive_sha256'])
        candidates = {r['app']:r for r in receipt['candidates']
                      if r['app'] in receipt['converted']}
        with self.pinned():
            configured, _ = host_catalog.installation_configuration()
        old_list = subprocess.check_output(['git','-C',str(host_catalog.ROOT),'show',
            self.baseline_revision+':tools/catalog-collector/collection-recipes.txt'],text=True)
        old_names = {line for line in old_list.splitlines() if line and not line.startswith('#')}
        # The upstream merge of 2026-11-16 returned these to upstream's originals;
        # their sources stay enrolled as catalog-only, outside this recipe scope.
        self.assertTrue(self.fell_back <= old_names)
        old_names -= self.fell_back
        new_names = {'x86_64/'+app for app in candidates}
        self.assertTrue(old_names.isdisjoint(new_names))
        wanted = old_names | new_names
        self.assertTrue(wanted <= {r['recipe'] for r in configured})
        # Retain each batch's exact historical scope as future batches are added.
        rows = [r for r in configured if r['recipe'] in wanted]
        sources = {str(r['repository_id']):r['repository'] for r in rows}
        old_rows = [r for r in rows if r['recipe'] in old_names]
        old_ids = {r['repository_id'] for r in old_rows}
        new_ids = {r['repository_id'] for r in rows if r['recipe'] in new_names}
        self.assertEqual(len(new_ids),len(candidates))
        self.assertTrue(old_ids.isdisjoint(new_ids))
        self.assertEqual(len(rows),len(wanted))
        revision = 'a'*40
        stamp = '2026-11-06T00:00:00Z'
        with tempfile.TemporaryDirectory(prefix='large-enrollment-') as temporary:
            home = Path(temporary)
            evidence = home/'responses';evidence.mkdir()
            retained = {}
            for row in old_rows:
                rid = str(row['repository_id'])
                retained[rid] = dict(repository_id=int(rid),repository=row['repository'],attempted_at=stamp)
                (evidence/(rid+'-releases.json')).write_text('[]')
                (evidence/(rid+'-receipt.txt')).write_text(stamp)
            with tarfile.open(archive) as saved:
                for app, row in candidates.items():
                    rid = str(row['repository_id'])
                    body = saved.extractfile(app+'/releases.json').read()
                    self.assertEqual(hashlib.sha256(body).hexdigest(), row['releases_sha256'])
                    (evidence/(rid+'-releases.json')).write_bytes(body)
                    (evidence/(rid+'-receipt.txt')).write_text(row['observed_at'][:19]+'Z')
            acquired = {}
            with patch.object(host_catalog,'configuration',return_value=(rows,sources)), \
                    patch('urllib.request.urlopen',side_effect=AssertionError('network')), \
                    contextlib.redirect_stdout(io.StringIO()):
                report = host_catalog.collect(retained,evidence,acquisitions=acquired)
            self.assertEqual(len(report),len(sources))
            self.assertEqual(set(acquired),set(sources))
            for app, row in candidates.items():
                rid = str(row['repository_id'])
                raw = json.loads((evidence/(rid+'-releases.json')).read_bytes())
                self.assertEqual(acquired[rid]['history_complete'],len(raw)<100)
                source = contracts.source(None,acquired[rid],rid=rid,repository=sources[rid],revision=revision)
                document = home/(rid+'.yaml');document.write_bytes(contracts.encode(source))
                facts = subprocess.run(['sh',str(host_catalog.ROOT/'modules/catalog-contract-reader.am'),
                    'asset_facts',str(document)],capture_output=True,text=True,timeout=30)
                self.assertEqual(facts.returncode,0,facts.stderr)
                for command in (['mawk'],['gawk'],['busybox','awk']):
                    with self.subTest(app=app,command=command):
                        selected = subprocess.run([*command,'-f',str(host_catalog.ROOT/'modules/catalog-yaml-policy.am')],
                            input=facts.stdout,text=True,capture_output=True,timeout=15,
                            env=dict(os.environ,LC_ALL='C',AM_YAML_RECIPE='x86_64/'+app,
                                AM_YAML_REPOSITORY=rid,AM_YAML_NOW=source['observed_at'],AM_YAML_PIN=revision))
                        self.assertEqual(selected.returncode,0,selected.stderr)
                        self.assertEqual(selected.stdout.splitlines()[-1],row['old_selected_url'])
            # Strict collection refuses as a whole when one saved page is malformed.
            broken = str(next(iter(candidates.values()))['repository_id'])
            (evidence/(broken+'-releases.json')).write_text('[invalid')
            with patch.object(host_catalog,'configuration',return_value=(rows,sources)), \
                    contextlib.redirect_stdout(io.StringIO()),self.assertRaises(ValueError):
                host_catalog.collect(retained,evidence,acquisitions={})


if __name__ == '__main__':
    unittest.main()
