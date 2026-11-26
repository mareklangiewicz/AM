"""Ticket 26: what the policy rows hold, and how it would fit CATALOG_* lines.

Run from the repository root: python3 docs/track/catalog-simplification/scripts/26/measure.py
"""
import collections
import json
from pathlib import Path

C = Path('tools/catalog-collector')
url = json.loads((C/'recipe-url-policies.json').read_text())
img = json.loads((C/'appimage-policies.json').read_text())
grep_count = sum(1 for _ in Path('programs').glob('*/*') if 'catalog-yaml.am' in _.read_text(errors='replace'))


def rules_report(name, rows, key):
    counts = collections.Counter(len(r[key]) for r in rows)
    pats = [rule['pattern'] for r in rows for rule in r[key]]
    print(f'{name}: {len(rows)} rows; rules per row {dict(sorted(counts.items()))}')
    print(f'  rule fields {sorted({f for r in rows for rule in r[key] for f in rule})}')
    print(f"  ignore_case false: {sum(not rule['ignore_case'] for r in rows for rule in r[key])}; "
          f"exclude true: {sum(rule['exclude'] for r in rows for rule in r[key])}")
    print(f"  patterns with a single quote: {sum(chr(39) in p for p in pats)}, newline: {sum(chr(10) in p for p in pats)}, "
          f"tab: {sum(chr(9) in p for p in pats)}, non-ASCII: {sum(any(ord(c) > 126 for c in p) for p in pats)}")
    longest = max(len(json.dumps(r[key], separators=(',', ':'))) for r in rows)
    print(f'  longest rules as compact JSON: {longest} chars')


rules_report('recipe-url-policies.json', url, 'url_rules')
print(f"  fields {sorted({f for r in url for f in r})}")
print(f"  channels {dict(collections.Counter(r['channel'] for r in url))}")
per_source = collections.Counter(r['source_recipe'] for r in url)
print(f"  source recipes {len(per_source)}; with several rows {sum(n > 1 for n in per_source.values())} "
      f"(max {max(per_source.values())})")
print(f"  recipe != source_recipe: {sum(r['recipe'] != r['source_recipe'] for r in url)}; "
      f"dispatch_recipe != recipe: {sum(r['dispatch_recipe'] != r['recipe'] for r in url)}")
print(f"  catalog_app != app: {sum(r['catalog_app'] != r['recipe'].split('/')[1] for r in url)}")
print(f"  aliases per row {dict(sorted(collections.Counter(len(r['source_aliases']) for r in url).items()))}; "
      f"aliases beyond the repository and its lowercase: "
      f"{sum(bool(set(r['source_aliases']) - {r['repository'], r['repository'].lower()}) for r in url)}")
print(f"  optional fields present: { {f: sum(f in r for r in url) for f in ('selection','tag_pattern','tag_exclude','git_ref','git_file')} }")
rules_report('appimage-policies.json', img, 'rules')
print(f"  fields {sorted({f for r in img for f in r})}")
print(f"  endpoints {dict(collections.Counter(r['endpoint'] for r in img))}; "
      f"release rules {dict(collections.Counter(r['release_rule'] for r in img))}")
both = {r['source_recipe'] for r in url} & {r['recipe'] for r in img}
print(f'recipes in both files: {len(both)}; scripts calling catalog-yaml.am (all arches): {grep_count}')
