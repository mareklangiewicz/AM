"""Recompute saved identity mappings and remaining scope without network access."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT/'tools/catalog-collector'))
from collector import Descriptor

OUT = Path(__file__).resolve().parent
payload_path = ROOT/'docs/track/release-catalog/research/remaining-appimage-preparation-20261102.json'
payload_raw = payload_path.read_bytes()
payload = json.loads(payload_raw)
summary = json.loads((OUT/'batch.json').read_bytes())
assert hashlib.sha256(payload_raw).hexdigest() == summary['payload_sha256']
assert len(summary['completed']) == 12 and not summary['accepted']
accepted = {}
failed = []
total_body = total_headers = 0
for index, attempt in enumerate(summary['completed']):
    assert attempt['url'] == payload['identity_requests'][index]
    directory = OUT/attempt['directory']
    report = json.loads((directory/'report.json').read_bytes())
    assert report['url'] == attempt['url'] and report['accepted'] == attempt['accepted']
    for kind, filename in [('body','body.json'), ('headers','headers.txt')]:
        raw = (directory/filename).read_bytes()
        assert len(raw) == report[kind+'_bytes']
        assert hashlib.sha256(raw).hexdigest() == report[kind+'_sha256']
    total_body += report['body_bytes']
    total_headers += report['headers_bytes']
    if attempt['accepted']:
        identity = json.loads((directory/'body.json').read_bytes())
        assert report['status'] == 200 and report['curl_exit'] == 0
        assert type(identity['id']) is int and identity['id'] > 0
        assert identity['id'] != summary['own_repository_id']
        assert identity['full_name'].lower() == attempt['url'].removeprefix('https://api.github.com/repos/').lower()
        assert identity['private'] is False and identity['visibility'] == 'public'
        assert report['identity'] == {k: identity[k] for k in ('id','full_name','private','visibility')}
        accepted[attempt['url']] = (identity, attempt['directory'])
    else:
        assert index == len(summary['completed']) - 1
        headers = (directory/'headers.txt').read_bytes().decode('latin-1').split('\r\n')
        location = [line.split(':',1)[1].strip() for line in headers if line.lower().startswith('location:')]
        failed.append(dict(url=attempt['url'], status=report.get('status'),
                           location=location, identity_accepted=False, directory=attempt['directory']))
rows = []
for row in payload['rows']:
    if row['identity_request'] not in accepted:
        continue
    identity, directory = accepted[row['identity_request']]
    url = 'https://api.github.com/repositories/' + str(identity['id']) + row['alias'][len(row['identity_request']):]
    descriptor = Descriptor(url)
    descriptor.validate(identity['id'])
    rows.append(dict(alias=row['alias'], repository_id=identity['id'], fetch_url=url,
                     request_id=descriptor.request_id, api_version=descriptor.api_version,
                     accept=descriptor.accept, initial_validators={},
                     identity_evidence=directory+'/report.json',
                     release_status='not-requested-not-enrolled', recipes=[r['path'] for r in row['recipes']]))
result = dict(schema=1, payload_sha256=summary['payload_sha256'],
              attempted_identities=12, accepted_identities=len(accepted),
              release_candidate_count=len(rows), recipe_count=sum(len(r['recipes']) for r in rows),
              body_bytes=total_body, header_bytes=total_headers,
              elapsed_request_seconds=sum(json.loads((OUT/a['directory']/'report.json').read_text())['elapsed_seconds'] for a in summary['completed']),
              failed=failed, release_candidates=rows,
              unattempted_identity_requests=payload['identity_requests'][12:])
assert len(result['unattempted_identity_requests']) == 36
(OUT/'audit.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('release_candidates','unattempted_identity_requests')}, indent=2))
