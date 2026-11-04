#!/usr/bin/env python3
"""Small offline consumer integration matrix; no collection or installation."""
import json
import os
import pathlib
import subprocess
import tempfile

from experiment import document, repository, SCHEMA

HERE = pathlib.Path(__file__).resolve().parent


def main():
    results = []
    with tempfile.TemporaryDirectory(prefix='yaml-browse-') as directory:
        root = pathlib.Path(directory)
        (root/'repositories').mkdir()
        apps = dict(format=2, schema=SCHEMA, apps={'example':123, 'example-beta':123})
        obj = repository()
        # One retained older observation and one implicit shared observation.
        obj['releases']['457'] = dict(obj['releases']['456'], tag='v2.1.0')
        obj['releases']['457'].pop('observed_at')
        expected = ''.join(rid + ''.join('\t'+json.dumps(value,ensure_ascii=False) for value in
                             (record['tag'],record.get('observed_at',obj['observed_at']),
                              record['published_at'],record['prerelease'],record['title']))+'\n'
                           for rid, record in obj['releases'].items()).encode()
        for tool in ('mawk','gawk','busybox'):
            shim = root/tool
            shim.mkdir()
            (shim/'awk').write_text('#!/bin/sh\nexec '+tool+(' awk' if tool=='busybox' else '')+' "$@"\n')
            (shim/'awk').chmod(0o755)
            env = dict(os.environ,PATH=str(shim)+':'+os.environ['PATH'],TMPDIR=str(root),
                       AM_YAML_MAX_INPUT_BYTES='2097152', AM_YAML_MAX_OUTPUT_BYTES='2097152')
            def query(app):
                return subprocess.run(['/bin/dash',str(HERE/'browse.sh'),str(root),app],
                                      env=env,capture_output=True,timeout=10)
            (root/'apps.yaml').write_text(document(apps))
            file = root/'repositories/123.yaml'
            file.write_text(document(obj))
            for alias in ('example','example-beta'):
                run = query(alias)
                assert (run.returncode,run.stdout)==(0,expected), (tool,alias,run.stderr)
            run = query('missing')
            assert (run.returncode,run.stdout)==(3,b'')
            wrong = dict(obj,repository_id=124)
            file.write_text(document(wrong))
            run = query('example')
            assert (run.returncode,run.stdout)==(2,b'')
            file.write_text(document(obj)+'unknown: "bad suffix"\n')
            run = query('example')
            assert (run.returncode,run.stdout)==(2,b'')
            file.write_text(document(obj))
            (root/'apps.yaml').write_text(document(apps)+'unknown: "bad suffix"\n')
            run = query('example')
            assert (run.returncode,run.stdout)==(2,b'')
            leftovers = [path.name for path in root.iterdir() if path.name.startswith('tmp.')]
            assert not leftovers
            item = dict(awk=tool,status='passed',cases=6,
                        release_rows=2,distinct_effective_observations=2)
            results.append(item)
            print(json.dumps(item),flush=True)
    (HERE/'browse-results.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__ == '__main__':
    main()
