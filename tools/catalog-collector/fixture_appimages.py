"""Saved upstream fixture loader; not an operational command."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
from fixture_facts import merge_attempts, utc
from bounded import normalize
from retention import refresh
from test_yaml_reader import SCHEMA
from yaml_publication import candidate_tree
from reference_policies import APPIMAGES, select_cohort

RESEARCH = ROOT/'docs/track/release-catalog/research'

def fixtures():
    sources = json.loads((ROOT/'docs/track/release-catalog/design/staged-manifest.json').read_text())['sources']
    from fixture_sunshine import RID, saved
    source, raw, report = saved()
    sources.append(source)
    by_request = {s['request_id']:s for s in sources}
    needed = {row['repository_id'] for row in APPIMAGES.values()}
    found = {RID: (source,raw,report,'docs/track/release-catalog/research/appimage-next-large-batch-20261102/evidence.tar.gz:release-0531')}
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
