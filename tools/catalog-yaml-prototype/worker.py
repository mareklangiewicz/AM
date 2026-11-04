#!/usr/bin/env python3
"""Linux/POSIX fork experiment for trusted offline collector work, not a sandbox."""
import json
import math
import os
import pathlib
import resource
import signal
import tempfile
import time

from bounded import collect_files
from retention import parameters, refresh


class WorkerRefusal(RuntimeError):
    pass


def positive(value):
    return type(value) is int and value > 0


def run_worker(work, *, seconds=120, address_bytes=384*1024*1024,
               file_bytes=32*1024*1024, temporary_parent=None):
    """Return one JSON result only after exit 0 and complete serialization.

    Address space is RLIMIT_AS, not RSS. RLIMIT_FSIZE is per regular file,
    not aggregate disk. No pipes or inherited worker output can block the parent.
    Only trusted work that does not escape its session is supported. Forking
    requires a single-threaded parent. Existing parent/input allocations are
    outside these child limits. The parent checks status every 10 ms; elapsed
    deadline causes immediate SIGKILL, with ordinary OS scheduling latency.
    """
    if (type(seconds) not in (int, float) or not math.isfinite(seconds) or seconds <= 0
            or not positive(address_bytes) or not positive(file_bytes)):
        raise ValueError('worker limits')
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='yaml-worker-', dir=temporary_parent) as directory:
        output = pathlib.Path(directory) / 'result.json'
        pid = os.fork()
        if pid == 0:
            try:
                os.setsid()
                resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
                resource.setrlimit(resource.RLIMIT_AS, (address_bytes, address_bytes))
                resource.setrlimit(resource.RLIMIT_FSIZE, (file_bytes, file_bytes))
                # Keep diagnostics and accidental prints out of the result channel.
                with open(os.devnull, 'wb') as null:
                    os.dup2(null.fileno(), 1)
                    os.dup2(null.fileno(), 2)
                with output.open('w', encoding='utf-8') as stream:
                    json.dump(work(), stream, ensure_ascii=False, allow_nan=False)
                os._exit(0)
            except BaseException:
                os._exit(2)
        reaped = False
        try:
            while True:
                if time.monotonic() - started >= seconds:
                    raise WorkerRefusal('deadline')
                done, status = os.waitpid(pid, os.WNOHANG)
                if done:
                    reaped = True
                    if status != 0:
                        raise WorkerRefusal('worker failure')
                    break
                time.sleep(0.01)
            # A successful leader must not leave descendants writing its result.
            try:
                os.killpg(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            if output.stat().st_size > file_bytes:
                raise WorkerRefusal('result size')
            try:
                return json.loads(output.read_text(encoding='utf-8'))
            except (OSError, ValueError) as exc:
                raise WorkerRefusal('invalid result') from exc
        finally:
            # Also handle interrupts/errors. Kill the leader even if setsid has
            # not completed yet, then its session, then reap our direct child.
            if not reaped:
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            try:
                os.killpg(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            if not reaped:
                os.waitpid(pid, 0)


def collect_supervised(previous, pages, *, attempted_at, page_size=100,
                       page_limit=1, reconcile=False, worker_limits=None, **limits):
    """Offline adapter under hard worker limits; parent constructs refusal state.

    Any child failure is conservatively collection_limit. No precise OOM/CPU
    diagnosis is inferred from an exit status. Supervisor setup/I/O errors
    propagate to the caller, exposing no candidate and leaving previous untouched.
    """
    parameters(page_size, page_limit)
    if reconcile and page_limit != 'all':
        raise ValueError('reconciliation requires all')
    options = dict(attempted_at=attempted_at, page_size=page_size,
                   page_limit=page_limit, reconcile=reconcile)
    try:
        return run_worker(lambda: collect_files(previous, pages, **options, **limits),
                          **(worker_limits or {}))
    except WorkerRefusal:
        return refresh(previous, [dict(error='collection_limit')], **options)
