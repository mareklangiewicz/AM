#!/usr/bin/env python3
"""Serial offline retention/staging/reader measurements; no network access."""
import copy
import datetime
import json
import os
import pathlib
import resource
import signal
import subprocess
import sys
import tempfile
import time
from experiment import document, repository
from retention import fresh, refresh

HERE = pathlib.Path(__file__).resolve().parent
MIB = 1024*1024


def capped():
    resource.setrlimit(resource.RLIMIT_AS, (384*MIB, 384*MIB))
    resource.setrlimit(resource.RLIMIT_CPU, (55, 55))
    resource.setrlimit(resource.RLIMIT_FSIZE, (64*MIB, 64*MIB))


def fixture(count, assets=8, title=32):
    obj = repository()
    sample = obj['releases']['456']
    asset = sample['assets']['789']
    sample['assets'] = {str(i): dict(asset) for i in range(1, assets+1)}
    sample['title'] = 'x'*title
    obj['releases'] = {str(i): copy.deepcopy(sample) for i in range(1, count+1)}
    return obj


def growth():
    previous = fixture(1)
    facts = copy.deepcopy(previous['releases']['1'])
    facts.pop('observed_at')
    history = []
    for day in range(1, 31):
        at = (datetime.datetime(2026, 11, 3) + datetime.timedelta(days=day)).strftime('%Y-%m-%dT%H:%M:%SZ')
        records = {str(i): facts for i in range((day-1)*100+2, day*100+2)}
        result = refresh(previous, [dict(received_at=at, releases=records, has_next=True, bytes=100, seconds=0)], attempted_at=at)
        assert result['collection']['status'] == 'ok'
        assert result['releases']['1'] == previous['releases']['1']
        previous = result
        history.append(dict(day=day, releases=len(result['releases']), bytes=len(document(result).encode())))
    assert not fresh(previous['releases']['1'], at)
    assert fresh(previous['releases']['3001'], at)
    # Discover exact merged size once, then test inclusive boundary and one byte below.
    seen = '2026-12-04T00:00:00Z'
    response = dict(received_at=seen, releases={'4000': facts}, has_next=True, bytes=1, seconds=0)
    proposed = refresh(previous, [response], attempted_at=seen)
    size = len(document(proposed).encode())
    exact = refresh(previous, [response], attempted_at=seen, max_catalog_bytes=size)
    refused = refresh(previous, [response], attempted_at=seen, max_catalog_bytes=size-1)
    assert exact == proposed
    assert refused['collection']['reason'] == 'collection_limit'
    assert refused['releases'] == previous['releases']
    assert refused['last_success'] == previous['last_success']
    return dict(history=history, exact_merge_bytes=size, one_byte_under_refused=True, untouched_old_release_stale=True)


def stage():
    # Build close to the proposed 16 MiB retained cap, then add 100 fetched IDs.
    sample = fixture(1)
    overhead = len(document(dict(sample, releases={})).encode())
    row = len(document(sample).encode())-overhead
    count = (16*MIB-overhead)//(row+10)-100
    previous = fixture(count)
    facts = copy.deepcopy(previous['releases']['1']); facts.pop('observed_at')
    response = dict(received_at='2026-11-04T00:00:00Z', releases={str(i): facts for i in range(count+1,count+101)}, has_next=True, bytes=1, seconds=0)
    result = refresh(previous, [response], attempted_at=response['received_at'])
    assert result['collection']['status'] == 'ok'
    return dict(previous_releases=count, previous_bytes=len(document(previous).encode()),
                fetched_releases=100, merged_bytes=len(document(result).encode()))


