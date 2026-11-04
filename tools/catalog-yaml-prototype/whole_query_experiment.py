#!/usr/bin/env python3
"""Offline whole-reader fault injection; no proposed consumer API or dependency."""
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import time

from deadline_experiment import running
from experiment import document, repository
from worker import WorkerRefusal, run_worker

HERE = pathlib.Path(__file__).resolve().parent


def trial(phase, directory):
    root = directory / phase
    root.mkdir()
    arena = root / 'arena'
    arena.mkdir()
    fixture = root / 'fixture.yaml'
    fixture.write_text(document(repository()))
    pidfile = root / 'pid'
    marker = root / 'entered'
    output = arena / 'output'
    shim = root / 'bin'
    shim.mkdir()
    environment = dict(os.environ, PATH=str(shim)+':'+os.environ['PATH'],
                       TMPDIR=str(arena), AM_YAML_PRIVATE_SPOOL=str(arena/'spool'),
                       AM_YAML_PARSE_SECONDS='', TEST_PID=str(pidfile),
                       TEST_MARKER=str(marker))
    # Shell helpers deliberately stop at exec sleep: no escaped sessions.
    if phase in ('wc', 'awk', 'cat', 'partial-cat'):
        tool = 'cat' if phase == 'partial-cat' else phase
        script = '#!/bin/sh\nprintf "%s" "$$" > "$TEST_PID"\n: > "$TEST_MARKER"\ntrap "" TERM\n'
        if phase == 'partial-cat':
            script += 'printf "already delivered\\n"\n'
        script += 'exec sleep 30\n'
        (shim/tool).write_text(script)
        (shim/tool).chmod(0o755)
    read_fd = write_fd = None
    if phase == 'blocked-output':
        read_fd, write_fd = os.pipe()
        os.set_blocking(write_fd, False)
        while True:
            try:
                os.write(write_fd, b'x'*4096)
            except BlockingIOError:
                break
        os.set_blocking(write_fd, True)
        # Cat reaches its output with a real full pipe, not a sleeping shim.
        real_cat = shutil.which('busybox') + ' cat'
        (shim/'cat').write_text('#!/bin/sh\nprintf "%s" "$$" > "$TEST_PID"\n: > "$TEST_MARKER"\nexec '+real_cat+' "$@"\n')
        (shim/'cat').chmod(0o755)

    def work():
        if read_fd is not None:
            os.close(read_fd)
        with output.open('xb') as stream:
            result = subprocess.run(['/bin/dash', str(HERE/'reader.sh'),
                                     'releases', str(fixture)], env=environment,
                                    stdout=write_fd if write_fd is not None else stream,
                                    stderr=subprocess.DEVNULL)
        return {'status': result.returncode}

    started = time.monotonic()
    candidate = False
    refusal = None
    digest = None
    try:
        result = run_worker(work, seconds=1 if phase != 'success' else 5,
                            temporary_parent=root)
        candidate = result['status'] == 0
        if candidate:
            digest = hashlib.sha256(output.read_bytes()).hexdigest()
    except WorkerRefusal as exc:
        refusal = str(exc)
    finally:
        elapsed = time.monotonic()-started
        if write_fd is not None:
            os.close(write_fd)
            os.close(read_fd)
    partial_bytes = output.stat().st_size if output.exists() else 0
    # SIGKILL bypasses shell traps. The surviving parent owns arena reclamation.
    shutil.rmtree(arena)
    alive = False
    if pidfile.exists():
        pid = int(pidfile.read_text())
        for _ in range(100):
            if not running(pid):
                break
            time.sleep(.01)
        alive = running(pid)
    assert not alive, phase
    assert not arena.exists(), phase
    if phase == 'success':
        assert candidate and refusal is None
        expected = subprocess.check_output(['/bin/dash', str(HERE/'reader.sh'),
                                             'releases', str(fixture)])
        assert digest == hashlib.sha256(expected).hexdigest()
    else:
        assert marker.exists(), phase + ' failed to reach injected phase'
        assert not candidate and refusal == 'deadline', (phase, refusal, locals().get('result'))
        assert elapsed < 4, (phase, elapsed)
    if phase == 'partial-cat':
        assert partial_bytes > 0
    return dict(phase=phase, seconds=round(elapsed,3), candidate=candidate,
                refusal=refusal, private_output_bytes=partial_bytes,
                sha256=digest, target_running=alive, arena_removed=not arena.exists())


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='yaml-whole-query-') as directory:
        results = [trial(phase, pathlib.Path(directory)) for phase in
                   ('success', 'wc', 'awk', 'cat', 'partial-cat', 'blocked-output')]
    print(json.dumps(results, indent=2))
