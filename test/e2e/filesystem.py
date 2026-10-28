"""Filesystem observations independent of scenarios and container layout."""
import os


def snapshot_tree(root):
    """Capture descendants' bytes/modes/mtime and link targets without following links.

    Paths are relative strings; root metadata is omitted. File access times and
    directory timestamps are intentionally ignored. Symlink targets are not read.
    """
    return {str(path.relative_to(root)):
            ('link', os.readlink(path)) if path.is_symlink() else
            ('file', path.read_bytes(), path.stat().st_mode, path.stat().st_mtime_ns) if path.is_file() else
            ('dir', path.stat().st_mode)
            for path in root.rglob('*')}
