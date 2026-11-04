#!/usr/bin/env python3
"""Audit reviewed AppImage URL policies on saved upstream JSON, offline only."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/catalog-collector'))
from attempt_adapter import merge_attempts, utc
from bounded import normalize
from retention import refresh
from experiment import SCHEMA
from yaml_publication import candidate_tree
from yaml_recipe_cohort import APPIMAGES, select_cohort
from recipe_cohort import legacy

RESEARCH = ROOT/'docs/track/release-catalog/research'


def fixtures():
    sources = json.loads((ROOT/'docs/track/release-catalog/design/staged-manifest.json').read_text())['sources']
    by_request = {s['request_id']:s for s in sources}
    needed = {row['repository_id'] for row in APPIMAGES.values()}
    found = {}
    for report_path in sorted(RESEARCH.glob('*/release-*/report.json')) + [RESEARCH/'brave-release-20261031/report.json']:
        report = json.loads(report_path.read_text())
        request = report.get('descriptor', {}).get('request_id')
        if request not in by_request:
            continue
        source = by_request[request]
        rid = source['repository_id']
        if rid not in needed or (rid in found and
                (not found[rid][0]['url'].endswith('/latest') or source['url'].endswith('/latest'))):
            continue
        raw = report_path.with_name('body.json').read_bytes()
        found[rid] = (source, raw, report, str(report_path.relative_to(ROOT)))
    archive_path = RESEARCH/'supervised-baseline-40529551070-evidence.tar.gz'
    with tarfile.open(archive_path) as archive:
        prefix = 'supervised-baseline-40529551070/'
        report = json.load(archive.extractfile(prefix+'report.json'))
        for record in report['attempts']:
            rid = record['repository_id']
            if rid not in needed or rid in found or record['descriptor']['url'].endswith('/latest'):
                continue
            source = next(s for s in sources if s['repository_id']==rid and not s['url'].endswith('/latest'))
            raw = archive.extractfile(prefix+record['request_id']+'.body').read()
            found[rid] = (source, raw, record, str(archive_path.relative_to(ROOT)))
    if set(found) != needed:
        raise ValueError(('missing saved list fixtures', sorted(needed-set(found))))
    result = {}
    for rid, (source, raw, report, location) in found.items():
        if len(raw) != report['body_bytes'] or hashlib.sha256(raw).hexdigest() != report['body_sha256']:
            raise ValueError(('saved body identity', location))
        started = report.get('request_started_at', report.get('started_at'))
        completed = report.get('response_completed_at', report.get('completed_at'))
        attempt = dict(repository_id=rid, descriptor=report['descriptor'], body=raw,
                       outcome='response', status=report['status'], request_started_at=started,
                       response_completed_at=completed)
        alias = source['aliases'][0]
        initial = dict(format=2, schema=SCHEMA, repository_id=rid,
            repository=alias.split('/repos/',1)[1].split('/releases',1)[0])
        attempted_at = utc(started).strftime('%Y-%m-%dT%H:%M:%SZ')
        if source['url'].endswith('/latest'):
            # A saved latest object supplies ONE release's facts only. This is
            # not a fabricated list response or evidence of list acquisition.
            response = dict(received_at=utc(completed).strftime('%Y-%m-%dT%H:%M:%SZ'),
                releases=normalize([json.loads(raw)],100),has_next=True,bytes=len(raw),seconds=0)
            repository = refresh(initial,[response],attempted_at=attempted_at,max_catalog_bytes=2097152)
        else:
            repository = merge_attempts(initial, [(attempt, True)], attempted_at=attempted_at,
                page_size=100 if 'per_page=100' in source['url'] else 30, max_catalog_bytes=2097152)
        if repository['collection']['status'] != 'ok':
            raise ValueError(('normalization refused', location, repository['collection']))
        tree = candidate_tree({'fixture':rid}, {str(rid):repository}, schema=SCHEMA, max_file_bytes=2097152)
        result[rid] = dict(raw=raw, report=report, repository=repository, tree=tree, location=location,endpoint='latest_singleton' if source['url'].endswith('/latest') else 'list')
    return result


def latest_fixtures():
    sources = json.loads((ROOT/'docs/track/release-catalog/design/staged-manifest.json').read_text())['sources']
    needed = {row['repository_id'] for row in APPIMAGES.values() if row['endpoint']=='latest'}
    requests = {s['request_id']:s['repository_id'] for s in sources
                if s['url'].endswith('/latest') and s['repository_id'] in needed}
    result = {}
    for path in sorted(RESEARCH.glob('*/release-*/report.json')):
        report = json.loads(path.read_text())
        request = report.get('descriptor',{}).get('request_id')
        if request not in requests:
            continue
        raw = path.with_name('body.json').read_bytes()
        if len(raw)!=report['body_bytes'] or hashlib.sha256(raw).hexdigest()!=report['body_sha256']:
            raise ValueError(('saved latest body identity',str(path)))
        result[requests[request]] = dict(raw=raw,report=report,location=str(path.relative_to(ROOT)))
    if set(result)!=set(requests.values()):
        raise ValueError('missing saved latest bodies')
    return result


def audit():
    saved = fixtures()
    latest = latest_fixtures()
    rows = []
    with tempfile.TemporaryDirectory(prefix='yaml-appimage-audit-') as scratch:
        facts = {}
        for rid, fixture in saved.items():
            path = Path(scratch)/f'{rid}.yaml'
            path.write_bytes(fixture['tree'][f'repositories/{rid}.yaml'])
            facts[rid] = subprocess.run(['sh',str(ROOT/'modules/catalog-yaml-reader.am'),
                'asset_facts',str(path)],capture_output=True,check=True).stdout
        for recipe, policy in APPIMAGES.items():
            rid = policy['repository_id']; fixture = saved[rid]; repository = fixture['repository']
            original = latest[rid] if policy['endpoint']=='latest' else fixture
            old = legacy(recipe, original['raw'])
            try:
                selected = select_cohort(recipe,repository,'b'*40,now=utc(repository['observed_at']))
            except ValueError as error:
                if str(error) != 'no_matching_asset':
                    raise
                selected = None
            expected = None if selected is None else ['b'*40,str(rid),selected['release_id'],
                        selected['asset_id'],selected['observed_at'],selected['asset']['url']]
            for command in (['mawk'],['gawk'],['busybox','awk']):
                result = subprocess.run([*command,'-f',str(ROOT/'modules/catalog-yaml-policy.am')],
                    input=facts[rid],capture_output=True,
                    env={'PATH':'/usr/bin:/bin','LC_ALL':'C','AM_YAML_RECIPE':recipe,
                         'AM_YAML_REPOSITORY':str(rid),'AM_YAML_PIN':'b'*40,
                         'AM_YAML_NOW':repository['observed_at']})
                if expected is None:
                    if result.returncode == 0 or result.stdout or b'no_matching_asset' not in result.stderr:
                        raise ValueError(('awk refusal differs',command,recipe,result))
                elif result.returncode != 0 or result.stdout.decode().splitlines() != expected:
                    raise ValueError(('awk policy differs',command,recipe,result))
            proposed = selected['asset']['url'] if selected else ''
            rows.append(dict(recipe=recipe,recipe_sha256=hashlib.sha256((ROOT/'programs'/recipe).read_bytes()).hexdigest(),
                repository_id=rid,legacy_evidence=original['location'],
                legacy_body_sha256=original['report']['body_sha256'],
                legacy_url=old,proposed_url=proposed,equal=old==proposed,
                selected_release_id=selected['release_id'] if selected else None,
                selected_asset_id=selected['asset_id'] if selected else None))
    evidence = [dict(repository_id=rid,location=f['location'],body_sha256=f['report']['body_sha256'],
        body_bytes=len(f['raw']),endpoint=f['endpoint'],observed_at=f['repository']['observed_at'],
        releases=len(f['repository']['releases']),
        assets=sum(len(r['assets']) for r in f['repository']['releases'].values()),
        repository_yaml_bytes=len(f['tree'][f'repositories/{rid}.yaml'])) for rid,f in sorted(saved.items())]
    return dict(scope='Hash-checked saved pages only; no current upstream or default/retained-capacity guarantee',
                comparisons=len(rows),awk_comparisons=3*len(rows),equal=sum(r['equal'] for r in rows),
                evidence=evidence,rows=rows)


if __name__ == '__main__':
    result = audit()
    Path(__file__).with_name('appimage-cohort-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows','evidence')},indent=2))
    for row in result['rows']:
        if not row['equal']:
            print(json.dumps(row))