def measured(command, root, env=None, expected=0, file_limit=64*MIB):
    def child_limits():
        capped()
        resource.setrlimit(resource.RLIMIT_FSIZE, (file_limit, file_limit))
    metrics = root/'metrics'; output = root/'stdout'; err = root/'stderr'
    spool = root/'spool'; spool.mkdir(exist_ok=True)
    started = time.monotonic(); peak_spool = 0; timed_out = False
    metrics.unlink(missing_ok=True)
    with output.open('wb') as out, err.open('wb') as error:
        proc = subprocess.Popen(['/usr/bin/time','-f','%M %e','-o',str(metrics),*command],
                                stdout=out,stderr=error,env=dict(os.environ, TMPDIR=str(spool), **(env or {})),preexec_fn=child_limits, start_new_session=True)
        try:
            while proc.poll() is None:
                try:
                    peak_spool = max(peak_spool, sum(p.stat().st_size for p in spool.iterdir()))
                except FileNotFoundError:
                    pass  # Reader may unlink its completed private spool between samples.
                if time.monotonic()-started > 60:
                    os.killpg(proc.pid, signal.SIGKILL); proc.wait(); timed_out = True; break
                time.sleep(0.01)
        finally:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL); proc.wait()
    status = 124 if timed_out else proc.returncode
    allowed = expected if isinstance(expected, tuple) else (expected,)
    if (expected is None and status == 0) or (expected is not None and status not in allowed):
        raise RuntimeError(f'{command}: {proc.returncode}: {err.read_text()}')
    rss, seconds = metrics.read_text().splitlines()[-1].split() if metrics.exists() and metrics.stat().st_size else ('0', str(time.monotonic()-started))
    return dict(exit_status=status, peak_rss_kib=int(rss), seconds=float(seconds), output_bytes=output.stat().st_size,
                sampled_peak_spool_bytes=peak_spool)


def main():
    results = dict(limits=dict(address_space_mib=384,cpu_seconds=55,wall_seconds=60,file_mib=64))
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        for operation in ('growth','stage'):
            metrics = measured([sys.executable, str(HERE/'growth.py'), operation], root)
            results[operation] = dict(json.loads((root/'stdout').read_text()), **metrics)
            print(json.dumps({operation:results[operation]}),flush=True)
            (HERE/'growth-results.json').write_text(json.dumps(results,indent=2)+'\n')
        results['readers'] = []
        # Small, near-cap many-release and large embedded-asset shapes.
        for shape, obj in [('small',fixture(100)),('retained',fixture(10000)),('assets',fixture(1,assets=60000)),('long_scalar',fixture(1,title=65523)),('overlong_scalar',fixture(1,title=65524))]:
            path = root/'fixture.yaml'; path.write_text(document(obj))
            for awk in ('mawk','gawk','busybox'):
                shim=root/awk; shim.mkdir(exist_ok=True)
                (shim/'awk').write_text('#!/bin/sh\nexec '+awk+(' awk' if awk=='busybox' else '')+' "$@"\n')
                (shim/'awk').chmod(0o755)
                env=dict(PATH=str(shim)+':'+os.environ['PATH'])
                args=['rows','releases','observed_at','published_at','prerelease','title']
                if shape=='assets':
                    args=['rows','releases/1/assets','name','url','size','content_type']
                result=measured(['sh',str(HERE/'reader.sh'),args[0],str(path),*args[1:]],root,env,expected=2 if shape=='overlong_scalar' else (0,124,137,152))
                if result['exit_status']:
                    results['readers'].append(dict(awk=awk,shape=shape,input_bytes=path.stat().st_size,status='line_limit_refusal' if shape=='overlong_scalar' else 'process_limit_refusal',**result))
                    print(json.dumps(results['readers'][-1]),flush=True)
                    assert result['output_bytes']==0
                    (HERE/'growth-results.json').write_text(json.dumps(results,indent=2)+'\n')
                    continue
                expected_rows=60000 if shape=='assets' else len(obj['releases'])
                assert sum(1 for _ in (root/'stdout').open('rb')) == expected_rows
                result.update(awk=awk,shape=shape,input_bytes=path.stat().st_size,rows=expected_rows)
                results['readers'].append(result); print(json.dumps(result),flush=True)
                (HERE/'growth-results.json').write_text(json.dumps(results,indent=2)+'\n')
                if shape=='small':
                    refused=measured(['sh',str(HERE/'reader.sh'),args[0],str(path),*args[1:]],root,env,expected=None,file_limit=4096)
                    assert refused['output_bytes']==0
                    results['readers'].append(dict(awk=awk,shape='spool_file_limit',file_limit_bytes=4096,**refused))
                if shape=='retained':
                    bad=root/'bad.yaml'; bad.write_bytes(path.read_bytes()+b'unknown: "suffix"\n')
                    rejected=measured(['sh',str(HERE/'reader.sh'),args[0],str(bad),*args[1:]],root,env,expected=2)
                    assert rejected['output_bytes']==0
                    results['readers'].append(dict(awk=awk,shape='malformed_suffix',input_bytes=bad.stat().st_size,**rejected))
    (HERE/'growth-results.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__ == '__main__':
    if len(sys.argv)>1:
        print(json.dumps({'growth':growth,'stage':stage}[sys.argv[1]]()))
    else:
        main()
