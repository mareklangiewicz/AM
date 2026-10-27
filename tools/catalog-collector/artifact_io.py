"""Read a closed candidate directory without trusting paths or file modes."""
from pathlib import Path
import re
import stat

from collector import BODY_CAP, require
from storage import INDEX_CAP, TREE_CAP, validate


def read_candidate(directory):
    root = Path(directory)
    require(not root.is_symlink() and root.is_dir(), 'invalid_candidate_directory')
    tree, total = {}, 0
    for path in root.rglob('*'):
        relative = path.relative_to(root).as_posix()
        mode = path.lstat().st_mode
        require(not stat.S_ISLNK(mode), 'candidate_symlink')
        if stat.S_ISDIR(mode):
            require(relative == 'bodies', 'unexpected_directory')
            continue
        require(stat.S_ISREG(mode) and not mode & 0o111, 'invalid_candidate_mode')
        require(relative == 'index.json' or re.fullmatch(r'bodies/[0-9a-f]{64}\.json', relative),
                'unexpected_candidate_path')
        cap = INDEX_CAP if relative == 'index.json' else BODY_CAP
        size = path.stat().st_size
        total += size
        require(size <= cap and total <= TREE_CAP, 'candidate_bound')
        with path.open('rb') as stream:
            raw = stream.read(cap + 1)
        require(len(raw) == size and len(raw) <= cap, 'candidate_changed')
        tree[relative] = raw
    validate(tree)
    return tree
