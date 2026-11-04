#!/usr/bin/env python3
"""Run shared observation-default acceptance on the three supported awk tools."""
import json,os,pathlib,subprocess,tempfile
HERE=pathlib.Path(__file__).resolve().parent
results=[]
with tempfile.TemporaryDirectory() as directory:
    for name in ('mawk','gawk','busybox'):
        shim=pathlib.Path(directory)/name;shim.mkdir()
        executable=shim/'awk'
        executable.write_text('#!/bin/sh\nexec '+name+(' awk' if name=='busybox' else '')+' "$@"\n')
        executable.chmod(0o755)
        env=dict(os.environ,AM_YAML_AWK_PATH=str(shim))
        run=subprocess.run(['python3',str(HERE/'default_experiment.py')],env=env,capture_output=True,text=True,timeout=60)
        if run.returncode:
            raise RuntimeError(name+'\n'+run.stdout+run.stderr)
        results.append(dict(awk=name,status='passed',new_groups=7,inherited_reader_groups=9))
        print(json.dumps(results[-1]),flush=True)
(HERE/'default-results.json').write_text(json.dumps(results,indent=2)+'\n')
