#!/usr/bin/env python3
"""Reserved logical-byte staging for the trusted offline collector experiment."""
import json
import os
import pathlib
import stat
import tempfile

from bounded import FixtureBudget, collect_files
from retention import parameters
from worker import positive, run_worker


class StageRefusal(RuntimeError):
    pass


class Stage:
    """Single-owner arena. All managed writes must use a live reservation.

    Sum of capacities bounds simultaneous logical file lengths, conservatively
    including unused result space. This is not a filesystem quota. Metadata,
    allocation blocks, external originals and arbitrary worker files are excluded.
    No threads/concurrent mutation or untrusted children are supported.
    """
    def __init__(self, total_bytes=128*1024*1024, max_files=128, *, parent=None):
        if not positive(total_bytes) or not positive(max_files):
            raise ValueError('stage limits')
        self.total_bytes, self.max_files = total_bytes, max_files
        self.used = self.peak = self.serial = 0
        self.live = {}
        self.temporary = tempfile.TemporaryDirectory(prefix='yaml-stage-', dir=parent)
        self.root = pathlib.Path(self.temporary.name)
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.temporary.cleanup()
        self.live.clear()
        self.used = 0
        self.closed = True

    def reserve(self, size):
        if type(size) is not int or size < 0:
            raise ValueError('reservation')
        if self.closed or self.used + size > self.total_bytes or len(self.live) >= self.max_files:
            raise StageRefusal('aggregate staging capacity')
        self.serial += 1
        path = self.root / str(self.serial)
        self.live[path] = size
        self.used += size
        self.peak = max(self.peak, self.used)
        return path

    def release(self, path):
        capacity = self.live[path]
        path.unlink(missing_ok=True)
        del self.live[path]
        self.used -= capacity

    def snapshot(self, source, *, max_bytes):
        if type(max_bytes) is not int or max_bytes < 0:
            raise ValueError('input bound')
        # Nonblocking open allows rejecting FIFOs without waiting for a writer.
        fd = os.open(source, os.O_RDONLY | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > max_bytes:
                raise StageRefusal('regular input byte bound')
            path = self.reserve(info.st_size)
            try:
                with path.open('xb') as output:
                    remaining = info.st_size
                    while True:
                        chunk = stream.read(min(65536, remaining + 1))
                        if not chunk:
                            if remaining:
                                raise StageRefusal('input shrank')
                            return path
                        if len(chunk) > remaining:
                            raise StageRefusal('input grew')
                        output.write(chunk)
                        remaining -= len(chunk)
            except BaseException:
                self.release(path)
                raise


def collect_staged(stage, previous_path, pages, *, attempted_at, page_size=100,
                   page_limit=1, reconcile=False, input_bytes=32*1024*1024,
                   response_bytes=16*1024*1024, source_bytes=96*1024*1024,
                   max_pages=64, result_bytes=32*1024*1024, worker_limits=None,
                   **limits):
    """Return a stage-owned JSON candidate path; parent never decodes JSON.

    Snapshots are private and removed after worker completion. Candidate capacity
    stays charged until stage.release(path) or arena close, including while later
    sources run. Parent copies <=64 KiB at once; parent staging time is cooperative,
    not covered by the child watchdog. No publication/copy outside this arena.
    Refusal raises without a candidate; caller retains its original prior file.
    """
    parameters(page_size, page_limit)
    if reconcile and page_limit != 'all':
        raise ValueError('reconciliation requires all')
    if not all(positive(v) for v in (input_bytes, response_bytes, source_bytes, max_pages, result_bytes)):
        raise ValueError('staging limits')
    worker_options = dict(worker_limits or {})
    if any(k in worker_options for k in ('result_path', 'file_bytes')):
        raise ValueError('result bound owned by staging')
    snapshots = []
    candidate = None
    try:
        # Reserve result headroom before copying inputs or doing collection work.
        candidate = stage.reserve(result_bytes)
        previous = stage.snapshot(previous_path, max_bytes=input_bytes)
        snapshots.append(previous)
        selected = []
        consumed = 0
        iterator = iter(pages)
        count = max_pages if page_limit == 'all' else min(max_pages, page_limit)
        for index in range(count):
            try:
                page = next(iterator)
            except StopIteration:
                break
            copied = stage.snapshot(page['path'], max_bytes=min(response_bytes, source_bytes-consumed))
            snapshots.append(copied)
            consumed += stage.live[copied]
            selected.append(dict(path=copied, has_next=page['has_next']))
            if page['has_next'] is False:
                break
        else:
            if selected and selected[-1]['has_next'] is not False and (page_limit == 'all' or page_limit > max_pages):
                raise StageRefusal('page safety capacity')

        def work():
            # Both decoding and result serialization are under worker RLIMIT_AS.
            with previous.open(encoding='utf-8') as stream:
                old = json.load(stream)
            return collect_files(old, selected, attempted_at=attempted_at,
                                 page_size=page_size, page_limit=page_limit,
                                 reconcile=reconcile,
                                 budget=FixtureBudget(requests=max_pages, response_bytes=response_bytes,
                                                      total_bytes=source_bytes), **limits)
        run_worker(work, file_bytes=result_bytes, result_path=candidate, **worker_options)
        return candidate
    except BaseException:
        if candidate is not None:
            stage.release(candidate)
        raise
    finally:
        for path in snapshots:
            stage.release(path)
