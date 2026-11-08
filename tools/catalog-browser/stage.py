#!/usr/bin/env python3
"""Stage an exact public payload; never publish or include tracker/fixture files."""
from pathlib import Path
import argparse
import shutil

ROOT = Path(__file__).resolve().parents[2]
FILES = (
    'web/catalog/index.html', 'web/catalog/app.mjs',
    'web/catalog/catalog.mjs', 'web/catalog/keyboard.mjs',
    'tools/catalog-contract/reader.mjs', 'tools/catalog-contract/definitions.mjs',
)

def stage(destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    for name in FILES:
        source = ROOT / name
        if source.is_symlink() or not source.is_file():
            raise ValueError(f'Invalid payload source: {name}')
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    (destination / '.nojekyll').touch()
    (destination / 'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AM catalog</title><script>location.replace("web/catalog/"+location.search+location.hash)</script><a href="web/catalog/">Open AM catalog</a></html>\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', help='New directory; existing directories refuse')
    stage(parser.parse_args().destination)
