"""Bounded evidence for the frozen AppImage batch; never publishes or runs apps."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import subprocess

from collector import Descriptor
from identity_batch import ROOT, OWN_REPOSITORY_ID, fetch, request, load_payload
from storage import content

PREVIOUS = ROOT/'docs/track/release-catalog/research/remaining-identities-20261102-network'


def saved_identities(payload):
    summary = json.loads((PREVIOUS/'batch.json').read_bytes())
    known, skipped = {}, set()
    assert len(summary['completed']) == 12
    for i, attempt in enumerate(summary['completed']):
        assert attempt['url'] == payload['identity_requests'][i]
        directory = PREVIOUS/attempt['directory']
        report = json.loads((directory/'report.json').read_bytes())
        raw = (directory/'body.json').read_bytes()
        assert hashlib.sha256(raw).hexdigest() == report['body_sha256']
        assert hashlib.sha256((directory/'headers.txt').read_bytes()).hexdigest() == report['headers_sha256']
        if report['accepted']:
            value = json.loads(raw)
            assert value['full_name'].lower() == attempt['url'].split('/repos/')[1].lower()
            assert value['private'] is False and value['visibility'] == 'public'
            assert type(value['id']) is int and value['id'] != OWN_REPOSITORY_ID
            known[attempt['url']] = dict(repository_id=value['id'], evidence=str(directory.relative_to(ROOT)))
        else:
            skipped.add(attempt['url'])
    return known, skipped


def release_request(url, repository_id, out, deadline, *, token=None):
    descriptor = Descriptor(url)
    descriptor.validate(repository_id)
    def validate(value, raw):
        content(raw, dict(url=url))
        releases = value if type(value) is list else [value]
        return dict(descriptor=dict(url=url, api_version=descriptor.api_version,
                                    accept=descriptor.accept, request_id=descriptor.request_id),
                    release_count=len(releases), asset_count=sum(len(r['assets']) for r in releases))
    return fetch(url, out, deadline, validate_value=validate, body_cap=8_000_000, token=token)


def collect(out, *, authenticated=False):
    out = out.resolve()
    payload = load_payload(check_recipes=False)
    known, skipped = saved_identities(payload)
    out.mkdir(exist_ok=True)
    (out/'.gitattributes').write_text('**/headers.txt -text\n')
    summary = dict(started_at=datetime.now(timezone.utc).isoformat(),
                   policy='isolate-endpoint-failures-no-retries-no-redirects',
                   identities=known, excluded_identity_urls=sorted(skipped), releases=[], failures=[], pending=[])
    deadline = time.monotonic()+3000
    # Explicit credential acquisition: never persisted or placed in argv/environment.
    token = None
    if authenticated:
        token = subprocess.run(['/usr/bin/gh', 'auth', 'token', '--hostname', 'github.com'],
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                               check=True, timeout=10).stdout.strip()
    quota_exhausted = False
    def save():
        temp = out/'batch.json.tmp'
        temp.write_text(json.dumps(summary, indent=2)+'\n')
        temp.replace(out/'batch.json')
    def quota(report):
        if report.get('reused'):
            return False
        headers = report.get('public_headers', {})
        return headers.get('x-ratelimit-remaining') == '0' or report.get('status') in (403, 429)
    def obtain(directory, url, send):
        if directory.exists():
            # Resume a bookkeeping interruption using exact saved bytes, never another GET.
            report = json.loads((directory/'report.json').read_bytes())
            assert report['url'] == url
            for kind, name in [('body', 'body.json'), ('headers', 'headers.txt')]:
                raw = (directory/name).read_bytes()
                assert len(raw) == report[kind+'_bytes']
                assert hashlib.sha256(raw).hexdigest() == report[kind+'_sha256']
            report = dict(report, reused=True)
            return report
        return send()
    save()
    try:
        for index, row in enumerate(payload['rows']):
            identity_url = row['identity_request']
            if identity_url in skipped:
                continue
            if quota_exhausted or time.monotonic() >= deadline:
                summary['pending'].append(row['alias'])
                continue
            if identity_url not in known:
                directory = out/f'identity-{index+1:02d}'
                report = obtain(directory, identity_url, lambda: request(identity_url, directory, deadline, own_id=OWN_REPOSITORY_ID, token=token))
                quota_exhausted = quota(report)
                if not report['accepted']:
                    skipped.add(identity_url)
                    summary['failures'].append(dict(stage='identity', alias=row['alias'],
                                                    report=str(directory.relative_to(ROOT))+'/report.json'))
                    save()
                    continue
                known[identity_url] = dict(repository_id=report['identity']['id'], evidence=str(directory.relative_to(ROOT)))
                save()
                if quota_exhausted:
                    summary['pending'].append(row['alias'])
                    continue
            mapping = known[identity_url]
            url = 'https://api.github.com/repositories/'+str(mapping['repository_id'])+row['alias'][len(identity_url):]
            directory = out/f'release-{index+1:02d}'
            report = obtain(directory, url, lambda: release_request(url, mapping['repository_id'], directory, deadline, token=token))
            quota_exhausted = quota(report)
            result = dict(alias=row['alias'], repository_id=mapping['repository_id'],
                          fetch_url=url, identity_evidence=mapping['evidence'],
                          evidence=str(directory.relative_to(ROOT)), accepted=report['accepted'])
            summary['releases'].append(result)
            if not report['accepted']:
                summary['failures'].append(dict(stage='release', alias=row['alias'],
                                                report=str(directory.relative_to(ROOT))+'/report.json'))
            save()
    finally:
        summary['completed_at'] = datetime.now(timezone.utc).isoformat()
        summary['quota_exhausted'] = quota_exhausted
        save()
    print(json.dumps(dict(identities=len(known), releases=len(summary['releases']),
                          accepted=sum(r['accepted'] for r in summary['releases']),
                          failures=summary['failures'], pending=len(summary['pending']),
                          quota_exhausted=quota_exhausted),indent=2))
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--authenticated', action='store_true')
    args = parser.parse_args()
    collect(args.output, authenticated=args.authenticated)
