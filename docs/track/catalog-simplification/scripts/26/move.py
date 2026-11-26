"""Ticket 26: move the policy JSON rows into their recipes as CATALOG_* lines.

From the repository root:
  python3 docs/track/catalog-simplification/scripts/26/move.py          # check only
  python3 docs/track/catalog-simplification/scripts/26/move.py --write  # rewrite recipes

--write also refreshes each row's source_sha256 in the JSON, so the code that
still reads the JSON accepts the rewritten recipes until it is switched over.
Every recipe must parse back to exactly its rows (aliases that only differ from
the repository in case are implied; AppImage rows drop `selector`).
"""
import collections
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, 'tools/catalog-collector')
from recipe_declarations import MARKER, policy_lines, policy_rows, rows_json, with_policy  # noqa: E402

C = Path('tools/catalog-collector')
url = json.loads((C/'recipe-url-policies.json').read_text())
img = json.loads((C/'appimage-policies.json').read_text())
by_recipe = collections.defaultdict(list)
for row in url:
    by_recipe[row['source_recipe']].append(row)
images = {row['recipe']: row for row in img}
assert not set(by_recipe) & set(images)


def expected_url(row):
    row = {k: v for k, v in row.items() if k != 'source_sha256'}
    row['source_aliases'] = sorted({row['repository'], *(a for a in row['source_aliases']
                                                         if a.lower() != row['repository'].lower())})
    return row


def appimage_digest(text):
    return hashlib.sha256('\n'.join(l for l in text.split('\n') if l != 'CATALOG_FORMAT=3'
                                    and not l.startswith('CATALOG_RECIPE=')).encode()).hexdigest()


changed, skipped, lines = {}, [], 0
for recipe in sorted({*by_recipe, *images}):
    path = Path('programs', recipe)
    text = path.read_text()
    if MARKER in text:  # a declaration supersedes its old row (the manager checks it first)
        skipped.append(recipe)
        continue
    urls, image = by_recipe.get(recipe, []), images.get(recipe)
    if image:
        image = {k: v for k, v in image.items() if k not in ('source_sha256', 'selector')}
    new_lines = policy_lines(urls, image)
    new = with_policy(text, new_lines)
    got = policy_rows(recipe, new)
    assert got == ([expected_url(r) for r in urls], image), recipe
    assert new.replace('\n'.join(new_lines)+'\n', '', 1) == text, recipe
    changed[recipe] = new
    lines += len(new_lines)
print(f'{len(changed)} recipes, {lines} lines; skipped (declared): {skipped}')
if '--write' in sys.argv:
    for recipe, new in changed.items():
        Path('programs', recipe).write_text(new)
    for row in url:
        row['source_sha256'] = hashlib.sha256(changed[row['source_recipe']].encode()).hexdigest()
    for row in img:
        if row['recipe'] in changed:
            row['source_sha256'] = appimage_digest(changed[row['recipe']])
    (C/'recipe-url-policies.json').write_text(rows_json(url))
    (C/'appimage-policies.json').write_text(rows_json(img))
    print('written')
