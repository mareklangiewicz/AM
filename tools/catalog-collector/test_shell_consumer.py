"""Actual shell reader with retained responses and stubbed curl/clock, no HTTP."""
import copy
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from shell_lookup import epoch, render
from storage import validate, canonical, decode
import test_storage as storage_tests
from test_storage import GEN

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / 'modules/catalog.am'
PIN = 'b' * 40
ALIAS = 'https://api.github.com/repos/obsidianmd/obsidian-releases/releases'


class ShellFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        storage_tests.StorageContract.setUpClass()
        cls.base = storage_tests.StorageContract.base
        cls.index = validate(cls.base)
        cls.rid = cls.index['aliases'][ALIAS]['request_id']
        cls.obs = cls.index['entries'][cls.rid]['observation']

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.bin = self.path / 'bin'
        self.bin.mkdir()
        self.tree = dict(self.base)
        self.now = [epoch(GEN)] * 3
        self.body = self.base['bodies/' + self.rid + '.json']
        self.script('curl', '''import json, os, pathlib, sys
p=pathlib.Path(os.environ['FIXTURE'])
a=sys.argv[1:]; url=a[-1]
with (p/'calls').open('a') as f: f.write(json.dumps(a)+'\\n')
if '/commits/' in url: raw=('b'*40+'\\n').encode()
else:
    assert '/ivan-hc/AM/'+'b'*40+'/' in url, url
    name=url.split('/'+'b'*40+'/',1)[1]
    raw=(p/'tree'/name).read_bytes()
(p/'last-url').write_text(url)
pathlib.Path(a[a.index('--output')+1]).write_bytes(raw)
print(os.environ.get('HTTP_STATUS','200'),end='')
''')
        self.script('date', '''import json, os, pathlib
p=pathlib.Path(os.environ['FIXTURE'])/'times'
t=json.loads(p.read_text()); print(t.pop(0) if len(t)>1 else t[0]); p.write_text(json.dumps(t))
''')

    def script(self, name, body):
        p = self.bin / name
        p.write_text('#!' + sys.executable + '\n' + body)
        p.chmod(0o755)

    def env(self):
        return {**os.environ, 'FIXTURE': str(self.path), 'PATH': str(self.bin)+':/usr/bin:/bin'}

    def stage(self):
        for name, raw in self.tree.items():
            p = self.path / 'tree' / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw)
        (self.path/'times').write_text(json.dumps(self.now))
        (self.path/'calls').write_text('')

    def invoke(self, args=None, shell='/bin/sh', env=None):
        self.stage()
        return subprocess.run([shell, str(HELPER), ALIAS, *(args if args is not None else ['--commit', PIN])],
                              cwd=self.path, env=env or self.env(), capture_output=True)

    def consent(self):
        return ['--commit', PIN, '--accept-stale', PIN, self.rid, self.obs['sha256']]

    def calls(self):
        return [json.loads(line) for line in (self.path/'calls').read_text().splitlines()]


