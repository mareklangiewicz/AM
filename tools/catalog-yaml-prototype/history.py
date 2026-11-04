#!/usr/bin/env python3
"""Offline paired Git histories: identical effective facts, two timestamp encodings.

32 snapshots per case, fixed identity/commit clocks, one file, no network/remotes.
Git repack is serial with one thread and a 32 MiB delta-window memory setting.
"""
import copy
import datetime
import json
import os
import pathlib
import resource
import subprocess
import tempfile
from experiment import document, repository
from retention import observation, refresh

HERE = pathlib.Path(__file__).resolve().parent


def git(root, *args, **options):
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null')
    return subprocess.run(['git', '-C', str(root), *args], env=env,
                          check=True, capture_output=True, **options).stdout


def facts(rid):
    sample = copy.deepcopy(repository()['releases']['456'])
    sample.pop('observed_at')
    sample['tag'] = 'v'+str(rid)
    sample['title'] = 'Release '+str(rid)
    sample['url'] = 'https://github.com/example/app/releases/tag/v'+str(rid)
    asset = sample['assets']['789']
    sample['assets'] = {str(i): dict(asset, name=f'app-{rid}-{i}.AppImage', size=rid*100+i)
                        for i in range(1, 9)}
    return sample


def expand(obj):
    return {rid: dict(observed_at=observation(record,obj['observed_at']),
                      **{k:v for k,v in record.items() if k!='observed_at'})
            for rid,record in obj['releases'].items()}


def snapshots(case):
    count = 100 if case=='same_page_100' else 1000
    shared = repository()
    initial = '2026-11-03T00:59:30Z'
    shared['observed_at'] = initial
    shared['releases'] = {str(i):facts(i) for i in range(1,count+1)}
    explicit = {k:copy.deepcopy(v) for k,v in shared.items() if k!='observed_at'}
    explicit['releases'] = {str(i):dict(observed_at=initial, **facts(i)) for i in range(1,count+1)}
    yield explicit, shared
    for day in range(1,32):
        date = datetime.datetime(2026,11,3)+datetime.timedelta(days=day)
        attempt = date.strftime('%Y-%m-%dT00:00:00Z')
        ids = list(range(1, count+1)) if case=='ten_pages_1000' else list(range(1,101))
        if case=='rolling_page_100':
            ids = list(range(901+day*10,1001+day*10))
        pages = []
        for index in range(0,len(ids),100):
            at = (date+datetime.timedelta(seconds=index//100+1)).strftime('%Y-%m-%dT%H:%M:%SZ')
            pages.append(dict(received_at=at, releases={str(i):facts(i) for i in ids[index:index+100]},
                              has_next=index+100<len(ids) or case!='ten_pages_1000', bytes=1, seconds=0))
        # A failed attempt must add no timestamp churn in either encoding.
        failed = case=='rolling_page_100' and day%7==0
        if failed:
            pages.append(dict(error='transport',bytes=0,seconds=0))
        limit = 'all' if case=='ten_pages_1000' or failed else 1
        updated = refresh(shared,pages,attempted_at=attempt,page_limit=limit)
        assert updated['collection']['status'] == ('failed' if failed else 'ok')
        # Independent explicit observation oracle: update only response inclusions
        # after scope success; do not derive expected times from shared defaults.
        expected = copy.deepcopy(explicit['releases'])
        if not failed:
            for page in pages:
                for rid, record in page['releases'].items():
                    expected[rid] = dict(observed_at=page['received_at'], **record)
        expected = {rid:expected[rid] for rid in sorted(expected,key=int)}
        assert expand(updated) == expected
        explicit = {k:copy.deepcopy(v) for k,v in updated.items() if k not in ('observed_at','releases')}
        explicit['releases'] = expected
        shared = updated
        yield explicit,shared


def replay(case, root):
    variants = {}
    streams = {}
    totals = {'explicit':0,'shared':0}
    initial = {}
    final = {}
    try:
        for variant in totals:
            path = root/variant
            git(root,'init','--bare','--quiet',str(path))
            variants[variant] = path
            streams[variant] = (root/(variant+'.import')).open('wb')
        for index, pair in enumerate(snapshots(case)):
            for variant, obj in zip(('explicit','shared'),pair):
                data = document(obj).encode()
                totals[variant] += len(data)
                if index==0:
                    initial[variant] = len(data)
                final[variant] = len(data)
                # Identical commit metadata/order in both histories.
                stamp = 1793664000+index*86400
                message = f'snapshot {index}\n'.encode()
                stream = streams[variant]
                stream.write(f'commit refs/heads/trial\ncommitter Experiment <offline@example.invalid> {stamp} +0000\ndata {len(message)}\n'.encode())
                stream.write(message)
                stream.write(f'M 100644 inline catalog.yaml\ndata {len(data)}\n'.encode())
                stream.write(data)
                stream.write(b'\n')
        for stream in streams.values():
            stream.write(b'done\n');stream.close()
        result = dict(case=case,snapshots=index+1,variants={})
        for variant, path in variants.items():
            with (root/(variant+'.import')).open('rb') as source:
                git(path,'fast-import','--quiet','--date-format=raw',stdin=source)
            commits = git(path,'rev-list','--reverse','refs/heads/trial').decode().splitlines()
            assert len(commits)==index+1
            changes = git(path,'log','--format=','--numstat','refs/heads/trial','^'+commits[0]).decode().splitlines()
            added = deleted = 0
            for line in changes:
                if line:
                    a,d,name = line.split('\t')
                    assert name=='catalog.yaml'
                    added+=int(a); deleted+=int(d)
            git(path,'-c','pack.threads=1','-c','pack.windowMemory=32m',
                'repack','-adf','--depth=50','--window=10')
            pack = sum(p.stat().st_size for p in (path/'objects'/'pack').glob('*.pack'))
            pack_index = sum(p.stat().st_size for p in (path/'objects'/'pack').glob('*.idx'))
            result['variants'][variant] = dict(initial_snapshot_bytes=initial[variant],final_snapshot_bytes=final[variant],
                                              serialized_history_bytes=totals[variant],added_lines_after_initial=added,
                                              deleted_lines_after_initial=deleted,pack_bytes=pack,index_bytes=pack_index,packed_objects_bytes=pack+pack_index)
        a,b = result['variants']['explicit'],result['variants']['shared']
        result['savings'] = {key:dict(bytes=a[key]-b[key],percent=round(100*(a[key]-b[key])/a[key],2))
                             for key in ('final_snapshot_bytes','serialized_history_bytes','pack_bytes','packed_objects_bytes')}
        return result
    finally:
        for stream in streams.values():
            if not stream.closed:
                stream.close()


def main():
    # Fixed-size local replay, with allocation/file guards inherited by Git.
    resource.setrlimit(resource.RLIMIT_AS, (384*1024*1024,384*1024*1024))
    resource.setrlimit(resource.RLIMIT_FSIZE, (128*1024*1024,128*1024*1024))
    results = dict(git_version=subprocess.run(['git','--version'],capture_output=True,text=True,check=True).stdout.strip(),cases=[])
    with tempfile.TemporaryDirectory() as directory:
        for case in ('same_page_100','retained_1000_page_100','rolling_page_100','ten_pages_1000'):
            root = pathlib.Path(directory)/case;root.mkdir()
            result = replay(case,root)
            results['cases'].append(result)
            print(json.dumps(result),flush=True)
            (HERE/'history-results.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__ == '__main__':
    main()
