"""Failed attempts: failure causes, rotation, smaller pages and what the host makes of a failure (ticket 20).

The failure fields' grammar is the contract's (tools/catalog-contract/examples/
bad-failure-*.yaml); a run that records them is test_catalog_run's.
"""
import contextlib
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

import catalog_run
import documents
import host_catalog as host

ROOT = Path(__file__).resolve().parents[2]
OLD = '2026-11-03T01:00:00Z'
NEW = '2026-11-08T01:00:00Z'


def never_collected(**fields):
    return documents.failed(None, failed_at=NEW, failed_with='not_found', repository_id=fields.get('repository_id', 123),
                            repository=fields.get('repository', 'example/app'))


def collected():
    return documents.repository(None, dict(received_at=OLD, releases={}, history_complete=True),
                                repository_id=123, repository='example/app')


class HostReader(unittest.TestCase):
    def test_a_never_collected_source_yields_no_facts_for_selection(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(documents.encode('repository', never_collected(repository_id=144590939, repository='VSCodium/vscodium')))
            f.flush()
            facts = subprocess.run(['sh', str(ROOT/'modules/catalog-reader.am'), 'asset_facts', f.name],
                                   capture_output=True, text=True)
        self.assertEqual(facts.returncode, 0, facts.stderr)
        selected = subprocess.run(['awk', '-f', str(ROOT/'modules/catalog-yaml-policy.am')], input=facts.stdout,
                                  text=True, capture_output=True,
                                  env=dict(os.environ, LC_ALL='C', AM_YAML_RECIPE='x86_64/vscodium',
                                           AM_YAML_REPOSITORY='144590939', AM_YAML_NOW=NEW))
        self.assertNotEqual(selected.returncode, 0)
        self.assertEqual(selected.stdout, '')
        self.assertNotIn('repository_mismatch', selected.stderr)


class Rotation(unittest.TestCase):
    def test_the_latest_attempt_orders_collection(self):
        failing = documents.failed(collected(), failed_at=NEW, failed_with='transport', repository_id=123,
                                   repository='example/app')
        for document, attempted in ((collected(), OLD), (never_collected(), NEW), (failing, NEW)):
            with self.subTest(document.get('failed_with')):
                top = catalog_run.scan(documents.encode('repository', document))
                self.assertEqual(catalog_run.attempted_at(top), attempted)

    def test_failure_causes_and_run_wide_stops(self):
        def http(code):
            return urllib.error.HTTPError('https://api.github.com/', code, 'x', {}, None)
        cases = {'not_found': http(404), 'transport': http(502), 'too_large': host.ResponseLimit(),
                 'invalid_response': ValueError('page shape'), None: http(403)}
        for cause, error in cases.items():
            with self.subTest(cause):
                self.assertEqual(host.failure_cause(error), cause)
            if isinstance(error, urllib.error.HTTPError): error.close()
        for code in (401, 429):
            error = http(code)
            self.assertIsNone(host.failure_cause(error))
            error.close()
        self.assertIsNone(host.failure_cause(host.CollectionStop('byte_limit')))
        self.assertEqual(host.failure_cause(host.TransferFailure(1)), 'transport')

    def test_named_oversized_sources_request_smaller_pages(self):
        requested = []
        class Response:
            status = 200
            headers = {}
            def __init__(self, url): self.url = url
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, n): return b'[]'
        def opened(request):
            requested.append(request.full_url)
            return Response(request.full_url)
        rows = [dict(app='vscodium', repository_id=144590939, repository='VSCodium/vscodium'),
                dict(app='other', repository_id=7, repository='owner/other')]
        acquired = {}
        with patch.object(host, 'configuration', return_value=(rows, {str(r['repository_id']): r['repository'] for r in rows})), \
                patch.object(host, '_open', side_effect=opened), contextlib.redirect_stdout(io.StringIO()):
            host.collect({}, batch_size=2, acquisitions=acquired)
        self.assertEqual(sorted(requested), ['https://api.github.com/repositories/144590939/releases?per_page=30&page=1',
                                             'https://api.github.com/repositories/7/releases?per_page=100&page=1'])
        # 30 returned of 30 asked is a full page, not the whole history.
        self.assertEqual((acquired['144590939']['page_size'], acquired['7']['page_size']), (30, 100))


if __name__ == '__main__':
    unittest.main()
