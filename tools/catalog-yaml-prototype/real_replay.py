#!/usr/bin/env python3
"""Replay tracked real response evidence, never request it again."""
import hashlib
import json
import os
import pathlib
import re
import subprocess
import tempfile
import time

from attempt_adapter import merge_attempts, refresh_from_attempts, utc
from experiment import SCHEMA
from yaml_publication import git, load_local, publish_local

HERE = pathlib.Path(__file__).resolve().parent
EVIDENCE = HERE.parents[1]/'docs/track/release-catalog/research/appimage-batch-20261102'


def saved_inputs():
    identities = {}
    for path in EVIDENCE.glob('identity-*/body.json'):
        obj = json.loads(path.read_bytes())
        if 'full_name' in obj:  # Redirect/error identity bodies have no release replay.
            identities[obj['id']] = obj['full_name']
    repositories = {}
    pages = {}
    records = []
    excluded = []
    for report_path in sorted(EVIDENCE.glob('release-*/report.json')):
        report = json.loads(report_path.read_bytes())
        raw = report_path.with_name('body.json').read_bytes()
        assert report['accepted'] and report['status']==200
        assert len(raw)==report['body_bytes']
        assert hashlib.sha256(raw).hexdigest()==report['body_sha256']
        if report['url'].endswith('/latest'):
            excluded.append(dict(evidence=str(report_path.relative_to(HERE.parents[1])),reason='latest endpoint, not a list page'))
            continue
        rid = re.fullmatch(r'https://api.github.com/repositories/([1-9][0-9]*)/releases(?:\?per_page=100)?',report['url'])[1]
        page_size = 100 if '?per_page=100' in report['url'] else 30
        assert rid not in repositories
        attempt = dict(repository_id=int(rid),descriptor=dict(url=report['url']),
                       request_started_at=report['started_at'],response_completed_at=report['completed_at'],
                       body=raw,status=report['status'],outcome='response')
        # Existing evidence uses GitHub's default 30-record list page. This is
        # explicit fixture pagination metadata, not a production Link parser.
        has_next = 'rel="next"' in report['public_headers'].get('link','')
        pages[rid] = [(attempt,has_next)]
        name = identities.get(int(rid))
        if name is None:  # Earlier-enrolled identities need no new acquisition.
            name = re.match(r'https://github.com/([^/]+/[^/]+)/releases/',json.loads(raw)[0]['html_url'])[1]
        initial = dict(format=2,schema=SCHEMA,repository_id=int(rid),repository=name)
        at = utc(report['started_at']).strftime('%Y-%m-%dT%H:%M:%SZ')
        result = merge_attempts(initial,pages[rid],attempted_at=at,page_size=page_size,
                                max_catalog_bytes=2*1024*1024)
        assert result['collection']['status']=='ok', (rid,result['collection'])
        assert result['observed_at']==utc(report['completed_at']).strftime('%Y-%m-%dT%H:%M:%SZ')
        originals = {str(item['id']):item for item in json.loads(raw) if not item['draft']}
        assert list(result['releases']) == sorted(originals,key=int)
        for release_id, facts in result['releases'].items():
            original = originals[release_id]
            assert (facts['tag'],facts['url'],facts['published_at'],facts['prerelease']) == (
                original['tag_name'],original['html_url'],original['published_at'],original['prerelease'])
            assert facts.get('title') == original.get('name')
            assert set(facts['assets']) == {str(asset['id']) for asset in original['assets']}
            for asset in original['assets']:
                normalized = facts['assets'][str(asset['id'])]
                assert (normalized['name'],normalized['url'],normalized['size'],normalized['content_type']) == (
                    asset['name'],asset['browser_download_url'],asset['size'],asset['content_type'])
        repositories[rid] = result
        records.append(dict(repository_id=rid,evidence=str(report_path.relative_to(HERE.parents[1])),
                            body_sha256=report['body_sha256'],raw_bytes=len(raw),
                            releases=len(result['releases']),
                            assets=sum(len(r['assets']) for r in result['releases'].values()),
                            has_next=has_next,page_size=page_size))
    assert len(records)==41 and len(excluded)==3
    return repositories,pages,records,excluded


