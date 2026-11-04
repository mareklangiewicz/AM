"""Hash-checked saved Sunshine list response; no HTTP or manufactured history."""
import hashlib
import json
from pathlib import Path
import tarfile

ROOT=Path(__file__).resolve().parents[2]
RID=438803890
ARCHIVE=ROOT/'docs/track/release-catalog/research/appimage-next-large-batch-20261102/evidence.tar.gz'
REPORT='./release-0531/report.json'
BODY='./release-0531/body.json'
BODY_SHA256='ea360c2ecb2b4ca1b77a861ef59c8ba63b7433f96a0b83662ccaf3ba6d3f72ab'


def saved():
    with tarfile.open(ARCHIVE) as archive:
        report=json.load(archive.extractfile(REPORT))
        body=archive.extractfile(BODY).read()
    if (report['status']!=200 or report['body_bytes']!=len(body) or
            report['body_sha256']!=BODY_SHA256 or hashlib.sha256(body).hexdigest()!=BODY_SHA256 or
            report['url']!=f'https://api.github.com/repositories/{RID}/releases'):
        raise ValueError('Sunshine saved evidence mismatch')
    source=next(s for s in json.loads((ROOT/'docs/track/release-catalog/design/yaml-manifest.json').read_text())['sources']
                if s['repository_id']==RID)
    return source,body,report


def observation():
    from attempt_adapter import merge_attempts, utc
    from experiment import SCHEMA
    source,body,report=saved()
    attempt=dict(repository_id=RID,descriptor=report['descriptor'],body=body,outcome='response',
                 status=200,request_started_at=report['started_at'],response_completed_at=report['completed_at'])
    repository=merge_attempts(dict(format=2,schema=SCHEMA,repository_id=RID,repository='LizardByte/Sunshine'),
        [(attempt,True)],attempted_at=utc(report['started_at']).strftime('%Y-%m-%dT%H:%M:%SZ'),
        page_size=30,max_catalog_bytes=2097152)
    if repository['collection']['status']!='ok':raise ValueError('Sunshine saved normalization refused')
    return source,body,report,repository
