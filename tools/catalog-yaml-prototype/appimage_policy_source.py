#!/usr/bin/env python3
"""Compile reviewed, trusted AppImage policies into the existing awk module.

Development-only: this file and the JSON are never fetched or read by clients.
No recipe parsing, shell execution, or catalog-controlled regular expressions.
"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICIES = Path(__file__).with_name('appimage-policies.json')
START = '# BEGIN explicit AppImage policies (appimage_policy_source.py)\n'
END = '# END explicit AppImage policies\n'


def compile_source():
    rows = json.loads(POLICIES.read_text())
    groups = defaultdict(list)
    lines = [START.rstrip(), 'function appimage_recipe(recipe) {']
    # The repository binding is exact per recipe; the catalog map cannot reassign it.
    for row in rows:
        key = json.dumps(row['rules'], sort_keys=True)
        groups[key].append(row)
    for number, (rules, members) in enumerate(groups.items(), 1):
        for row in members:
            lines.append('    if(recipe==' + json.dumps(row['recipe']) + ') { image_policy=' +
                         str(number) + '; image_repository=' + json.dumps(str(row['repository_id'])) + '; image_stable=' +
                         str(int(row['release_rule']=='stable_published_desc')) + '; return 1 }')
    lines.extend(['    return 0', '}', 'function appimage_eligible(url, lower) {', '    lower=tolower(url)'])
    for number, rules in enumerate(groups, 1):
        conditions = []
        for rule in json.loads(rules):
            operand = 'lower' if rule['ignore_case'] else 'url'
            pattern = rule['pattern'].lower() if rule['ignore_case'] else rule['pattern']
            conditions.append(operand + (' !~ ' if rule['exclude'] else ' ~ ') + json.dumps(pattern))
        lines.append('    if(image_policy==' + str(number) + ') return (' + ' && '.join(conditions) + ')')
    lines.extend(['    return 0', '}', END.rstrip(), ''])
    return '\n'.join(lines)


if __name__ == '__main__':
    path = ROOT/'modules/catalog-yaml-policy.am'
    source = path.read_text()
    generated = compile_source()
    if START in source:
        before, rest = source.split(START, 1)
        _, after = rest.split(END, 1)
        source = before + generated + after
    else:
        source = source.replace('BEGIN {\n', generated + 'BEGIN {\n', 1)
    path.write_text(source)
