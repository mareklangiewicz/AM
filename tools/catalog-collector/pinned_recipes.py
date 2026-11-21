"""Recipe text frozen at one commit, for tests (ticket 28).

An upstream merge rewrites programs/, so a test that reads the live tree can
fail on any merge for a reason unrelated to the code it tests. Tests read the
recipes they use as material from here instead. Move COMMIT only on purpose,
to a commit whose recipes the tests were written against, and keep it on
main-marek so the checkout has it.
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMMIT = '3b9b918622ea89711078865be4968aa983e5b91b'
_cache = {}


def read_bytes(recipe):
    """The bytes of programs/RECIPE (for example 'x86_64/obsidian') at COMMIT."""
    if recipe not in _cache:
        _cache[recipe] = subprocess.run(
            ['git', '--no-replace-objects', '-C', str(ROOT), 'show', f'{COMMIT}:programs/{recipe}'],
            check=True, capture_output=True).stdout
    return _cache[recipe]


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
    subprocess.run(['git', 'init', '--quiet', '--template=', str(root)], check=True)
    objects = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', '--path-format=absolute', '--git-path', 'objects'],
                             check=True, capture_output=True, text=True).stdout.strip()
    (root/'.git/objects/info').mkdir(parents=True, exist_ok=True)
    (root/'.git/objects/info/alternates').write_text(objects+'\n', encoding='utf-8')
    for recipe in recipes:
        write(recipe, root)
    return root
