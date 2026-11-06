"""Actual configured collection and exact-parent publication from saved pages."""
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

import host_catalog
from publication import git, publish_tree
from retention import refresh
from yaml_publication import load_local, publish_local, schema_url


class LargeBatchEnrollment(unittest.TestCase):
    def test_configured_collection_preserves_baseline_and_publishes_twenty_saved_sources(self):
        research = host_catalog.ROOT/'docs/track/release-catalog/research'
        receipt = json.loads((research/'large-batch-evidence.json').read_text())
        archive = research/receipt['evidence_archive']
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),
                         receipt['evidence_archive_sha256'])
        candidates = {r['app']:r for r in receipt['candidates']
                      if r['app'] in receipt['converted']}
        rows, sources = host_catalog.configuration()
        self.assertEqual((len(rows), len(sources)), (43, 41))
        old_rows = [r for r in rows if r['app'] not in candidates]
        self.assertEqual((len(old_rows), len({r['repository_id'] for r in old_rows})), (23, 21))
        schema = schema_url('a'*40)
        stamp = '2026-11-06T00:00:00Z'
        with tempfile.TemporaryDirectory(prefix='large-enrollment-') as temporary:
            home = Path(temporary)
            repo = home/'catalog.git';repo.mkdir()
            git(repo,'init','--bare','--quiet','--template=')
            evidence = home/'responses';evidence.mkdir()
            prior = {}
            for row in old_rows:
                rid = str(row['repository_id'])
                seed = dict(format=2,schema=schema,repository_id=int(rid),repository=row['repository'])
                prior[rid] = refresh(seed,[dict(received_at=stamp,releases={},has_next=False,
                    bytes=2,seconds=0)],attempted_at=stamp,max_catalog_bytes=host_catalog.FILE_CAP)
                (evidence/(rid+'-releases.json')).write_text('[]')
                (evidence/(rid+'-receipt.txt')).write_text(stamp)
            parent = publish_local(repo,{r['app']:r['repository_id'] for r in old_rows},prior,
                schema=schema,max_file_bytes=host_catalog.FILE_CAP,expected_parent=None)
            with tarfile.open(archive) as saved:
                for app, row in candidates.items():
                    rid = str(row['repository_id'])
                    body = saved.extractfile(app+'/releases.json').read()
                    self.assertEqual(hashlib.sha256(body).hexdigest(), row['releases_sha256'])
                    (evidence/(rid+'-releases.json')).write_bytes(body)
                    (evidence/(rid+'-receipt.txt')).write_text(row['observed_at'][:19]+'Z')
            with patch('urllib.request.urlopen',side_effect=AssertionError('network')), \
                    contextlib.redirect_stdout(io.StringIO()):
                tree, report = host_catalog.collect('a'*40,prior,evidence)
            pin = publish_tree(repo,tree,parent)
            apps, repositories = load_local(repo,pin,max_file_bytes=host_catalog.FILE_CAP)
            self.assertEqual(apps,{r['app']:r['repository_id'] for r in rows})
            self.assertEqual(len(report),41)
            self.assertEqual({rid:repositories[rid] for rid in prior},prior)
            self.assertEqual(load_local(repo,parent,max_file_bytes=host_catalog.FILE_CAP)[0],
                             {r['app']:r['repository_id'] for r in old_rows})
            for app, row in candidates.items():
                rid = str(row['repository_id'])
                source = repositories[rid]
                self.assertEqual(source['collection']['status'],'ok')
                self.assertEqual(source['last_success']['page_size'],100)
                raw = json.loads((evidence/(rid+'-releases.json')).read_bytes())
                self.assertEqual(source['last_success']['history_complete'],len(raw)<100)
                document = home/(rid+'.yaml');document.write_bytes(tree['repositories/'+rid+'.yaml'])
                facts = subprocess.run(['sh',str(host_catalog.ROOT/'modules/catalog-yaml-reader.am'),
                    'asset_facts',str(document)],capture_output=True,text=True,timeout=30)
                self.assertEqual(facts.returncode,0,facts.stderr)
                for command in (['mawk'],['gawk'],['busybox','awk']):
                    with self.subTest(app=app,command=command):
                        selected = subprocess.run([*command,'-f',str(host_catalog.ROOT/'modules/catalog-yaml-policy.am')],
                            input=facts.stdout,text=True,capture_output=True,timeout=15,
                            env=dict(os.environ,LC_ALL='C',AM_YAML_RECIPE='x86_64/'+app,
                                AM_YAML_REPOSITORY=rid,AM_YAML_NOW=source['observed_at'],AM_YAML_PIN=pin))
                        self.assertEqual(selected.returncode,0,selected.stderr)
                        self.assertEqual(selected.stdout.splitlines()[-1],row['old_selected_url'])
            # A malformed newly enrolled source must not advance the exact parent.
            broken = str(next(iter(candidates.values()))['repository_id'])
            (evidence/(broken+'-releases.json')).write_text('[invalid')
            with contextlib.redirect_stdout(io.StringIO()),self.assertRaises(ValueError):
                host_catalog.collect('a'*40,repositories,evidence)
            self.assertEqual(git(repo,'rev-parse','refs/heads/catalog').decode().strip(),pin)
