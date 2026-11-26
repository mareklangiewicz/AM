"""Recipe text frozen at one commit, for tests (ticket 28).

An upstream merge rewrites programs/, so a test that reads the live tree can
fail on any merge for a reason unrelated to the code it tests. Tests read the
recipes they use as material from here instead. Move COMMIT only on purpose,
to a commit whose recipes the tests were written against, and keep it on
main-marek so the checkout has it.
"""
import atexit
import io
import sys
import tarfile
import tempfile
from functools import cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT/'tools/recipe-reconstruction') not in sys.path:
    sys.path.insert(0, str(ROOT/'tools/recipe-reconstruction'))
from originals import Originals  # noqa: E402

COMMIT = '125dd7632f670348b06c6ffe705f627f52bbc0a9'  # catalog-simplification 28: retired-names.yaml
_git = Originals(ROOT).git
# What the collector's configuration reads: every recipe (recipe_rows and the
# policy readers glob them), the enrollment (catalog/apps.yaml and the
# repository files it points to) and the fork-side lists beside it.
CONFIGURATION = ('programs/x86_64', 'programs/aarch64', 'programs/i686', 'programs/armv7l',
                 'catalog/apps.yaml', 'catalog/repositories',
                 'tools/catalog-collector/collection-recipes.txt',
                 'tools/catalog-collector/retired-names.yaml')


@cache
def read_bytes(recipe):
    """The bytes of programs/RECIPE (for example 'x86_64/obsidian') at COMMIT."""
    return _git('show', f'{COMMIT}:programs/{recipe}')


def read_text(recipe):
    return read_bytes(recipe).decode('utf-8')


def write(recipe, root):
    """Write programs/RECIPE at COMMIT under ROOT and return its path."""
    path = Path(root)/'programs'/recipe
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(read_bytes(recipe))
    return path


def repository(root, recipes=()):
    """Make ROOT a Git repository that sees this checkout's objects, with RECIPES
    written at COMMIT. Code that reads both `git show COMMIT:programs/R` and the
    working-tree programs/R then agrees, without the live tree."""
    root = Path(root)
    Originals(root.parent).git('init', '--quiet', '--template=', str(root))
    objects = _git('rev-parse', '--path-format=absolute', '--git-path', 'objects').decode().strip()
    (root/'.git/objects/info').mkdir(parents=True, exist_ok=True)
    (root/'.git/objects/info/alternates').write_text(objects+'\n', encoding='utf-8')
    for recipe in recipes:
        write(recipe, root)
    return root


def configuration(root):
    """Unpack CONFIGURATION at COMMIT under ROOT and return ROOT: a consistent
    snapshot of enrollment and recipes to pass as `root` (host_catalog,
    recipe_rows, recipe_policy_source) instead of the live checkout."""
    with tarfile.open(fileobj=io.BytesIO(_git('archive', COMMIT, '--', *CONFIGURATION))) as tree:
        tree.extractall(root, filter='data')
    return Path(root)


@cache
def shared_configuration():
    """One read-only configuration snapshot per test process; never write into it."""
    temporary = tempfile.TemporaryDirectory(prefix='pinned-configuration-')
    atexit.register(temporary.cleanup)
    return configuration(temporary.name)
