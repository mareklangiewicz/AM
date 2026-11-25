"""Saved upstream fixture loader; not an operational command."""
import hashlib
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
from fixture_facts import utc
from fixture_catalog import repository
from reference_policies import APPIMAGES

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
        if report['status'] != 200:
            raise ValueError(('saved response status', location))
        completed = report.get('response_completed_at', report.get('completed_at'))
        name = source['aliases'][0].split('/repos/',1)[1].split('/releases',1)[0]
        received = utc(completed).strftime('%Y-%m-%dT%H:%M:%SZ')
        if source['url'].endswith('/latest'):
            # A saved latest object supplies ONE release's facts only. This is
            # not a fabricated list response or evidence of list acquisition.
            result[rid] = repository(rid, name, [json.loads(raw)], received, complete=False)
        else:
            releases = json.loads(raw)
            page = 100 if 'per_page=100' in source['url'] else 30
            result[rid] = repository(rid, name, releases, received, complete=len(releases) < page)
    return result
