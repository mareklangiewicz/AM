#!/usr/bin/env python3
"""Serial shared-default reader measurements under trial supervised budgets."""
import hashlib
import json
import os
import pathlib
import tempfile
import time

from experiment import document
from growth import fixture
from reader_budget import query_staged, ReaderRefusal
from staging import Stage
from worker import WorkerRefusal

HERE = pathlib.Path(__file__).resolve().parent
MIB = 1024*1024


def expected_hash(obj, assets=False):
    digest = hashlib.sha256()
    records = obj['releases']['1']['assets'] if assets else obj['releases']
    for rid, record in records.items():
        if assets:
            values = [record[k] for k in ('name', 'url', 'size', 'content_type')]
        else:
            values = [record.get('observed_at', obj['observed_at']), record['published_at'],
                      record['prerelease'], record['title']]
        row = rid + ''.join('\t'+json.dumps(value, ensure_ascii=False) for value in values) + '\n'
        digest.update(row.encode())
    return digest.hexdigest(), len(records)


def main():
    result = dict(limits=dict(wall_seconds=60, address_space_mib=128,
                              input_bytes=33554432, output_bytes=16777216,
                              aggregate_stage_bytes=128*MIB), cases=[])
    destination = HERE/'reader-budget-measurements.json'
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        shims = {}
        for name in ('mawk', 'gawk', 'busybox'):
            shim = root/name; shim.mkdir()
            (shim/'awk').write_text('#!/bin/sh\nexec '+name+(' awk' if name=='busybox' else '')+' "$@"\n')
            (shim/'awk').chmod(0o755)
            shims[name] = dict(PATH=str(shim)+':'+os.environ['PATH'])
        for shape, count, assets, title in [('small',100,8,32), ('mixed',1000,8,32),
                                           ('retained',10000,8,32), ('assets',1,60000,32),
                                           ('long_scalar',1,8,65523)]:
            obj = fixture(count, assets=assets, title=title)
            # Mostly implicit shared times, with every tenth release retaining
            # an older explicit observation. This is not the old explicit shape.
            for rid, record in obj['releases'].items():
                if int(rid) % 10:
                    record.pop('observed_at', None)
            expected, rows = expected_hash(obj, assets=shape=='assets')
            source = root/'fixture.yaml'; source.write_text(document(obj))
            args = ('rows', 'releases/1/assets', 'name', 'url', 'size', 'content_type') if shape=='assets' else ('rows', 'releases', 'observed_at', 'published_at', 'prerelease', 'title')
            cases = [(shape, source, 16*MIB, 'success_or_runtime_refusal')]
            if shape == 'mixed':
                bad = root/'bad.yaml'; bad.write_bytes(source.read_bytes()+b'unknown: "suffix"\n')
                cases.append(('mixed_bad_suffix',bad,16*MIB,'parse_refusal'))
            if shape == 'assets':
                cases.append(('assets_output_limit',source,4096,'output_refusal'))
            for label, file, output_limit, expectation in cases:
                for name, env in shims.items():
                    report = {}
                    started = time.monotonic()
                    with Stage() as stage:
                        try:
                            path = query_staged(stage, file, *args, output_bytes=output_limit,
                                                worker_limits=dict(seconds=60,address_bytes=128*MIB),
                                                env=env, report=report)
                            assert expectation == 'success_or_runtime_refusal'
                            digest = hashlib.sha256(); lines = 0
                            with path.open('rb') as stream:
                                for line in stream:
                                    digest.update(line); lines += 1
                            assert digest.hexdigest() == expected and lines == rows
                            item = dict(status='ok', output_bytes=path.stat().st_size,
                                        rows=lines, sha256=digest.hexdigest())
                        except ReaderRefusal as exc:
                            assert exc.status == 2
                            assert stage.used == 0
                            item = dict(status='reader_refusal' if expectation=='success_or_runtime_refusal' else expectation,
                                        output_bytes=0, reader_status=exc.status)
                        except WorkerRefusal as exc:
                            assert expectation == 'success_or_runtime_refusal'
                            assert stage.used == 0
                            item = dict(status='worker_refusal', output_bytes=0, reason=str(exc))
                        if 'status' in report:
                            report['reader_status'] = report.pop('status')
                        item.update(awk=name,shape=label,input_bytes=file.stat().st_size,
                                    reserved_peak_bytes=stage.peak,wall_seconds=round(time.monotonic()-started,3),
                                    **report)
                    result['cases'].append(item)
                    print(json.dumps(item),flush=True)
                    destination.write_text(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__':
    main()
