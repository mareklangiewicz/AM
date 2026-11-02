"""Prepare/test frozen recipe migrations against retained metadata, offline only."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import subprocess

from identity_batch import ROOT, PAYLOAD, PAYLOAD_SHA256
from storage import content

EVIDENCE = ROOT/'docs/track/release-catalog/research/appimage-batch-20261102'
REPORT = EVIDENCE/'migration.json'


def pipeline(row, selector):
    match = re.fullmatch(r"version=\$\(curl -Ls (['\"]?)"+re.escape(row['alias'])+r"\1 \| (.*)\)", selector)
    if not match:
        raise ValueError('unsupported_selector: '+selector)
    return match.group(2)



def compact_recipe(recipe, row):
    install = pipeline(row, recipe['install_selector'])
    if install != pipeline(row, recipe['update_selector']):
        raise ValueError('different_install_update_selector')
    name = Path(recipe['path']).name
    return ('#!/bin/sh\n# AM INSTALL SCRIPT VERSION 3.5\n# AM-CATALOG-RECIPE 1\n'
            'set -eu\nAPP='+name+'\nCATALOG_ALIAS="'+row['alias']+'"\n\n'
            'select_asset() {\n\t'+install+'\n}\n\n'
            '# shellcheck source=modules/appimage.am\n'
            '. "/opt/am/modules/appimage.am"\nam_appimage "$0" "$@"\n')


def evaluate(*, write=False):
    raw = PAYLOAD.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PAYLOAD_SHA256
    payload = json.loads(raw)
    batch = json.loads((EVIDENCE/'batch.json').read_bytes())
    responses = {r['alias']: r for r in batch['releases'] if r['accepted']}
    result = dict(migrated=[], exceptions=[], pending=[], production_delta_lines=0, production_delta_bytes=0)
    for row in payload['rows']:
        if row['alias'] not in responses:
            result['pending'].extend(r['path'] for r in row['recipes'])
            continue
        response = responses[row['alias']]
        directory = ROOT/response['evidence']
        report = json.loads((directory/'report.json').read_bytes())
        body = (directory/'body.json').read_bytes()
        assert hashlib.sha256(body).hexdigest() == report['body_sha256']
        assert hashlib.sha256((directory/'headers.txt').read_bytes()).hexdigest() == report['headers_sha256']
        releases = content(body, dict(url=response['fetch_url']))
        if type(releases) is dict:
            releases = [releases]
        assets = {a['browser_download_url'] for release in releases for a in release['assets']}
        for recipe in row['recipes']:
            path = ROOT/recipe['path']
            original = subprocess.check_output(['git','show',payload['source_revision']+':'+recipe['path']],cwd=ROOT)
            assert hashlib.sha256(original).hexdigest() == recipe['sha256']
            assert original.decode().count(recipe['install_selector']) == 2
            source = compact_recipe(recipe, row)
            selected = []
            for key in ('install_selector', 'update_selector'):
                run = subprocess.run(['sh','-c','APP='+path.name+'\n'+pipeline(row, recipe[key])],
                                     input=body,capture_output=True,check=True,timeout=10)
                selected.append(run.stdout.decode().strip())
            if selected[0] != selected[1] or selected[0] not in assets:
                result['exceptions'].append(dict(path=recipe['path'], alias=row['alias'],
                                                 reason='original_selector_missing_actual_asset', selected=selected))
                continue
            current = path.read_bytes()
            assert hashlib.sha256(current).hexdigest() == recipe['sha256'] or current == source.encode()
            if write:
                path.write_text(source)
            result['migrated'].append(dict(path=recipe['path'], alias=row['alias'],
                                          source_sha256=recipe['sha256'], candidate_sha256=hashlib.sha256(source.encode()).hexdigest(),
                                          asset=selected[0], evidence=response['evidence'],
                                          before_lines=recipe['lines'], after_lines=len(source.splitlines()),
                                          before_bytes=recipe['bytes'], after_bytes=len(source.encode())))
            result['production_delta_lines'] += len(source.splitlines())-recipe['lines']
            result['production_delta_bytes'] += len(source.encode())-recipe['bytes']
    REPORT.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k: len(v) if type(v) is list else v for k,v in result.items()},indent=2))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    evaluate(write=args.write)
