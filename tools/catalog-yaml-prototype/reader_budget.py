#!/usr/bin/env python3
"""Offline supervised reader experiment; Python is not a consumer requirement."""
import json
import os
import pathlib
import resource
import subprocess
import time

from staging import StageRefusal
from worker import run_worker

HERE = pathlib.Path(__file__).resolve().parent


class ReaderRefusal(RuntimeError):
    def __init__(self, status):
        self.status = status
        super().__init__('reader exit ' + str(status))


def query_staged(stage, source, operation, *keys, input_bytes=32*1024*1024,
                 output_bytes=16*1024*1024, worker_limits=None, env=None,
                 report=None):
    """Return private raw query output only after complete supervised success.

    Reserve input + full spool + full output + diagnostics + a 4096-byte receipt. The parent
    decodes only that fixed-size receipt. Candidate output stays charged in stage.
    Parent input snapshot precedes the worker deadline, as in collect_staged.
    """
    if (type(input_bytes) is not int or not 1 <= input_bytes <= 33554432 or
            type(output_bytes) is not int or not 0 <= output_bytes <= 33554432):
        raise ValueError('reader limits')
    options = dict(worker_limits or {})
    if any(k in options for k in ('result_path', 'file_bytes')):
        raise ValueError('reader owns file allowance')
    paths = []
    output = None
    success = False
    try:
        output = stage.reserve(output_bytes); paths.append(output)
        spool = stage.reserve(output_bytes); paths.append(spool)
        receipt = stage.reserve(4096); paths.append(receipt)
        diagnostic = stage.reserve(max(output_bytes, 4096)); paths.append(diagnostic)
        snapshot = stage.snapshot(source, max_bytes=input_bytes); paths.append(snapshot)
        environment = dict(os.environ, **(env or {}))
        environment.update(AM_YAML_MAX_INPUT_BYTES=str(input_bytes),
                           AM_YAML_MAX_OUTPUT_BYTES=str(output_bytes),
                           AM_YAML_PRIVATE_SPOOL=str(spool))

        def work():
            started = time.monotonic()
            with output.open('xb') as stream, diagnostic.open('xb') as error:
                proc = subprocess.run(['sh', str(HERE/'reader.sh'), operation,
                                       str(snapshot), *keys], stdout=stream,
                                      stderr=error, env=environment)
            usage = resource.getrusage(resource.RUSAGE_CHILDREN)
            with diagnostic.open('rb') as stream:
                message = stream.read(512).decode('utf-8', errors='replace')
            return dict(status=proc.returncode, diagnostic=message, seconds=time.monotonic()-started,
                        peak_rss_kib=usage.ru_maxrss,
                        cpu_seconds=usage.ru_utime+usage.ru_stime)
        run_worker(work, file_bytes=max(output_bytes, 4096), result_path=receipt, **options)
        result = json.loads(receipt.read_text())  # Always bounded to 4096 bytes.
        if report is not None:
            report.update(result)
        if result['status'] != 0:
            raise ReaderRefusal(result['status'])
        if output.stat().st_size > output_bytes:
            raise StageRefusal('reader output bound')
        success = True
        return output
    finally:
        for path in paths:
            if not (success and path == output):
                stage.release(path)
