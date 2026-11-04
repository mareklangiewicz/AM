#!/usr/bin/env python3
"""Aggregate logical-byte accounting and file-oriented collector acceptance."""
import json
import os
import pathlib
import tempfile
import unittest
from unittest.mock import patch

from bounded_experiment import ATTEMPT, release
from experiment import Experiment, repository
from staging import Stage, StageRefusal, collect_staged
from worker import WorkerRefusal


class Staging(unittest.TestCase):
    accepted = Experiment.accepted
    run_reader = Experiment.run_reader

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = pathlib.Path(self.temporary.name)
        self.previous = self.root / 'previous.json'
        self.previous.write_text(json.dumps(repository()))
        self.original = self.previous.read_bytes()
        self.page = self.root / 'page.json'
        self.page.write_text(json.dumps([release()]))
        self.pages = [dict(path=self.page, has_next=False)]

    def collect(self, stage, **options):
        return collect_staged(stage, self.previous, self.pages,
                              attempted_at=ATTEMPT, **options)

    def test_exact_aggregate_and_cross_source_capacity(self):
        result_capacity = 16384
        inputs = self.previous.stat().st_size + self.page.stat().st_size
        with Stage(total_bytes=inputs+result_capacity) as stage:
            result = self.collect(stage, result_bytes=result_capacity)
            self.accepted(json.loads(result.read_text()))
            self.assertEqual(stage.peak, inputs+result_capacity)
            self.assertEqual(stage.used, result_capacity)
            with self.assertRaises(StageRefusal):
                self.collect(stage, result_bytes=result_capacity)
            self.assertEqual(list(stage.live), [result])
            stage.release(result)
            result = self.collect(stage, result_bytes=result_capacity)
            stage.release(result)
            self.assertEqual(stage.used, 0)
        with Stage(total_bytes=inputs+result_capacity-1) as stage:
            with self.assertRaises(StageRefusal):
                self.collect(stage, result_bytes=result_capacity)
            self.assertEqual(stage.used, 0)
            self.assertEqual(list(stage.root.iterdir()), [])
        self.assertEqual(self.previous.read_bytes(), self.original)

    def test_snapshot_bounds_empty_and_file_count(self):
        empty = self.root / 'empty'
        empty.touch()
        with Stage(total_bytes=4, max_files=1) as stage:
            path = stage.snapshot(empty, max_bytes=0)
            with self.assertRaises(StageRefusal):
                stage.reserve(0)
            stage.release(path)
            source = self.root / 'four'
            source.write_bytes(b'abcd')
            path = stage.snapshot(source, max_bytes=4)
            self.assertEqual(path.read_bytes(), b'abcd')
            stage.release(path)
            with self.assertRaises(StageRefusal):
                stage.snapshot(source, max_bytes=3)
            self.assertEqual(stage.used, 0)

    def test_input_growth_shrink_and_nonregular(self):
        actual = os.fstat
        for offset in (-1, 1):
            def changed(fd):
                fields = list(actual(fd)); fields[6] += offset
                return os.stat_result(fields)
            with Stage() as stage, patch('staging.os.fstat', changed):
                with self.assertRaises(StageRefusal):
                    stage.snapshot(self.page, max_bytes=4096)
                self.assertEqual(stage.used, 0)
                self.assertEqual(list(stage.root.iterdir()), [])
        fifo = self.root / 'fifo'
        os.mkfifo(fifo)
        with Stage() as stage:
            with self.assertRaises(StageRefusal):
                stage.snapshot(fifo, max_bytes=4096)

    def test_worker_refusal_cleans_reservations(self):
        for options in (dict(result_bytes=1), dict(worker_limits=dict(seconds=0.000001))):
            with Stage() as stage:
                with self.assertRaises(WorkerRefusal):
                    self.collect(stage, **options)
                self.assertEqual(stage.used, 0)
                self.assertEqual(list(stage.root.iterdir()), [])
        self.assertEqual(self.previous.read_bytes(), self.original)

    def test_scope_is_lazy_and_input_aggregate_refuses(self):
        def pages():
            yield dict(path=self.page, has_next=True)
            raise AssertionError('finite scope consumed an extra page')
        with Stage() as stage:
            candidate = collect_staged(stage, self.previous, pages(), attempted_at=ATTEMPT)
            result = json.loads(candidate.read_text())
            self.accepted(result)
            self.assertFalse(result['last_success']['history_complete'])
        with Stage() as stage:
            with self.assertRaises(StageRefusal):
                self.collect(stage, source_bytes=self.page.stat().st_size-1)
            self.assertEqual(stage.used, 0)
        with Stage() as stage:
            with self.assertRaises(StageRefusal):
                collect_staged(stage, self.previous,
                               [dict(path=self.page, has_next=True)],
                               attempted_at=ATTEMPT, page_limit='all', max_pages=1)
            self.assertEqual(stage.used, 0)

    def test_parent_does_not_decode_and_arena_cleanup(self):
        with Stage(parent=self.root) as stage:
            root = stage.root
            parent_pid = os.getpid()
            original_load = json.load
            original_loads = json.loads
            def child_load(*args, **kw):
                if os.getpid() == parent_pid:
                    raise AssertionError('parent decoded input')
                return original_load(*args, **kw)
            def child_loads(*args, **kw):
                if os.getpid() == parent_pid:
                    raise AssertionError('parent decoded result')
                return original_loads(*args, **kw)
            with patch('staging.json.load', child_load), patch('worker.json.loads', child_loads):
                candidate = self.collect(stage)
            self.assertTrue(candidate.exists())
            self.accepted(json.loads(candidate.read_text()))
        self.assertFalse(root.exists())
        with self.assertRaises(StageRefusal):
            stage.reserve(1)

    def test_write_failure_and_invalid_arguments(self):
        with Stage() as stage:
            with patch('staging.pathlib.Path.open', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    stage.snapshot(self.page, max_bytes=4096)
            self.assertEqual(stage.used, 0)
            for options in (dict(result_bytes=0), dict(max_pages=True),
                            dict(worker_limits=dict(file_bytes=10))):
                with self.assertRaises(ValueError):
                    self.collect(stage, **options)
            self.assertEqual(stage.used, 0)


if __name__ == '__main__':
    unittest.main()