class ShellConsumer(ShellFixture):
    def test_exact_bytes_pin_and_original_host_for_dash_and_bash(self):
        for shell in ('/bin/sh', '/bin/bash'):
            result=self.invoke(shell=shell)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(result.stdout,self.body)
            self.assertEqual(len(self.calls()),2)
            self.assertTrue(all('/ivan-hc/AM/'+PIN+'/' in c[-1] for c in self.calls()))
            self.assertTrue(all(c[0]=='-q' and '--max-filesize' in c and '-L' not in c for c in self.calls()))

    def test_resolve_once(self):
        result=self.invoke(args=[])
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(len(self.calls()),3)
        self.assertIn('/commits/heads/release-catalog',self.calls()[0][-1])
        self.assertEqual(result.stdout,self.body)

    def test_inclusive_edge_exact_stale_and_wrong_tuple(self):
        edge=datetime.fromisoformat(self.obs['validated_at'])+timedelta(days=1)
        self.now=[epoch(edge.isoformat())]*3
        result=self.invoke();self.assertEqual(result.returncode,0,result.stderr)
        self.now=[epoch((edge+timedelta(microseconds=1)).isoformat())]*3
        result=self.invoke();self.assertNotEqual(result.returncode,0)
        self.assertEqual(result.stdout,b'');self.assertEqual(len(self.calls()),1)
        self.assertIn((' '.join(self.consent())).encode(),result.stderr)
        result=self.invoke(self.consent());self.assertEqual(result.returncode,0,result.stderr)
        bad=self.consent();bad[-1]='0'*64
        self.assertNotEqual(self.invoke(bad).returncode,0)

    def test_future_expiry_and_regression_never_emit_body(self):
        edge=datetime.fromisoformat(self.obs['validated_at'])+timedelta(days=1)
        at=epoch(edge.isoformat());after=epoch((edge+timedelta(microseconds=1)).isoformat())
        gen=datetime.fromisoformat(GEN)
        for times in ([epoch((gen-timedelta(days=1)).isoformat())]*3,
                      [at,at,after],
                      [epoch(GEN),epoch((gen+timedelta(seconds=10)).isoformat()),epoch((gen+timedelta(seconds=5)).isoformat())]):
            self.now=times
            r=self.invoke();self.assertNotEqual(r.returncode,0);self.assertEqual(r.stdout,b'')

    def test_integrity_redirect_missing_lookup_and_duplicate_refuse(self):
        self.tree['bodies/'+self.rid+'.json']=self.body+b' '
        r=self.invoke();self.assertNotEqual(r.returncode,0);self.assertEqual(r.stdout,b'')
        self.tree=dict(self.base)
        r=self.invoke(env={**self.env(),'HTTP_STATUS':'302'})
        self.assertNotEqual(r.returncode,0);self.assertEqual(len(self.calls()),1)
        lines=self.tree['lookup.tsv'].splitlines()
        self.tree['lookup.tsv']+=lines[1]+b'\n'
        self.assertNotEqual(self.invoke().returncode,0)
        del self.tree['lookup.tsv']
        r=self.invoke();self.assertNotEqual(r.returncode,0);self.assertEqual(r.stdout,b'')

    def test_unavailable_removed_unmeasured_and_future_observation(self):
        for field,value in ((1,b'0'),(2,b'retired'),(4,b'-'),(7,b'9999999999.000000')):
            lines=self.base['lookup.tsv'].splitlines()
            for i,line in enumerate(lines):
                cols=line.split(b'\t')
                if cols[0]==ALIAS.encode():
                    cols[field]=value;lines[i]=b'\t'.join(cols)
            self.tree['lookup.tsv']=b'\n'.join(lines)+b'\n'
            r=self.invoke();self.assertNotEqual(r.returncode,0);self.assertEqual(len(self.calls()),1)

    def test_publisher_rejects_drifting_lookup_and_supports_retained_old_tree(self):
        bad=dict(self.base);bad['lookup.tsv']+=b'\n'
        with self.assertRaises(ValueError): validate(bad)
        del bad['lookup.tsv'];self.assertEqual(validate(bad),self.index)
        self.assertEqual(render(self.index,self.base['index.json']),self.base['lookup.tsv'])

    def test_same_length_hash_corruption_and_oversized_lookup_refuse(self):
        self.tree['bodies/'+self.rid+'.json']=self.body[:-1]+bytes([self.body[-1]^1])
        r=self.invoke();self.assertNotEqual(r.returncode,0);self.assertIn(b'hash mismatch',r.stderr)
        self.assertEqual(r.stdout,b'')
        self.tree=dict(self.base);self.tree['lookup.tsv']=b'x'*2_000_001
        r=self.invoke();self.assertNotEqual(r.returncode,0);self.assertEqual(r.stdout,b'')

    def test_missing_required_tool_is_visible_before_any_transfer(self):
        minimal=self.path/'minimal';minimal.mkdir()
        for name in ('curl','awk','date'):
            (minimal/name).symlink_to(self.bin/name if (self.bin/name).exists() else Path('/usr/bin')/name)
        r=self.invoke(env={**self.env(),'PATH':str(minimal)})
        self.assertNotEqual(r.returncode,0);self.assertIn(b'missing tool: sha256sum',r.stderr)
        self.assertEqual(self.calls(),[])
