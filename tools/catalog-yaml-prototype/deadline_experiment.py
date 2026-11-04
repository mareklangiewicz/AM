#!/usr/bin/env python3
"""Shell-only trusted-parser deadline acceptance; fixture shims never spawn trees."""
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from experiment import Experiment, document, repository

HERE = pathlib.Path(__file__).resolve().parent


def running(pid):
    try:
        return pathlib.Path('/proc',str(pid),'stat').read_text().split(') ',1)[1].split()[0] != 'Z'
    except FileNotFoundError:
        return False


class Deadlines(unittest.TestCase):
    accepted = Experiment.accepted
    run_reader = Experiment.run_reader

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = pathlib.Path(self.temporary.name)
        self.file = self.root/'fixture.yaml'
        self.file.write_text(document(repository()))
        self.spools = self.root/'spools'; self.spools.mkdir()
        shim = os.environ.get('AM_YAML_AWK_PATH')
        self.path = shim+':'+os.environ['PATH'] if shim else os.environ['PATH']
        self.shell = shutil.which('sh',path=self.path)

    def raw(self, operation='releases', *keys, seconds='5', env=None):
        environment = dict(os.environ,PATH=self.path,TMPDIR=str(self.spools),
                           AM_YAML_PARSE_SECONDS=seconds)
        environment.update(env or {})
        return subprocess.run([self.shell,str(HERE/'reader.sh'),operation,str(self.file),*keys],
                              env=environment,
                              capture_output=True,timeout=8)

    def test_success_is_byte_identical(self):
        for operation, keys in [('releases',[]), ('assets',['456']),
                                ('get',['releases','456','title']),
                                ('rows',['releases','observed_at','published_at'])]:
            plain = self.raw(operation,*keys,seconds='')
            guarded = self.raw(operation,*keys)
            self.assertEqual((guarded.returncode,guarded.stdout), (plain.returncode,plain.stdout))
            self.assertEqual(guarded.returncode,0)
        self.assertEqual(list(self.spools.iterdir()),[])

    def hung(self, partial):
        shim = self.root/'hung'; shim.mkdir()
        pidfile = self.root/'pid'
        script = '#!/bin/sh\nprintf "%s" "$$" > "$TEST_PARSER_PID"\ntrap "" TERM\n'
        if partial:
            script += 'printf "private partial output"\n'
        script += 'exec sleep 30\n'
        (shim/'awk').write_text(script); (shim/'awk').chmod(0o755)
        run = self.raw(seconds='1',env=dict(PATH=str(shim)+':'+self.path,TEST_PARSER_PID=str(pidfile)))
        self.assertIn(run.returncode,(124,137))
        self.assertEqual(run.stdout,b'')
        self.assertTrue(pidfile.exists())
        self.assertFalse(running(int(pidfile.read_text())))
        self.assertEqual(list(self.spools.iterdir()),[])

    def test_term_ignoring_parser_is_killed(self):
        self.hung(False)

    def test_partial_spool_never_exposed(self):
        self.hung(True)

    def test_missing_timeout_refuses_before_parser(self):
        shim = self.root/'missing'; shim.mkdir()
        run = self.raw(env=dict(PATH=str(shim)))
        self.assertEqual(run.returncode,2)
        self.assertIn(b'timeout unavailable',run.stderr)
        self.assertEqual(run.stdout,b'')
        self.assertEqual(list(self.spools.iterdir()),[])

    def test_invalid_seconds(self):
        for seconds in ('0','01','-1','+1','1.5','nan','3601','10000'):
            run = self.raw(seconds=seconds)
            self.assertEqual((run.returncode,run.stdout),(2,b''))
        self.assertEqual(list(self.spools.iterdir()),[])

    def test_reader_refusals_preserve_status_and_cleanup(self):
        missing = self.raw('get','releases','999','tag')
        self.assertEqual((missing.returncode,missing.stdout),(3,b''))
        over = self.raw(env=dict(AM_YAML_MAX_OUTPUT_BYTES='0'))
        self.assertEqual((over.returncode,over.stdout),(2,b''))
        self.file.write_bytes(self.file.read_bytes()+b'unknown: "suffix"\n')
        malformed = self.raw()
        self.assertEqual((malformed.returncode,malformed.stdout),(2,b''))
        self.assertEqual(list(self.spools.iterdir()),[])


if __name__ == '__main__':
    unittest.main()
