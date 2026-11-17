"""Full snapshot reads retain cross-file and byte-canonicality checks."""
import unittest

import host_catalog
from retention import refresh
from yaml_publication import candidate_tree, schema_url, tree_documents

OLD = '2026-11-05T00:00:00Z'
SCHEMA = schema_url('a'*40)
LIMITS = dict(max_files=1024, max_tree_bytes=1073741824, max_file_bytes=host_catalog.FILE_CAP)


def previous(count):
    """Format-2 repository documents; this file goes with format 2 (ticket 25 step D)."""
    rows = [dict(repository_id=i, repository='owner/repo-'+str(i)) for i in range(1, count+1)]
    return {str(r['repository_id']): refresh(dict(format=2, schema=SCHEMA, **r),
        [dict(received_at=OLD, releases={'123':dict(tag='v1',
            url='https://github.com/'+r['repository']+'/releases/tag/v1',
            published_at=OLD, prerelease=False, assets={})},
            bytes=2, seconds=0, has_next=False)],
        attempted_at=OLD) for r in rows}


class SnapshotCanonicality(unittest.TestCase):
    def test_canonical_snapshot_and_unsorted_app_map(self):
        documents = previous(2)
        tree = candidate_tree({'app-2':2,'app-1':1}, documents,
            schema=SCHEMA, max_file_bytes=LIMITS['max_file_bytes'])
        self.assertEqual(tree_documents(tree, LIMITS)[1], documents)
        altered = dict(tree)
        altered['apps.yaml'] = tree['apps.yaml'].replace(
            b'  "app-1": 1\n  "app-2": 2\n', b'  "app-2": 2\n  "app-1": 1\n')
        self.assertNotEqual(altered, tree)
        with self.assertRaises(ValueError):
            tree_documents(altered, LIMITS)

    def test_missing_reference_and_wrong_source_path_refuse(self):
        tree = candidate_tree({'app-1':1}, previous(1),
            schema=SCHEMA, max_file_bytes=LIMITS['max_file_bytes'])
        missing = dict(tree)
        missing.pop('repositories/1.yaml')
        with self.assertRaisesRegex(ValueError, 'missing repository'):
            tree_documents(missing, LIMITS)
        wrong = dict(tree)
        wrong['repositories/2.yaml'] = wrong.pop('repositories/1.yaml')
        with self.assertRaisesRegex(ValueError, 'path_identity'):
            tree_documents(wrong, LIMITS)


if __name__ == '__main__':
    unittest.main()
