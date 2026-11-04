#!/usr/bin/env python3
"""Real process-limit/refusal probes; no network or production files."""
import json
import os
import pathlib
import signal
import tempfile
import time
import unittest
from unittest.mock import patch

from bounded_experiment import release, ATTEMPT
from experiment import Experiment, repository
from worker import collect_supervised, run_worker, WorkerRefusal


class Workers(unittest.TestCase):
    accepted = Experiment.accepted
    run_reader = Experiment.run_reader

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = pathlib.Path(self.directory.name)
        self.old = repository()
        page = self.root / 'page.json'
        page.write_text(json.dumps([release()]))
        self.pages = [dict(path=page, has_next=False)]

    def collect(self, **kw):
        result = collect_supervised(self.old, self.pages, attempted_at=ATTEMPT, **kw)
        self.accepted(result)
        return result

    def rollback(self, result):
        self.assertEqual(result['collection']['reason'], 'collection_limit')
        for key in ('releases', 'observed_at', 'last_success'):
            self.assertEqual(result[key], self.old[key])

    def test_real_normalization_and_refusal(self):
        original = json.dumps(self.old, sort_keys=True)
        result = self.collect()
        self.assertEqual(result['collection']['status'], 'ok')
        self.assertIn('457', result['releases'])
        self.rollback(self.collect(worker_limits=dict(file_bytes=1)))
        self.assertEqual(json.dumps(self.old, sort_keys=True), original)

    def test_noncooperative_deadline_and_cleanup(self):
        def hung(*args, **kw):
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            time.sleep(30)
        before = time.monotonic()
        with patch('worker.collect_files', hung):
            self.rollback(self.collect(worker_limits=dict(seconds=0.15,
                                                           temporary_parent=self.root)))
        self.assertLess(time.monotonic() - before, 3)
        self.assertEqual(list(self.root.glob('yaml-worker-*')), [])

    def test_memory_allocation_refusal(self):
        def allocate(*args, **kw):
            return bytearray(256*1024*1024)
        with patch('worker.collect_files', allocate):
            self.rollback(self.collect(worker_limits=dict(address_bytes=96*1024*1024)))

    def test_partial_serialization_and_exception_refusal(self):
        for work in (lambda: ['x'*65536]*16, lambda: [1, object()]):
            with self.assertRaises(WorkerRefusal):
                run_worker(work, file_bytes=1024, temporary_parent=self.root)
            self.assertEqual(list(self.root.glob('yaml-worker-*')), [])
        def broken(*args, **kw):
            args[0]['releases'].clear()
            raise RuntimeError('merge failed after modifying private copy')
        with patch('worker.collect_files', broken):
            self.rollback(self.collect())

    def test_file_boundary_and_invalid_limits(self):
        self.assertEqual(run_worker(lambda: 'abcd', file_bytes=6), 'abcd')
        with self.assertRaises(WorkerRefusal):
            run_worker(lambda: 'abcd', file_bytes=5)
        for options in (dict(seconds=float('nan')), dict(seconds=float('inf')),
                        dict(seconds=0), dict(file_bytes=True), dict(address_bytes=-1)):
            with self.assertRaises(ValueError):
                run_worker(lambda: None, **options)

    def test_descendant_group_is_killed(self):
        marker = self.root / 'escaped'
        def descendants():
            if os.fork() == 0:
                time.sleep(0.5)
                marker.write_text('unexpected surviving child')
                os._exit(0)
            time.sleep(30)
        with self.assertRaises(WorkerRefusal):
            run_worker(descendants, seconds=0.15)
        time.sleep(0.6)
        self.assertFalse(marker.exists())
        def completed_leader():
            if os.fork() == 0:
                time.sleep(0.5)
                marker.write_text('unexpected surviving child')
                os._exit(0)
            return 'done'
        self.assertEqual(run_worker(completed_leader), 'done')
        time.sleep(0.6)
        self.assertFalse(marker.exists())


if __name__ == '__main__':
    unittest.main()
