"""Failed attempts: per-repository failure fields, rotation and smaller pages (ticket 20)."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

import collection_interface as interface
import contracts as c
from contracts import decode, encode, header
import host_catalog as host
import incremental
from publication import publish_tree

ROOT = c.ROOT
PIN = 'a'*40
OLD = '2026-11-03T01:00:00Z'
NEW = '2026-11-08T01:00:00Z'


def never_collected(**fields):
    doc = dict(header('repository', PIN), repository_id=123, repository='example/app',
               failed_at=NEW, failed_with='not_found', releases={})
    doc.update(fields)
    return doc


def collected(**fields):
    doc = dict(header('repository', PIN), repository_id=123, repository='example/app', collected_at=OLD,
               scope=dict(page_size=100, pages_fetched=1, history_complete=True), observed_at=OLD, releases={})
    doc.update(fields)
    return doc


def raw(doc):
    """Bytes in canonical encoding, bypassing decode so invalid documents can be built."""
    return ('\n'.join(c.emit_contract(doc, 'repository'))+'\n').encode()


class Readers(unittest.TestCase):
    def shell(self, data):
        with tempfile.NamedTemporaryFile() as f:
            f.write(data); f.flush()
            return subprocess.run(['sh', str(ROOT/'modules/catalog-contract-reader.am'), 'validate', f.name],
                                  capture_output=True)

    def browser(self, data):
        js = ("import {parseDocument} from './tools/catalog-contract/reader.mjs';let s='';"
              "for await(const b of process.stdin)s+=b;try{parseDocument(s)}catch(e){console.error(e.message);process.exitCode=2}")
        return subprocess.run(['node', '--input-type=module', '-e', js], input=data, capture_output=True, cwd=ROOT)

    def test_both_readers_accept_failure_fields_and_refuse_broken_pairs(self):
        good = {'never collected': never_collected(),
                'failing after a success': collected(failed_at=NEW, failed_with='transport')}
        bad = {'failed_at without cause': never_collected(failed_with=None),
               'never collected without failure': never_collected(failed_at=None, failed_with=None),
               'never collected with releases': never_collected(releases=collected(releases={'1': dict(
                   tag='v1', url='https://example.com/r', prerelease=False, published_at=OLD, assets={})})['releases']),
               'collection fields split': collected(scope=None),
               'failure not after collection': collected(failed_at=OLD, failed_with='transport'),
               'unknown cause': never_collected(failed_with='gone')}
        for name, doc in good.items():
            with self.subTest(name):
                self.assertEqual(self.shell(raw(doc)).returncode, 0, self.shell(raw(doc)).stderr)
                self.assertEqual(self.browser(raw(doc)).returncode, 0, self.browser(raw(doc)).stderr)
        for name, doc in bad.items():
            doc = {k: v for k, v in doc.items() if v is not None}
            with self.subTest(name):
                self.assertNotEqual(self.shell(raw(doc)).returncode, 0)
                self.assertNotEqual(self.browser(raw(doc)).returncode, 0)

    def test_a_never_collected_source_yields_no_facts_for_selection(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(encode(never_collected(repository_id=144590939, repository='VSCodium/vscodium'))); f.flush()
            facts = subprocess.run(['sh', str(ROOT/'modules/catalog-contract-reader.am'), 'asset_facts', f.name],
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
        for doc, attempted in ((collected(), OLD), (never_collected(), NEW),
                               (collected(failed_at=NEW, failed_with='transport'), NEW)):
            with self.subTest(doc.get('failed_with')):
                _, meta = incremental.decode('repositories/example.yaml', encode(doc), 'format-3')
                self.assertEqual(meta['attempted_at'], attempted)
                self.assertEqual(meta.get('completed_at'), doc.get('collected_at'))

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
        made = c.source(None, acquired['144590939'], rid='144590939', repository='VSCodium/vscodium', revision=PIN)
        self.assertEqual(made['scope']['page_size'], 30)


class Collect(unittest.TestCase):
    """A failing source gets its fields, keeps its facts, and loses the fields on success."""

    def run_collect(self, root, name, read, parent=None, repo=None):
        registry = root/'names.json'
        registry.write_text(json.dumps(dict(active={'123': 'example', '124': 'other'}, retired=[])))
        rows = [dict(app='example', repository_id=123, repository='example/app'),
                dict(app='other', repository_id=124, repository='owner/other')]
        command = ['collect', '--output', str(root/name), '--registry', str(registry), '--run-id', '7', '--batch-size', '2']
        if parent: command += ['--repo', str(repo), '--parent', parent]
        with patch.object(interface, 'verify_checkout_inputs'), \
                patch.object(host, 'configuration', return_value=(rows, {'123': 'example/app', '124': 'owner/other'})), \
                patch.object(host, '_response', side_effect=read), contextlib.redirect_stdout(io.StringIO()):
            interface.main(command)
        interface.main(['validate', '--candidate', str(root/name/'format-3'), '--channel', 'format-3'])
        return c.read_directory(root/name/'format-3')

    def test_failure_fields_round_trip(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            def first(rid, evidence, allowance, *, rate=None):
                if rid == '123': raise urllib.error.HTTPError('https://api.github.com/', 404, 'x', {}, None)
                if rid == '124': return b'[]', OLD
            with patch.object(host, 'utc', return_value=NEW):
                tree = self.run_collect(root, 'first', first)
            self.assertEqual(decode(tree['repositories/example.yaml']), never_collected(
                schema=decode(tree['repositories/example.yaml'])['schema']))
            self.assertEqual(decode(tree['apps.yaml'])['apps']['example'], 'repositories/example.yaml')

            repo = root/'v3.git'
            subprocess.run(['git', 'init', '--bare', '--quiet', '--template=', str(repo)], check=True)
            parent = publish_tree(repo, tree, None)
            def second(rid, evidence, allowance, *, rate=None):
                if rid == '124': raise OSError('reset')
                return b'[]', '2026-11-09T01:00:00Z'
            with patch.object(host, 'utc', return_value='2026-11-09T02:00:00Z'):
                again = self.run_collect(root, 'second', second, parent, repo)
            fixed = decode(again['repositories/example.yaml'])
            self.assertNotIn('failed_at', fixed)
            self.assertEqual(fixed['collected_at'], '2026-11-09T01:00:00Z')
            failing = decode(again['repositories/other.yaml'])
            self.assertEqual((failing.pop('failed_at'), failing.pop('failed_with')), ('2026-11-09T02:00:00Z', 'transport'))
            before = decode(tree['repositories/other.yaml'])
            self.assertEqual({k: v for k, v in failing.items() if k != 'schema'}, {k: v for k, v in before.items() if k != 'schema'})

    def test_run_wide_stop_records_nothing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            def read(rid, evidence, allowance, *, rate=None):
                raise urllib.error.HTTPError('https://api.github.com/', 403, 'x', {}, None)
            tree = self.run_collect(root, 'out', read)
            self.assertFalse([path for path in tree if path.startswith('repositories/')])


if __name__ == '__main__':
    unittest.main()
