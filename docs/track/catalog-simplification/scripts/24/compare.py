"""Compare every recipe's selection: v3 tip under the old code vs the seed under HEAD (ticket 24 part 4).

    python3 -B docs/track/catalog-simplification/scripts/24/compare.py --old-code DIR --v3 DIR --seed DIR

--old-code is a worktree of the last pre-cutover main-marek (its modules/),
--v3 a checkout of release-catalog-v3's tip, --seed seed.py's output (catalog/).
Each recipe the policy declares is selected at policy level (reader facts into
catalog-yaml-policy.am) with one fixed clock, as catalog-yaml.am would.
Prints a JSON summary and every recipe whose selection differs. Run once.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import subprocess

import yaml

ROOT = Path(__file__).resolve().parents[5]
NOW = '2026-11-25T11:00:00Z'
LOADER = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)
OUTPUT = {'release': 'release-id', 'git-tag': 'tag', 'git-branch': 'git-commit', 'git-file': 'git-commit'}
OPERATION = {'asset': 'asset_facts', 'release': 'release_facts'}


def recipes(policy):
    """Every recipe the HEAD policy knows by name."""
    return sorted(set(re.findall(r'recipes_repository\["([^"]+)"\]', policy.read_text())))


def info(modules, recipe):
    run = subprocess.run(['awk', '-f', str(modules/'catalog-yaml-policy.am')], input=b'', capture_output=True,
                         env=dict(os.environ, LC_ALL='C', AM_YAML_RECIPE=recipe, AM_YAML_CHECK_RECIPE='1',
                                  AM_YAML_APP_NAME='1', AM_YAML_POLICY_INFO='1'))
    if run.returncode:
        return None
    app, selection = run.stdout.decode().splitlines()[:2]
    return app, selection


def select(modules, reader, path, recipe, selection, *, pin_line):
    """The policy's answer for one recipe over one repository file, as identifying lines."""
    rid = subprocess.run(['sh', str(modules/reader), 'get', str(path), 'repository_id'], capture_output=True).stdout.decode()
    facts = subprocess.run(['sh', str(modules/reader), OPERATION.get(selection, 'git_facts'), str(path)], capture_output=True,
                           env=dict(os.environ, AM_YAML_MAX_INPUT_BYTES='33554432', AM_YAML_MAX_OUTPUT_BYTES='33554432'))
    if facts.returncode:
        return 'reader refused'
    env = dict(os.environ, LC_ALL='C', AM_YAML_RECIPE=recipe, AM_YAML_REPOSITORY=rid, AM_YAML_NOW=NOW, AM_YAML_PIN='a'*40)
    if selection in OUTPUT:
        env['AM_YAML_OUTPUT'] = OUTPUT[selection]
    run = subprocess.run(['awk', '-f', str(modules/'catalog-yaml-policy.am')], input=facts.stdout, capture_output=True, env=env)
    if run.returncode:
        return 'refused: '+run.stderr.decode().strip().removeprefix('catalog selection: ')
    lines = run.stdout.decode().splitlines()
    if selection not in OUTPUT:  # repository, release, asset, observed, url (old: a pin line first)
        lines = lines[1:] if pin_line else lines
        return ' '.join([lines[1], lines[2], lines[4]])
    return lines[0] if lines else ''


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--old-code', type=Path, required=True)
    parser.add_argument('--v3', type=Path, required=True)
    parser.add_argument('--seed', type=Path, required=True)
    args = parser.parse_args()
    old_apps = yaml.load((args.v3/'apps.yaml').read_text(), Loader=LOADER)['apps']
    new_apps = yaml.load((args.seed/'apps.yaml').read_text(), Loader=LOADER)['apps']
    old_modules, new_modules = args.old_code/'modules', ROOT/'modules'

    def compare(recipe):
        known = info(new_modules, recipe)
        if not known:
            return recipe, 'not a catalog recipe', None
        app, selection = known
        old_path = args.v3/old_apps[app] if app in old_apps else None
        new_path = args.seed/new_apps[app]['repository'] if app in new_apps else None
        old = select(old_modules, 'catalog-contract-reader.am', old_path, recipe, selection, pin_line=True) if old_path and old_path.exists() else 'no v3 file'
        new = select(new_modules, 'catalog-reader.am', new_path, recipe, selection, pin_line=False) if new_path and new_path.exists() else 'no seed file'
        return recipe, old, new

    with ThreadPoolExecutor(max_workers=os.cpu_count()) as pool:
        results = list(pool.map(compare, recipes(new_modules/'catalog-yaml-policy.am')))
    differ = [r for r in results if r[2] is not None and r[1] != r[2]]
    summary = dict(recipes=len(results), compared=sum(r[2] is not None for r in results),
                   same=sum(r[2] is not None and r[1] == r[2] for r in results), differ=len(differ))
    print(json.dumps(summary))
    for recipe, old, new in differ:
        print(f'{recipe}\n  v3:   {old}\n  seed: {new}')


if __name__ == '__main__':
    main()