def main():
    started = time.monotonic()
    repositories,pages,records,excluded = saved_inputs()
    apps = {'source-'+rid:int(rid) for rid in repositories}
    with tempfile.TemporaryDirectory(prefix='yaml-real-replay-') as directory:
        root = pathlib.Path(directory)
        repo = root/'git'
        repo.mkdir()
        git(repo,'init','--bare')
        options = dict(schema=SCHEMA,max_file_bytes=2*1024*1024)
        before = publish_local(repo,apps,repositories,expected_parent=None,**options)
        print('Published 41-source saved-response snapshot',flush=True)
        assert load_local(repo,before,max_file_bytes=options['max_file_bytes']) == (apps,repositories)
        # Original attempts happened at different times. A common scope start
        # before all of them preserves their distinct per-source receipt times.
        attempt_start = min(obj['collection']['attempted_at'] for obj in repositories.values())
        after = before
        for size in (30,100):
            selected = {item['repository_id']:pages[item['repository_id']] for item in records if item['page_size']==size}
            after = refresh_from_attempts(repo,after,selected,attempted_at=attempt_start,page_size=size,**options)
        _, loaded = load_local(repo,after,max_file_bytes=options['max_file_bytes'])
        for rid, original in repositories.items():
            for key in ('releases','observed_at','last_success'):
                assert loaded[rid][key]==original[key],(rid,key)
            raw = git(repo,'show',after+':repositories/'+rid+'.yaml')
            record = next(item for item in records if item['repository_id']==rid)
            record['yaml_bytes'] = len(raw)
            record['yaml_sha256'] = hashlib.sha256(raw).hexdigest()
        largest = max(records,key=lambda item:item['yaml_bytes'])
        rid = largest['repository_id']
        snapshot = root/'snapshot'
        (snapshot/'repositories').mkdir(parents=True)
        for name in ('apps.yaml','repositories/'+rid+'.yaml'):
            (snapshot/name).write_bytes(git(repo,'show',after+':'+name))
        measurements = []
        expected = None
        for tool in ('mawk','gawk','busybox'):
            shim = root/tool
            shim.mkdir()
            (shim/'awk').write_text('#!/bin/sh\nexec '+tool+(' awk' if tool=='busybox' else '')+' "$@"\n')
            (shim/'awk').chmod(0o755)
            tick = time.monotonic()
            run = subprocess.run(['/bin/dash',str(HERE/'browse.sh'),str(snapshot),'source-'+rid],
                                 env=dict(os.environ,PATH=str(shim)+':'+os.environ['PATH']),
                                 capture_output=True,timeout=60)
            assert run.returncode==0,run.stderr
            assert run.stdout.count(b'\n')==largest['releases']
            if expected is None:
                expected=run.stdout
            assert run.stdout==expected
            measurements.append(dict(awk=tool,seconds=round(time.monotonic()-tick,3),
                                     rows=largest['releases'],sha256=hashlib.sha256(run.stdout).hexdigest()))
            print(json.dumps(measurements[-1]),flush=True)
    result = dict(sources=len(records),raw_bytes=sum(item['raw_bytes'] for item in records),
                  yaml_bytes=sum(item['yaml_bytes'] for item in records),
                  releases=sum(item['releases'] for item in records),
                  assets=sum(item['assets'] for item in records),
                  largest_repository=rid,largest_yaml_bytes=largest['yaml_bytes'],
                  replay_seconds=round(time.monotonic()-started,3),
                  largest_browse=measurements,excluded=excluded,cases=records)
    (HERE/'real-replay-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'}),flush=True)


if __name__ == '__main__':
    main()
