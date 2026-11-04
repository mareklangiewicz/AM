#!/usr/bin/env python3
"""Offline audit of explicit am-utils policies against hash-checked saved facts."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/catalog-collector'))
from attempt_adapter import merge_attempts, utc
from experiment import SCHEMA
from yaml_publication import candidate_tree
from yaml_recipe_cohort import AM_UTILS, select_cohort

RID = 1225768109
EVIDENCE = ROOT/'docs/track/release-catalog/research/am-utils-release-20261028'


def fixture():
    raw = (EVIDENCE/'body.json').read_bytes()
    report = json.loads((EVIDENCE/'report.json').read_bytes())
    if len(raw) != report['body_bytes'] or hashlib.sha256(raw).hexdigest() != report['body_sha256']:
        raise ValueError('saved body identity')
    attempt = dict(repository_id=RID, descriptor=report['descriptor'], body=raw,
                   outcome='response', status=report['status'],
                   request_started_at=report['started_at'], response_completed_at=report['completed_at'])
    repository = merge_attempts(dict(format=2, schema=SCHEMA, repository_id=RID,
                                    repository='ivan-hc/am-utils'), [(attempt, False)],
        attempted_at=utc(report['started_at']).strftime('%Y-%m-%dT%H:%M:%SZ'),
        page_size=30, max_catalog_bytes=2097152)
    if repository['collection']['status'] != 'ok':
        raise ValueError('saved normalization refused')
    apps = {recipe.split('/')[1]:RID for recipe in AM_UTILS}
    tree = candidate_tree(apps, {str(RID):repository}, schema=SCHEMA, max_file_bytes=2097152)
    return raw, report, repository, tree


def selector(recipe):
    source = (ROOT/'programs'/recipe).read_text()
    arch, app = recipe.split('/')
    component = 'c%2B%2Bfilt' if app == 'c++filt' else '${APP}'
    expected = ('\tsed \'s/[()",{} ]/\\n/g\' | grep -Eoi "https.*download.*/'+arch+
                '-[0-9]{8}/'+component+'_.*-'+arch+'-static$" | head -1')
    match = re.search(r'^select_asset\(\) \{\n(.*?)\n\}',source,re.M|re.S)
    if match is None or match[1] != expected:
        raise ValueError('unreviewed selector: '+recipe)
    if f'CATALOG_RECIPE="{recipe}"' not in source or 'CATALOG_FORMAT=2' not in source:
        raise ValueError('missing format binding: '+recipe)
    return app, expected


def audit():
    raw, report, repository, tree = fixture()
    rows = []
    with tempfile.TemporaryDirectory(prefix='yaml-am-utils-audit-') as scratch:
        doc = Path(scratch)/'repository.yaml'; doc.write_bytes(tree[f'repositories/{RID}.yaml'])
        facts = subprocess.run(['sh', str(ROOT/'modules/catalog-yaml-reader.am'), 'asset_facts', str(doc)],
                               capture_output=True, check=True).stdout
        for recipe in AM_UTILS:
            app, suffix = selector(recipe)
            old = subprocess.run(['sh','-c',suffix], input=raw, capture_output=True, check=True,
                                 env={'APP':app,'PATH':'/usr/bin:/bin','LC_ALL':'C'}).stdout.decode().strip()
            selected = select_cohort(recipe,repository,'b'*40,now=utc(repository['observed_at']))
            if old != selected['asset']['url']:
                raise ValueError(('saved selector differs', recipe, old, selected))
            expected = ['b'*40,str(RID),selected['release_id'],selected['asset_id'],
                        selected['observed_at'],old]
            for command in (['mawk'],['gawk'],['busybox','awk']):
                result = subprocess.run([*command,'-f',str(ROOT/'modules/catalog-yaml-policy.am')],
                    input=facts,capture_output=True,check=True,
                    env={'PATH':'/usr/bin:/bin','LC_ALL':'C','AM_YAML_RECIPE':recipe,
                         'AM_YAML_REPOSITORY':str(RID),'AM_YAML_PIN':'b'*40,
                         'AM_YAML_NOW':repository['observed_at']})
                if result.stdout.decode().splitlines() != expected:
                    raise ValueError(('awk policy differs',command,recipe,result))
            rows.append(dict(recipe=recipe,recipe_sha256=hashlib.sha256((ROOT/'programs'/recipe).read_bytes()).hexdigest(),
                             release_id=selected['release_id'],asset_id=selected['asset_id'],url=old))
    return dict(body_sha256=report['body_sha256'], body_bytes=len(raw),
                observed_at=repository['observed_at'],repository_yaml_bytes=len(tree[f'repositories/{RID}.yaml']),
                comparisons=len(rows),awk_comparisons=3*len(rows),
                scope='Saved six-release/1750-asset response; no live or default-capacity evidence',rows=rows)


if __name__ == '__main__':
    result = audit()
    Path(__file__).with_name('am-utils-cohort-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'rows'},indent=2))
