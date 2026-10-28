import os
from pathlib import Path
import tempfile
import unittest

from filesystem import snapshot_tree


class SnapshotTree(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def test_empty_and_nested(self):
        self.assertEqual(snapshot_tree(self.root), {})
        (self.root/'nested').mkdir()
        file = self.root/'nested/file'
        file.write_bytes(b'original')
        snapshot = snapshot_tree(self.root)
        self.assertEqual(snapshot['nested'], ('dir', (self.root/'nested').stat().st_mode))
        self.assertEqual(snapshot['nested/file'], ('file', b'original', file.stat().st_mode, file.stat().st_mtime_ns))

    def test_changes_in_contents_mode_and_mtime_are_observed(self):
        file = self.root/'file'; file.write_bytes(b'a')
        before = snapshot_tree(self.root)
        file.write_bytes(b'b')
        self.assertNotEqual(snapshot_tree(self.root), before)
        before = snapshot_tree(self.root)
        file.chmod(0o700)
        self.assertNotEqual(snapshot_tree(self.root), before)
        before = snapshot_tree(self.root)
        stat = file.stat()
        os.utime(file, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000_000))
        self.assertNotEqual(snapshot_tree(self.root), before)

    def test_live_dangling_and_directory_links_are_not_followed(self):
        (self.root/'dir').mkdir()
        (self.root/'dir/file').write_bytes(b'bytes')
        (self.root/'live').symlink_to('dir/file')
        (self.root/'dangling').symlink_to('missing')
        (self.root/'directory-link').symlink_to('dir', target_is_directory=True)
        snapshot = snapshot_tree(self.root)
        for name, target in (('live','dir/file'), ('dangling','missing'), ('directory-link','dir')):
            self.assertEqual(snapshot[name], ('link', target))
        self.assertNotIn('directory-link/file', snapshot)
