"""The host reads raw main-marek/catalog/ files: catalog-yaml.am end to end.

catalog/ is built by documents.py from GitHub release bodies saved by run
40529551070 (Obsidian, Neovim) and committed to main-marek in a bare
repository. A fake curl serves https://raw.githubusercontent.com/<repo>/main-marek/catalog/<path>
from it, as raw GitHub would; recipes run catalog-yaml.am as they do on a host.
Expected answers are read off the saved bodies by hand.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import documents
import test_catalog_run as run_fixture

ROOT = Path(__file__).resolve().parents[2]
SOURCE = 'https://raw.githubusercontent.com/selected-owner/selected.repo/main-marek'
RECEIVED = '2026-10-27T15:17:57Z'
NOW = '2026-10-28T10:00:00Z'
MODULES = ('catalog-yaml.am', 'catalog-reader.am', 'catalog-parser.am', 'catalog-tables.am', 'catalog-yaml-policy.am')
CURL = r'''import json,os,pathlib,re,subprocess,sys
p=pathlib.Path(os.environ['FIXTURE']); args=sys.argv[1:]; url=args[-1]
with (p/'calls').open('a') as f: f.write(url+'\n')
assert args[0]=='-q' and '-L' not in args and args[args.index('--max-redirs')+1]=='0'
m=re.fullmatch(r'https://raw\.githubusercontent\.com/selected-owner/selected\.repo/main-marek/(catalog/[a-z0-9_./+-]+)',url)
assert m,url
missing=p/'missing-once'
if missing.exists() and missing.read_text()==m.group(1):
    missing.unlink(); print('404',end=''); sys.exit(0)
shown=subprocess.run(['git','--git-dir',os.environ['REMOTE'],'show','main-marek:'+m.group(1)],capture_output=True)
if shown.returncode: print('404',end=''); sys.exit(0)
pathlib.Path(args[args.index('--output')+1]).write_bytes(shown.stdout)
print('200',end='')
'''
DATE = r'''import datetime,os,sys
s=os.environ['CLOCK'];d=datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
f=sys.argv[-1]
if f=='+%s %Y-%m-%dT%H:%M:%SZ': print(str(int(d.timestamp()))+' '+s)
else: raise ValueError(f)
'''


def catalog_tree():
    bodies = run_fixture.saved_bodies()
    tree = {}
    for rid, name, repository in ((run_fixture.OBSIDIAN, 'obsidian', 'obsidianmd/obsidian-releases'),
                                  (run_fixture.NVIM, 'nvim', 'neovim/neovim')):
        from bounded import normalize
        raw = json.loads(bodies[rid])
        acquired = dict(received_at=RECEIVED, releases=normalize(raw, 100, allow_missing_published=True), history_complete=False)
        tree[f'catalog/repositories/{name}.yaml'] = documents.encode('repository', documents.repository(
            None, acquired, repository_id=rid, repository=repository))
    apps = dict(apps={'nvim': dict(repository='repositories/nvim.yaml', x86_64='declaration'),
                      'nvim-nightly': dict(repository='repositories/nvim.yaml', x86_64='declaration'),
                      'obsidian': dict(repository='repositories/obsidian.yaml', x86_64='declaration')})
    tree['catalog/apps.yaml'] = documents.encode('apps', apps)
    return tree


class HostCatalog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='host-catalog-')
        cls.addClassCleanup(cls.tmp.cleanup)
        base = Path(cls.tmp.name)
        cls.remote = base/'origin.git'
        work = base/'work'
        subprocess.run(['git', 'init', '-q', '--bare', '-b', 'main-marek', str(cls.remote)], check=True)
        subprocess.run(['git', 'init', '-q', '-b', 'main-marek', str(work)], check=True)
        for path, raw in catalog_tree().items():
            (work/path).parent.mkdir(parents=True, exist_ok=True)
            (work/path).write_bytes(raw)
        for command in (['add', '-A'], ['-c', 'user.name=t', '-c', 'user.email=t@example.org', 'commit', '-q', '-m', 'catalog'],
                        ['push', '-q', str(cls.remote), 'HEAD:main-marek']):
            subprocess.run(['git', '-C', str(work), *command], check=True)

    def setUp(self):
        case = tempfile.TemporaryDirectory(prefix='host-case-')
        self.addCleanup(case.cleanup)
        self.path = Path(case.name)
        self.modules = self.path/'modules'
        self.modules.mkdir()
        for name in MODULES:
            shutil.copyfile(ROOT/'modules'/name, self.modules/name)
        self.bin = self.path/'bin'
        self.bin.mkdir()
        for name, body in (('curl', CURL), ('date', DATE), ('sleep', 'pass\n')):
            (self.bin/name).write_text('#!'+sys.executable+'\n'+body)
            (self.bin/name).chmod(0o755)

    def select(self, recipe, *options, clock=NOW, session=None):
        env = dict(os.environ, PATH=f'{self.bin}:{os.environ["PATH"]}', FIXTURE=str(self.path), REMOTE=str(self.remote),
                   CLOCK=clock, AMREPO=SOURCE)
        env.pop('AM_CATALOG_SESSION', None)
        if session:
            env['AM_CATALOG_SESSION'] = str(session)
        return subprocess.run(['sh', str(self.modules/'catalog-yaml.am'), recipe, *options], env=env, capture_output=True)

    def calls(self):
        path = self.path/'calls'
        return path.read_text().splitlines() if path.exists() else []

    def test_a_recipe_gets_its_download_url_from_raw_catalog_files(self):
        run = self.select('x86_64/obsidian', '--url')
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout.decode(),
                         'https://github.com/obsidianmd/obsidian-releases/releases/download/v1.14.5/Obsidian-1.14.5.AppImage\n')
        self.assertEqual(self.calls(), [SOURCE+'/catalog/apps.yaml', SOURCE+'/catalog/repositories/obsidian.yaml'])

    def test_the_full_selection_names_repository_release_asset_time_and_url(self):
        run = self.select('x86_64/obsidian')
        self.assertEqual(run.returncode, 0, run.stderr)
        lines = run.stdout.decode().splitlines()
        self.assertEqual(len(lines), 5)
        self.assertEqual((lines[0], lines[1], lines[3]), ('262342594', '420802120', RECEIVED))
        self.assertTrue(lines[4].endswith('/Obsidian-1.14.5.AppImage'))

    def test_a_file_missing_once_behind_the_cdn_is_retried(self):
        (self.path/'missing-once').write_text('catalog/repositories/obsidian.yaml')
        run = self.select('x86_64/obsidian', '--url')
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(self.calls().count(SOURCE+'/catalog/repositories/obsidian.yaml'), 2)

    def test_a_session_reads_each_file_once(self):
        session = self.path/'session'
        session.mkdir()
        for recipe in ('x86_64/obsidian', 'x86_64/nvim', 'x86_64/obsidian'):
            run = self.select(recipe, '--url', session=session)
            self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(sorted(self.calls()), sorted([SOURCE+'/catalog/apps.yaml', SOURCE+'/catalog/repositories/obsidian.yaml',
                                                       SOURCE+'/catalog/repositories/nvim.yaml']))

    def test_old_data_warns_and_still_selects(self):
        run = self.select('x86_64/obsidian', '--url', clock='2026-11-20T10:00:00Z')
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn(b'warning: obsidian catalog data last seen 23 days ago', run.stderr)

    def test_removed_options_are_refused_by_name(self):
        for option in ('--commit', '--updated-at'):
            with self.subTest(option=option):
                run = self.select('x86_64/obsidian', option, 'a'*40)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn(option.encode(), run.stderr)
                self.assertEqual(self.calls(), [])


if __name__ == '__main__':
    unittest.main()
