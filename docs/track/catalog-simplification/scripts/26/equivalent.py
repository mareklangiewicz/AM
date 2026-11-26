"""Ticket 26: two policy modules select alike (same assignments, group numbers by content).

python3 docs/track/catalog-simplification/scripts/26/equivalent.py OLD.am NEW.am
Prints what only one side has, ignoring line order, duplicate lines and the
numbering of URL rule groups and AppImage policies. `allow` lists recipes
whose difference is expected.
"""
import re
import sys
from pathlib import Path

ALLOW = {'x86_64/sunshine'}  # its declaration supersedes its old AppImage row


def model(path):
    text = Path(path).read_text()
    image = re.search(r'# BEGIN explicit AppImage policies.*?# END explicit AppImage policies\n', text, re.S)[0]
    text = text.replace(image, '')
    head, rest = text.split('# BEGIN recipe declarations\n', 1)
    block, tail = rest.split('# END recipe declarations\n', 1)
    groups, facts = {}, set()
    for m in re.finditer(r'^    url_rule_(\w+)\[(\d+),(\d+)\]=(.*)$', block, re.M):
        groups.setdefault(m[2], {}).setdefault(m[3], {})[m[1]] = m[4]
    content = {g: tuple(tuple(sorted(r.items())) for _, r in sorted(rules.items(), key=lambda i: int(i[0])))
               for g, rules in groups.items()}
    for line in block.splitlines():
        if line.startswith('    url_rule_'):
            continue
        m = re.fullmatch(r'    recipes_url_group\[(.*)\]=(\d+)', line)
        facts.add(('url_group', m[1], content[m[2]]) if m else ('line', line))
    conds = dict(re.findall(r'if\(image_policy==(\d+)\) return \((.*)\)', image))
    for recipe, number, rest_ in re.findall(r'if\(recipe==("[^"]*")\) \{ image_policy=(\d+);(.*)\}', image):
        facts.add(('image', recipe, conds[number], rest_))
    outside = head + tail
    return facts, outside


old, old_out = model(sys.argv[1])
new, new_out = model(sys.argv[2])
assert old_out == new_out, 'the module differs outside the generated sections'
only_old = {f for f in old - new if not any(a in str(f) for a in ALLOW)}
only_new = {f for f in new - old if not any(a in str(f) for a in ALLOW)}
for f in sorted(map(str, only_old)):
    print('old only:', f)
for f in sorted(map(str, only_new)):
    print('new only:', f)
print(f'{len(old)} old facts, {len(new)} new; {len(old - new)} only old '
      f'({len(old - new) - len(only_old)} allowed), {len(new - old)} only new')
sys.exit(1 if only_old or only_new else 0)
