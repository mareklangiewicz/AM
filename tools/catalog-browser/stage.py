#!/usr/bin/env python3
"""Stage an exact public payload; never publish or include tracker/fixture files."""
from pathlib import Path
import argparse
import shutil
import json
import hashlib
import re

ROOT = Path(__file__).resolve().parents[2]
FILES = (
    'web/catalog/index.html', 'web/catalog/style.css', 'web/catalog/app.mjs',
    'web/catalog/catalog.mjs', 'web/catalog/keyboard.mjs', 'web/catalog/delivery.mjs',
    'tools/catalog-contract/parse.mjs', 'tools/catalog-contract/schema.mjs', 'tools/catalog-contract/platforms.json',
)

def stage(destination, review_data=None):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    for name in FILES:
        source = ROOT / name
        if source.is_symlink() or not source.is_file():
            raise ValueError(f'Invalid payload source: {name}')
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    if review_data:
        # A review build carries saved catalog/ files; the page reads them instead of main-marek.
        review_data = Path(review_data)
        metadata = json.loads((review_data / 'review.json').read_text())
        for name, digest in metadata['document_sha256'].items():
            if not re.fullmatch(r'apps\.yaml|repositories/[a-z0-9][a-z0-9_.+-]{0,63}\.yaml|status/(?:runs|statistics)\.yaml', name):
                raise ValueError('Unexpected review path')
            source = review_data / 'catalog' / name
            if source.is_symlink() or hashlib.sha256(source.read_bytes()).hexdigest() != digest:
                raise ValueError('Invalid review document')
            target = destination / 'review-data/catalog' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        (destination / 'web/catalog/delivery.mjs').write_text('export default ' + json.dumps(dict(label=metadata['label'])) + ';\n')
    (destination / '.nojekyll').touch()
    (destination / 'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AM catalog</title><script>location.replace("web/catalog/"+location.search+location.hash)</script><a href="web/catalog/">Open AM catalog</a></html>\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', help='New directory; existing directories refuse')
    parser.add_argument('--review-data', type=Path)
    args = parser.parse_args()
    stage(args.destination, args.review_data)
