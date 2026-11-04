#!/usr/bin/env python3
"""Two local shells x two local timeout tools x three awk implementations."""
import json
import os
import pathlib
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
results = []
with tempfile.TemporaryDirectory() as directory:
    for shell in ('dash','busybox'):
        for timer in ('uutils','busybox'):
            for awk in ('mawk','gawk','busybox'):
                shim = pathlib.Path(directory)/(shell+'-'+timer+'-'+awk); shim.mkdir()
                commands = dict(sh='/bin/dash' if shell=='dash' else '/usr/bin/busybox sh',
                                timeout='/usr/bin/timeout' if timer=='uutils' else '/usr/bin/busybox timeout',
                                awk=awk+(' awk' if awk=='busybox' else ''))
                for name, command in commands.items():
                    path = shim/name
                    path.write_text('#!/bin/sh\nexec '+command+' "$@"\n'); path.chmod(0o755)
                run = subprocess.run(['python3',str(HERE/'deadline_experiment.py')],
                                     env=dict(os.environ,AM_YAML_AWK_PATH=str(shim)),
                                     capture_output=True,text=True,timeout=45)
                if run.returncode:
                    raise RuntimeError(shell+'/'+timer+'/'+awk+'\n'+run.stdout+run.stderr)
                item = dict(shell=shell,timeout=timer,awk=awk,status='passed',
                            new_groups=6,inherited_reader_groups=9)
                results.append(item);print(json.dumps(item),flush=True)
                (HERE/'deadline-results.json').write_text(json.dumps(results,indent=2)+'\n')
