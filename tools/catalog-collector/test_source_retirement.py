"""Retiring a catalog source: its documents leave the next snapshot, its name is never reused (ticket 21)."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import contracts as c
from contracts import header, encode, decode
from publication import git, publish_tree
import collection_interface as interface
import host_catalog as host
from test_contracts import PIN, NEW, documents

KEPT, GONE = 123, 456


def repository(rid, name):
    doc = documents()['repository']
    doc.update(repository_id=rid, repository=name)
    return doc


def binding(rid):
    return {'x86_64': dict(repository_id=rid, availability='unknown', classification='unknown')}


class Retirement(unittest.TestCase):
    """A parent snapshot holding two sources; the checkout enrolls only one."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = root = Path(temporary.name)
        self.v3 = root/'v3.git'
        git(root, 'init', '--bare', '--quiet', '--template=', str(self.v3))
        apps = {'example': 'repositories/example.yaml', 'gone': 'repositories/gone.yaml'}
        self.parent = {'catalog.yaml': encode(documents()['catalog']),
                       'apps.yaml': encode(dict(header('apps', PIN), apps=apps)),
                       'repositories/example.yaml': encode(repository(KEPT, 'example/app')),
                       'repositories/gone.yaml': encode(repository(GONE, 'gone/app'))}
        self.parent.update(c.partition_provenance(apps, {'example': binding(KEPT), 'gone': binding(GONE)}, PIN))
        self.prior = publish_tree(self.v3, self.parent, None)
        self.saved = root/'saved'
        self.saved.mkdir()
        (self.saved/'123-releases.json').write_text('[]', encoding='utf-8')
        (self.saved/'123-receipt.txt').write_text(NEW, encoding='utf-8')

    def collect(self, retired, output='output', batch_size=None, schemas=None):
        registry = self.root/(output+'-names.json')
        registry.write_text(json.dumps(dict(active={str(KEPT): 'example'}, retired=retired)), encoding='utf-8')
        rows = [dict(app='example', repository_id=KEPT, repository='example/app')]
        command = ['collect', '--repo', str(self.v3), '--parent', self.prior, '--evidence', str(self.saved),
                   '--registry', str(registry), '--run-id', '124', '--output', str(self.root/output)]
        if batch_size:
            command += ['--batch-size', str(batch_size)]
        if schemas:
            command += ['--schemas-revision', schemas]
        with patch.object(interface, 'verify_checkout_inputs'), \
                patch.object(host, 'configuration', return_value=(rows, {str(KEPT): 'example/app'})), \
                patch.object(host, '_open', side_effect=AssertionError('offline network')):
            interface.main(command)
        return c.read_directory(self.root/output/'format-3')

    def test_a_retired_source_leaves_the_next_snapshot_with_its_provenance(self):
        # A schema transition rebinds every retained source, but not this one.
        for batch_size, schemas in ((None, None), (1, None), (None, 'b'*40)):
            with self.subTest(batch_size=batch_size, schemas=schemas):
                output = 'output-'+str(batch_size)+'-'+str(schemas)
                tree = self.collect(['gone'], output, batch_size, schemas)
                self.assertNotIn('repositories/gone.yaml', tree)
                self.assertNotIn('provenance/gone.yaml', tree)
                self.assertEqual(decode(tree['apps.yaml'])['apps'], {'example': 'repositories/example.yaml'})
                self.assertIn('repositories/example.yaml', tree)
                interface.main(['validate', '--candidate', str(self.root/output/'format-3'), '--channel', 'format-3'])

    def test_the_parent_snapshot_keeps_it(self):
        self.collect(['gone'])
        self.assertEqual(git(self.v3, 'show', self.prior+':repositories/gone.yaml'), self.parent['repositories/gone.yaml'])

    def test_a_source_dropped_without_the_retirement_step_refuses(self):
        for batch_size in (None, 1):
            with self.subTest(batch_size=batch_size), \
                    self.assertRaisesRegex(ValueError, 'retained source gone is neither active nor retired'):
                self.collect([], 'refused-'+str(batch_size), batch_size)


if __name__ == '__main__':
    unittest.main()
