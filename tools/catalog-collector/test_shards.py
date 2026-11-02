"""Atomic composition, selective Python reads and unchanged real shell reader."""
import copy
from datetime import datetime, timedelta
import json
import unittest

from consumer import lookup
from public_http import RAW_ROOT, allowed
from reader import StaleObservation
from shards import compose, split, root_index
from storage import apply, canonical, digest, validate
from test_shell_consumer import ShellFixture, ALIAS, PIN
import test_storage as fixtures
from test_storage import GEN, REV


def fixture():
    fixtures.StorageContract.setUpClass()
    base = fixtures.StorageContract.base
    old = validate(base)
    manifest = json.loads(old['manifest_json'])
    trees = {}
    for name, rows in [('00', manifest['sources'][:3]), ('01', manifest['sources'][3:])]:
        raw = canonical(dict(schema=2, sources=rows))
        # Keep recorded successful evidence/provenance, with no synthetic freshness.
        selected = {row['request_id'] for row in rows}
        subset = copy.deepcopy(old)
        subset['manifest_json'] = raw.decode()
        subset['manifest_sha256'] = digest(raw)
        subset['entries'] = {rid: e for rid, e in subset['entries'].items() if rid in selected}
        subset['aliases'] = {a: t for a, t in subset['aliases'].items() if t['request_id'] in selected}
        tree = {'index.json': canonical(subset)}
        for rid in selected:
            path = old['entries'][rid]['observation']['path']
            tree[path] = base[path]
        validate(tree)
        trees[name] = tree
    return trees, compose(trees, generated_at=GEN, revision=REV, run={'id':'2', 'attempt':'1'})


class Shards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shards, cls.tree = fixture()

    def test_roundtrip_and_no_retirement_between_shards(self):
        self.assertEqual(split(self.tree), self.shards)
        self.assertEqual(len(root_index(self.tree['index.json'])['aliases']),
                         sum(len(validate(t)['aliases']) for t in self.shards.values()))

    def test_tamper_extra_missing_route_and_duplicate_refuse(self):
        for mutation in ('body', 'index', 'lookup', 'extra', 'missing', 'route'):
            tree = dict(self.tree)
            if mutation == 'body': tree[next(p for p in tree if p.startswith('bodies/'))] = b'[]'
            if mutation == 'index': tree['shards/00/index.json'] += b' '
            if mutation == 'lookup': tree['lookup.tsv'] += b'bad\n'
            if mutation == 'extra': tree['extra'] = b'x'
            if mutation == 'missing': del tree['shards/00/index.json']
            if mutation == 'route':
                root = json.loads(tree['index.json'])
                root['aliases'][ALIAS] = '01'
                tree['index.json'] = canonical(root)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): split(tree)
        with self.assertRaisesRegex(ValueError, 'duplicate_shard'):
            compose({'00':self.shards['00'], '01':self.shards['00']},
                    generated_at=GEN, revision=REV, run={'id':'1','attempt':'1'})

    def test_reference_selective_pinned_reads_and_exact_stale_consent(self):
        for alias in root_index(self.tree['index.json'])['aliases']:
            calls = []
            def fetch(url, cap, deadline):
                self.assertTrue(allowed(url))
                calls.append(url)
                raw = self.tree[url.removeprefix(RAW_ROOT+PIN+'/')]
                self.assertLessEqual(len(raw), cap)
                return raw
            raw, meta = lookup(alias, commit=PIN, fetch=fetch,
                utcnow=lambda:datetime.fromisoformat(GEN))
            self.assertEqual(len(calls), 3)
            self.assertEqual(meta['catalog_gets'], 3)
            self.assertEqual(raw, self.tree['bodies/'+meta['request_id']+'.json'])
            later = datetime.fromisoformat(GEN)+timedelta(days=3)
            with self.assertRaises(StaleObservation) as error:
                lookup(alias, commit=PIN, fetch=fetch, utcnow=lambda:later)
            result, _ = lookup(alias, commit=PIN, fetch=fetch, utcnow=lambda:later,
                               stale_acceptance=error.exception.acceptance)
            self.assertEqual(result, raw)


class ShardShell(ShellFixture):
    @classmethod
    def setUpClass(cls):
        cls.shards, cls.base = fixture()
        cls.index = validate(cls.shards['00'])
        cls.rid = cls.index['aliases'][ALIAS]['request_id']
        cls.obs = cls.index['entries'][cls.rid]['observation']

    def test_existing_shell_reads_composed_root_without_changes(self):
        for shell in ('/bin/sh', '/bin/bash'):
            result = self.invoke(shell=shell)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, self.body)
            self.assertEqual(len(self.calls()), 2)
