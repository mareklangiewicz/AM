#!/usr/bin/env python3
"""Direct reader measurements; /usr/bin/time is a measurement tool only."""
import hashlib
import json
import os
import pathlib
import subprocess
import tempfile
import time

from experiment import document
from growth import fixture
from reader_budget_measure import expected_hash

HERE = pathlib.Path(__file__).resolve().parent


def main():
    results = []
    with tempfile.TemporaryDirectory(prefix='yaml-simple-') as directory:
        root = pathlib.Path(directory)
        for count in (100, 500, 1000):
            obj = fixture(count, assets=8, title=32)
            for rid, record in obj['releases'].items():
                if int(rid) % 10:
                    record.pop('observed_at', None)
            expected, rows = expected_hash(obj)
            source = root/'source.yaml'
            source.write_text(document(obj))
            for tool in ('mawk', 'gawk', 'busybox'):
                shim = root/tool
                shim.mkdir(exist_ok=True)
                (shim/'awk').write_text('#!/bin/sh\nexec '+tool+(' awk' if tool=='busybox' else '')+' "$@"\n')
                (shim/'awk').chmod(0o755)
                environment = dict(os.environ, PATH=str(shim)+':'+os.environ['PATH'],
                                   TMPDIR=str(root), AM_YAML_MAX_INPUT_BYTES='2097152',
                                   AM_YAML_MAX_OUTPUT_BYTES='2097152')
                output = root/'output'
                metrics = root/'metrics'
                started = time.monotonic()
                with output.open('wb') as stream:
                    run = subprocess.run(['/usr/bin/time','-f','%U %S %M','-o',str(metrics),
                                          '/bin/dash',str(HERE/'reader.sh'),'rows',str(source),
                                          'releases','observed_at','published_at','prerelease','title'],
                                         env=environment,stdout=stream,stderr=subprocess.PIPE,
                                         timeout=30)
                elapsed = time.monotonic()-started
                assert run.returncode == 0, (tool, count, run.stderr)
                data = output.read_bytes()
                assert hashlib.sha256(data).hexdigest() == expected
                assert data.count(b'\n') == rows
                user, system, rss = metrics.read_text().split()
                item = dict(awk=tool,releases=count,assets_per_release=8,
                            input_bytes=source.stat().st_size,output_bytes=len(data),
                            wall_seconds=round(elapsed,3),cpu_seconds=float(user)+float(system),
                            largest_process_rss_kib=int(rss),sha256=expected)
                results.append(item)
                print(json.dumps(item),flush=True)
    (HERE/'simple-measurements.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__ == '__main__':
    main()
