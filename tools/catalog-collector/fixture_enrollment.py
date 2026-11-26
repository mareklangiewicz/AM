"""Enrollment for a disposable checkout: catalog/apps.yaml with never-read
repository files, collection-recipes.txt and retired-names.yaml, as Marek
writes them by hand (catalog-simplification ticket 28)."""
import shutil
from pathlib import Path

import documents

RECIPES_COPY = Path(__file__).resolve().parent/'test-recipes'
NVIM, OBSIDIAN = 16408992, 262342594
# app: (repository file name, repository id, repository) for the copied recipes.
RECIPE_APPS = {'nvim': ('nvim', NVIM, 'neovim/neovim'),
               'nvim-nightly': ('nvim', NVIM, 'neovim/neovim'),
               'obsidian': ('obsidian', OBSIDIAN, 'obsidianmd/obsidian-releases')}


def never_read(repository_id, repository):
    """A repository file as enrollment adds it: identity, nothing observed (ticket 27)."""
    return documents.encode('repository', dict(repository_id=repository_id, repository=repository, releases={}))


def retired_names(names):
    return documents.encode('retired_names', dict(retired={name: True for name in names}))


def write(root, *, apps, recipes=(), retired=()):
    """Write enrollment under root and return root.

    apps maps an app to (file name, repository id, repository); each file is
    written never-read unless it exists. recipes are copied from test-recipes
    and listed in collection-recipes.txt."""
    root = Path(root)
    for recipe in recipes:
        target = root/'programs'/recipe
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(RECIPES_COPY/recipe, target)
    collector = root/'tools/catalog-collector'
    collector.mkdir(parents=True, exist_ok=True)
    (collector/'collection-recipes.txt').write_text(''.join(recipe+'\n' for recipe in recipes))
    (collector/'retired-names.yaml').write_bytes(retired_names(retired))
    catalog = root/'catalog'
    (catalog/'repositories').mkdir(parents=True, exist_ok=True)
    for name, rid, repository in apps.values():
        path = catalog/'repositories'/f'{name}.yaml'
        if not path.exists():
            path.write_bytes(never_read(rid, repository))
    (catalog/'apps.yaml').write_bytes(documents.encode('apps', dict(apps={
        app: dict(repository=f'repositories/{name}.yaml') for app, (name, _, _) in apps.items()})))
    return root
