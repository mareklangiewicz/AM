"""Full snapshot reads retain cross-file and byte-canonicality checks."""
import unittest

import test_batch_collection as fixture
from yaml_publication import candidate_tree, tree_documents


class SnapshotCanonicality(unittest.TestCase):
    def test_canonical_snapshot_and_unsorted_app_map(self):
        documents = fixture.BatchCollection().previous(2)
        tree = candidate_tree({'app-2':2,'app-1':1}, documents,
            schema=fixture.SCHEMA, max_file_bytes=fixture.LIMITS['max_file_bytes'])
        self.assertEqual(tree_documents(tree, fixture.LIMITS)[1], documents)
        altered = dict(tree)
        altered['apps.yaml'] = tree['apps.yaml'].replace(
            b'  "app-1": 1\n  "app-2": 2\n', b'  "app-2": 2\n  "app-1": 1\n')
        self.assertNotEqual(altered, tree)
        with self.assertRaises(ValueError):
            tree_documents(altered, fixture.LIMITS)

    def test_missing_reference_and_wrong_source_path_refuse(self):
        tree = candidate_tree({'app-1':1}, fixture.BatchCollection().previous(1),
            schema=fixture.SCHEMA, max_file_bytes=fixture.LIMITS['max_file_bytes'])
        missing = dict(tree)
        missing.pop('repositories/1.yaml')
        with self.assertRaisesRegex(ValueError, 'missing repository'):
            tree_documents(missing, fixture.LIMITS)
        wrong = dict(tree)
        wrong['repositories/2.yaml'] = wrong.pop('repositories/1.yaml')
        with self.assertRaisesRegex(ValueError, 'path_identity'):
            tree_documents(wrong, fixture.LIMITS)


if __name__ == '__main__':
    unittest.main()
