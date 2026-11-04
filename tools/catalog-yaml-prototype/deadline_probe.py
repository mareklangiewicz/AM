#!/usr/bin/env python3
"""Local timeout behavior probes; no portability inference from program names."""
import json
import os
import pathlib
import signal
import subprocess
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent


def main():
    results = []
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        for name, command in [('uutils', ['/usr/bin/timeout']), ('busybox', ['busybox','timeout'])]:
            for shape in ('single_exec', 'shell_tree'):
                marker = root/'marker'; marker.unlink(missing_ok=True)
                pidfile = root/'pid'; pidfile.unlink(missing_ok=True)
                script = 'trap "" TERM; exec sleep 30' if shape=='single_exec' else (
                    'sh -c \'trap "" TERM; sleep 2; : > "$1"\' sh "$1" & '
                    'printf "%s" "$!" > "$2"; wait')
                started = time.monotonic()
                with (root/'stdout').open('wb') as out, (root/'stderr').open('wb') as error:
                    process = subprocess.Popen([*command,'-s','KILL','1','sh','-c',script,
                                                'sh',str(marker),str(pidfile)],
                                               stdout=out,stderr=error,start_new_session=True)
                    try:
                        status = process.wait(timeout=4)
                        elapsed = time.monotonic()-started
                        if shape=='shell_tree':
                            time.sleep(max(0, 2.4-(time.monotonic()-started)))
                        results.append(dict(tool=name,shape=shape,status=status,
                                            seconds=round(elapsed,3), descendant_marker=marker.exists()))
                        print(json.dumps(results[-1]),flush=True)
                    finally:
                        if process.poll() is None:
                            os.killpg(process.pid,signal.SIGKILL);process.wait()
                        # Target only the descendant PID created by this probe.
                        if pidfile.exists():
                            try:
                                os.kill(int(pidfile.read_text()),signal.SIGKILL)
                            except ProcessLookupError:
                                pass
        target = root/'awk'
        target.write_text('#!/bin/sh\nprintf "explicit-external\\n" >&2\nexec sleep 30\n')
        target.chmod(0o755)
        environment = dict(os.environ, PATH=str(root)+':'+os.environ['PATH'])
        for label, args in [('bare',['awk','BEGIN {print "builtin-applet"}']),
                            ('explicit',[str(target)])]:
            run = subprocess.run(['/usr/bin/busybox','timeout','-s','KILL','1',*args],
                                 env=environment,capture_output=True,text=True,timeout=4)
            results.append(dict(tool='busybox',shape='applet_resolution',command=label,
                                status=run.returncode,stdout=run.stdout,stderr=run.stderr))
            print(json.dumps(results[-1]),flush=True)
    (HERE/'deadline-probe-results.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__ == '__main__':
    main()
