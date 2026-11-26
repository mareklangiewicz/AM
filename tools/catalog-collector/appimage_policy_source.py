#!/usr/bin/env python3
"""Compile reviewed, trusted AppImage policies into the existing awk module.

Each policy is CATALOG_* lines in its own recipe (ticket 26), read literally by
recipe_declarations.appimage_policy_rows; the compiled section of
modules/catalog-yaml-policy.am, which hosts fetch, is the only selection policy
for most of these recipes (ticket 29). No shell execution or catalog-controlled
regular expressions.
"""
import json
from collections import defaultdict
from pathlib import Path

from recipe_declarations import appimage_policy_rows

ROOT = Path(__file__).resolve().parents[2]
START = '# BEGIN explicit AppImage policies (appimage_policy_source.py)\n'
END = '# END explicit AppImage policies\n'


def compile_source(root=ROOT):
    rows = appimage_policy_rows(root)
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


def generate(root=ROOT):
    """Write the policies the tree's recipes declare into its policy module."""
    generated = compile_source(root)
    path = Path(root)/'modules/catalog-yaml-policy.am'
    source = path.read_text()
    if START in source:
        before, rest = source.split(START, 1)
        _, after = rest.split(END, 1)
        source = before + generated + after
    else:
        source = source.replace('BEGIN {\n', generated + 'BEGIN {\n', 1)
    path.write_text(source)


if __name__ == '__main__':
    generate()
