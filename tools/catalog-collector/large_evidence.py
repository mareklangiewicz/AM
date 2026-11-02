"""Bounded, resumable metadata acquisition for the frozen thousand-recipe queue.

No redirects, retries, enrollment, publication or app downloads. Four independent
requests per wave bound release response allocation to 32 MB; each wave has a
300-second deadline. Individual transport limits are unchanged.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

from identity_batch import ROOT, OWN_REPOSITORY_ID, request
from migration_evidence import release_request
from throughput import audit

DIRECTORY = ROOT/'docs/track/release-catalog/research/appimage-next-large-batch-20261102'
PAYLOAD_HASH = '731895e0b2a03e5080118dc36d09bc8e67def862f3c2bd5412cb60eb88eaafa6'
OUTPUT = DIRECTORY/'live'


def saved(directory, url):
    if not directory.exists():
        return None
    report = json.loads((directory/'report.json').read_bytes())
    if report['url'] != url:
        raise ValueError('saved_url_mismatch')
    for kind, name in [('body', 'body.json'), ('headers', 'headers.txt')]:
        raw = (directory/name).read_bytes()
        if len(raw) != report[kind+'_bytes'] or hashlib.sha256(raw).hexdigest() != report[kind+'_sha256']:
            raise ValueError('saved_integrity')
    return report


def quota_stop(report, raw_headers=b''):
    headers = report.get('public_headers', {})
    remaining = headers.get('x-ratelimit-remaining', '')
    # curl may refuse an oversized Content-Length before fetch() parses its
    # retained headers. Inspect quota evidence without accepting the response or
    # modifying its original report. Duplicate/missing values still stop.
    if not remaining and report.get('curl_exit') == 63:
        matches = re.findall(rb'(?im)^x-ratelimit-remaining: ([0-9]+)\r$', raw_headers)
        statuses = re.findall(rb'(?m)^HTTP/1\.1 ([0-9]{3})[^\r]*\r$', raw_headers)
        if len(matches) == len(statuses) == 1 and statuses[0] == b'200':
            remaining = matches[0].decode('ascii')
    return (report.get('status') in (403, 429) or
            not remaining.isdecimal() or int(remaining) < 100)


def collect():
    raw = (DIRECTORY/'payload.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != PAYLOAD_HASH:
        raise ValueError('payload_changed')
    audit(raw, (ROOT/'docs/track/release-catalog/design/staged-manifest.json').read_bytes(),
          lambda p: (ROOT/p).read_bytes())
    payload = json.loads(raw)
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT/'.gitattributes').write_text('**/headers.txt -text\n')
    token = subprocess.run(['/usr/bin/gh', 'auth', 'token', '--hostname', 'github.com'],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True, timeout=10).stdout.strip()
    summary = dict(payload_sha256=PAYLOAD_HASH, started_at=datetime.now(timezone.utc).isoformat(),
                   policy='four-per-wave-no-redirects-no-retries', identities={}, releases=[],
                   stopped=None, received_bytes=0)
    end = time.monotonic()+3600

    def save():
        temp = OUTPUT/'batch.json.tmp'
        temp.write_text(json.dumps(summary, indent=2)+'\n')
        temp.replace(OUTPUT/'batch.json')

    def waves(jobs):
        for offset in range(0, len(jobs), 4):
            if time.monotonic() >= end or summary['received_bytes'] >= 1_000_000_000:
                summary['stopped'] = 'session_time_or_bytes'
                break
            deadline = min(end, time.monotonic()+300)
            selected = jobs[offset:offset+4]
            def execute(job):
                directory, url, send = job
                reused = saved(directory, url)
                return reused if reused is not None else send(deadline)
            with ThreadPoolExecutor(max_workers=4) as pool:
                reports = list(pool.map(execute, selected))
            for job, report in zip(selected, reports):
                summary['received_bytes'] += report['body_bytes']+report['headers_bytes']
                yield job, report
            save()
            print(json.dumps(dict(stage=stage, completed=min(offset+4, len(jobs)),
                                  total=len(jobs), bytes=summary['received_bytes'])), flush=True)
            if any(quota_stop(report, (job[0]/'headers.txt').read_bytes())
                   for job, report in zip(selected, reports)):
                summary['stopped'] = 'quota_or_missing_quota'
                break

    try:
        stage = 'identity'
        jobs = []
        # Preserve the frozen shared-caller priority; don't request an identity twice.
        urls = list(dict.fromkeys(row['identity_request'] for row in payload['rows']))
        for index, url in enumerate(urls, 1):
            directory = OUTPUT/f'identity-{index:04d}'
            jobs.append((directory, url, lambda deadline, u=url, d=directory:
                         request(u, d, deadline, own_id=OWN_REPOSITORY_ID, token=token)))
        for (directory, url, _), report in waves(jobs):
            summary['identities'][url] = dict(accepted=report['accepted'],
                repository_id=report.get('identity', {}).get('id'),
                evidence=str(directory.relative_to(ROOT)))
        if summary['stopped']:
            return summary
        stage = 'release'
        jobs, mappings = [], {}
        for index, row in enumerate(payload['rows'], 1):
            known = summary['identities'][row['identity_request']]
            if not known['accepted']:
                continue
            repository_id = known['repository_id']
            url = f'https://api.github.com/repositories/{repository_id}'+row['alias'][len(row['identity_request']):]
            directory = OUTPUT/f'release-{index:04d}'
            mappings[url] = dict(alias=row['alias'], repository_id=repository_id, fetch_url=url,
                                 identity_evidence=known['evidence'], evidence=str(directory.relative_to(ROOT)))
            jobs.append((directory, url, lambda deadline, u=url, d=directory, rid=repository_id:
                         release_request(u, rid, d, deadline, token=token)))
        for (directory, url, _), report in waves(jobs):
            summary['releases'].append(dict(mappings[url], accepted=report['accepted']))
        return summary
    finally:
        token = b''
        summary['completed_at'] = datetime.now(timezone.utc).isoformat()
        save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collect', action='store_true', required=True)
    parser.parse_args()
    result = collect()
    print(json.dumps(dict(identities=len(result['identities']), releases=len(result['releases']),
                          accepted=sum(r['accepted'] for r in result['releases']), stopped=result['stopped'])))
