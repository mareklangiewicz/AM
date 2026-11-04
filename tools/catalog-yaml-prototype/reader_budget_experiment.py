#!/usr/bin/env python3
"""Reader output accounting, reservation and watchdog acceptance."""
import json
import os
import pathlib
import subprocess
import tempfile
import unittest

from experiment import Experiment, document, repository
from reader_budget import query_staged, ReaderRefusal
from staging import Stage, StageRefusal
from worker import WorkerRefusal

HERE = pathlib.Path(__file__).resolve().parent


class ReaderBudgets(unittest.TestCase):
    accepted = Experiment.accepted
    run_reader = Experiment.run_reader

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = pathlib.Path(self.temporary.name)
        self.obj = repository()
        self.file = self.root/'fixture.yaml'
        self.file.write_text(document(self.obj))
        shim = os.environ.get('AM_YAML_AWK_PATH')
        self.env = dict(PATH=shim+':'+os.environ['PATH']) if shim else {}

    def raw(self, operation, *keys, cap=16777216, file=None):
        return subprocess.run(['sh', str(HERE/'reader.sh'), operation, str(file or self.file), *keys],
                              env=dict(os.environ, **self.env, AM_YAML_MAX_OUTPUT_BYTES=str(cap)),
                              capture_output=True, timeout=15)

    def test_exact_output_and_one_byte_below(self):
        for operation, keys in [('releases', []), ('assets', ['456']),
                                ('rows', ['releases', 'observed_at', 'title']),
                                ('get', ['releases', '456', 'title'])]:
            accepted = self.raw(operation, *keys)
            self.assertEqual(accepted.returncode, 0)
            size = len(accepted.stdout)
            self.assertGreater(size, 0)
            self.assertEqual(self.raw(operation, *keys, cap=size).stdout, accepted.stdout)
            refused = self.raw(operation, *keys, cap=size-1)
            self.assertEqual(refused.returncode, 2)
            self.assertEqual(refused.stdout, b'')
        self.assertEqual(self.raw('validate', cap=0).returncode, 0)
        apps = self.root/'apps.yaml'
        apps.write_text(document(dict(format=2, schema=self.obj['schema'], apps={'app':123})))
        self.assertEqual(self.raw('apps', cap=4, file=apps).stdout, b'app\n')
        refused = self.raw('apps', cap=3, file=apps)
        self.assertEqual((refused.returncode, refused.stdout), (2, b''))
        empty = self.root/'empty.yaml'
        self.obj['releases']['456']['title'] = ''
        empty.write_text(document(self.obj))
        run = self.raw('get', 'releases', '456', 'title', cap=0, file=empty)
        self.assertEqual((run.returncode, run.stdout), (0, b''))

    def test_projection_duplicates_and_invalid_budgets(self):
        self.assertEqual(self.raw('rows', 'releases', 'tag', 'tag').returncode, 2)
        for cap in (-1, 'no', 33554433, '01'):
            refused = self.raw('releases', cap=cap)
            self.assertEqual(refused.returncode, 2)
            self.assertEqual(refused.stdout, b'')

    def test_supervised_success_and_exact_reservations(self):
        expected = self.raw('rows', 'releases', 'observed_at', 'title').stdout
        cap = len(expected)
        allowance = self.file.stat().st_size + 2*cap + 4096 + max(cap,4096)
        with Stage(total_bytes=allowance) as stage:
            report = {}
            path = query_staged(stage, self.file, 'rows', 'releases', 'observed_at', 'title',
                                output_bytes=cap, env=self.env, report=report)
            self.assertEqual(path.read_bytes(), expected)
            self.assertEqual(stage.peak, allowance)
            self.assertEqual(stage.used, cap)
            self.assertEqual(report['status'], 0)
            stage.release(path)
            self.assertEqual(stage.used, 0)
        with Stage(total_bytes=allowance-1) as stage:
            with self.assertRaises(StageRefusal):
                query_staged(stage, self.file, 'rows', 'releases', 'observed_at', 'title',
                             output_bytes=cap, env=self.env)
            self.assertEqual(stage.used, 0)

    def test_invalid_suffix_missing_and_output_refusal(self):
        bad = self.root/'bad.yaml'
        bad.write_bytes(self.file.read_bytes()+b'unknown: "suffix"\n')
        for file, operation, keys, cap, status in [
            (bad, 'releases', [], 4096, 2),
            (self.file, 'get', ['releases', '999', 'tag'], 4096, 3),
            (self.file, 'releases', [], 0, 2)]:
            with Stage() as stage:
                with self.assertRaises(ReaderRefusal) as caught:
                    query_staged(stage, file, operation, *keys, output_bytes=cap, env=self.env)
                self.assertEqual(caught.exception.status, status)
                self.assertEqual(stage.used, 0)
                self.assertEqual(list(stage.root.iterdir()), [])

    def test_deadline_refusal_removes_all_outputs(self):
        # A deliberately noncooperative awk shim verifies the watchdog, without
        # relying on a small real fixture happening to exceed its time budget.
        shim = self.root/'bin'; shim.mkdir()
        (shim/'awk').write_text('#!/bin/sh\ntrap "" TERM\nsleep 30\n')
        (shim/'awk').chmod(0o755)
        with Stage() as stage:
            with self.assertRaises(WorkerRefusal):
                query_staged(stage, self.file, 'releases', output_bytes=4096,
                             worker_limits=dict(seconds=0.15),
                             env=dict(PATH=str(shim)+':'+os.environ['PATH']))
            self.assertEqual(stage.used, 0)
            self.assertEqual(list(stage.root.iterdir()), [])

    def test_input_limit_and_private_spool_exclusive(self):
        with Stage() as stage:
            with self.assertRaises(StageRefusal):
                query_staged(stage, self.file, 'releases', input_bytes=self.file.stat().st_size-1)
            self.assertEqual(stage.used, 0)
        spool = self.root/'existing'
        spool.write_bytes(b'preserve')
        run = subprocess.run(['sh', str(HERE/'reader.sh'), 'releases', str(self.file)],
                             env=dict(os.environ, **self.env, AM_YAML_PRIVATE_SPOOL=str(spool)),
                             capture_output=True, timeout=15)
        self.assertNotEqual(run.returncode, 0)
        self.assertEqual(run.stdout, b'')
        self.assertEqual(spool.read_bytes(), b'preserve')


if __name__ == '__main__':
    unittest.main()
