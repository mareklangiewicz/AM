"""One collector run, end to end: GitHub's answers in, a catalog/ commit on main-marek out.

The fixture is a small AM checkout (three real recipes, their registry names)
with a bare origin standing in for GitHub's repository, and saved GitHub
release bodies standing in for the API. The run is the same two commands CI
runs: collect (read-only) writes a candidate; publish validates it with the
host's reader and commits it to main-marek, retrying after a rejected push.
"""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import catalog_run
import fixture_recipes

ROOT = Path(__file__).resolve().parents[2]
NVIM, OBSIDIAN = 16408992, 262342594
RECIPES = ['x86_64/nvim', 'x86_64/nvim-nightly', 'x86_64/obsidian']
# Copies, not the live tree: the without-upstream-recipes job deletes programs/.
RECIPES_COPY = Path(__file__).resolve().parent/'test-recipes'


def git(cwd, *args, env=None):
    return subprocess.run(['git', '-C', str(cwd), *args], check=True, capture_output=True, text=True,
                          env=dict(os.environ, **(env or {}))).stdout.strip()


def saved_bodies():
    """GitHub's release-list bodies for Neovim and Obsidian, saved by run 40529551070."""
    return {rid: raw for rid, (raw, _) in fixture_recipes.saved_bodies().items()}


class Fixture:
    def __init__(self, directory):
        self.base = Path(directory)
        self.origin = self.base/'origin.git'
        self.checkout = self.base/'checkout'
        self.evidence = self.base/'github'
        git(self.base, 'init', '-q', '--bare', '-b', 'main-marek', str(self.origin))
        git(self.base, 'clone', '-q', str(self.origin), str(self.checkout))
        for recipe in RECIPES:
            target = self.checkout/'programs'/recipe
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(RECIPES_COPY/recipe, target)
        collector = self.checkout/'tools/catalog-collector'
        collector.mkdir(parents=True)
        (collector/'collection-recipes.txt').write_text('\n'.join(RECIPES)+'\n')
        (collector/'collection-apps.json').write_text('[]\n')
        (collector/'source-names.json').write_text(json.dumps(
            dict(active={str(NVIM): 'nvim', str(OBSIDIAN): 'obsidian'}, retired=[])))
        self.commit_code('README.md', 'fixture\n', 'fixture checkout')
        self.evidence.mkdir()
        for rid, body in saved_bodies().items():
            (self.evidence/f'{rid}-releases.json').write_bytes(body)
            (self.evidence/f'{rid}-receipt.txt').write_text('2026-11-25T10:00:00Z\n')

    def commit_code(self, path, text, message, clone=None):
        clone = clone or self.checkout
        (clone/path).write_text(text)
        git(clone, 'add', '-A')
        git(clone, '-c', 'user.name=Marek', '-c', 'user.email=marek@example.org', 'commit', '-q', '-m', message)
        git(clone, 'push', '-q', 'origin', 'HEAD:main-marek')

    def run(self, run_id, *, env=None, tamper=None):
        """collect in a fresh checkout of main-marek's tip, then publish."""
        work = self.base/f'run-{run_id}'
        git(self.base, 'clone', '-q', '-b', 'main-marek', str(self.origin), str(work))
        candidate = self.base/f'candidate-{run_id}'
        catalog_run.main(['collect', '--checkout', str(work), '--output', str(candidate), '--run-id', str(run_id),
                          '--attempt', '1', '--evidence', str(self.evidence), '--now', '2026-11-25T10:00:05Z'])
        if tamper:
            tamper(candidate)
        old = dict(os.environ)
        os.environ.update(env or {})
        try:
            catalog_run.main(['publish', '--candidate', str(candidate), '--remote', str(self.origin),
                              '--scratch', str(self.base/f'publish-{run_id}'), '--run-id', str(run_id), '--attempt', '1'])
        finally:
            os.environ.clear()
            os.environ.update(old)

    def tip_files(self):
        return git(self.base, '--git-dir', str(self.origin), 'ls-tree', '-r', '--name-only', 'main-marek').splitlines()

    def show(self, path):
        return git(self.base, '--git-dir', str(self.origin), 'show', 'main-marek:'+path)


def accepted_by_host_reader(text):
    run = subprocess.run(['awk', '-f', str(ROOT/'modules/catalog-tables.am'), '-f', str(ROOT/'modules/catalog-parser.am')],
                         input=(text+'\n').encode(), capture_output=True)
    return run.returncode == 0


class CollectorRun(unittest.TestCase):
    def test_a_first_run_commits_the_whole_catalog_on_top_of_main_marek(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(directory)
            before = git(fixture.base, '--git-dir', str(fixture.origin), 'rev-parse', 'main-marek')
            fixture.run(41)
            catalog = sorted(path for path in fixture.tip_files() if path.startswith('catalog/'))
            self.assertEqual(catalog, ['catalog/apps.yaml', 'catalog/repositories/nvim.yaml', 'catalog/repositories/obsidian.yaml',
                                       'catalog/status/runs.yaml', 'catalog/status/statistics.yaml'])
            for path in catalog:
                with self.subTest(path=path):
                    self.assertTrue(accepted_by_host_reader(fixture.show(path)))
            self.assertEqual(git(fixture.base, '--git-dir', str(fixture.origin), 'rev-parse', 'main-marek^'), before)
            changed = git(fixture.base, '--git-dir', str(fixture.origin), 'diff', '--name-only', 'main-marek^', 'main-marek').splitlines()
            self.assertTrue(all(path.startswith('catalog/') for path in changed))
            self.assertIn('"41-1":', fixture.show('catalog/status/runs.yaml'))
            self.assertIn('  "nvim":\n    repository: "repositories/nvim.yaml"\n    x86_64:', fixture.show('catalog/apps.yaml'))
            self.assertIn('observed_at: "2026-11-25T10:00:00Z"', fixture.show('catalog/repositories/obsidian.yaml'))

    def test_a_push_rejected_by_a_newer_code_commit_is_rebased_and_retried(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(directory)
            racer = fixture.base/'racer'
            git(fixture.base, 'clone', '-q', '-b', 'main-marek', str(fixture.origin), str(racer))
            # The first push the publisher tries finds a newer main-marek: a
            # pre-push hook pushes Marek's code commit first, once.
            hooks = fixture.base/'hooks'
            hooks.mkdir()
            hook = hooks/'pre-push'
            hook.write_text(f'''#!/bin/sh
[ -e "{fixture.base}/raced" ] && exit 0
touch "{fixture.base}/raced"
cd "{racer}" && echo code > code.txt && git add code.txt &&
  git -c user.name=Marek -c user.email=marek@example.org commit -q -m code && git push -q origin HEAD:main-marek
''')
            hook.chmod(0o755)
            fixture.run(42, env=dict(GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='core.hooksPath', GIT_CONFIG_VALUE_0=str(hooks)))
            self.assertTrue((fixture.base/'raced').exists(), 'the race never happened')
            self.assertEqual(git(fixture.base, '--git-dir', str(fixture.origin), 'log', '-1', '--format=%s', 'main-marek^'), 'code')
            self.assertIn('code.txt', fixture.tip_files())
            self.assertIn('catalog/repositories/nvim.yaml', fixture.tip_files())

    def test_a_second_run_reads_the_first_runs_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(directory)
            fixture.run(43)
            first = fixture.show('catalog/repositories/nvim.yaml')
            fixture.run(44)
            runs = fixture.show('catalog/status/runs.yaml')
            self.assertIn('"43-1":', runs)
            self.assertIn('"44-1":', runs)
            self.assertEqual(fixture.show('catalog/repositories/nvim.yaml'), first)


    def test_a_candidate_the_host_reader_refuses_commits_only_its_run_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(directory)
            fixture.run(45)
            facts = {path: fixture.show(path) for path in fixture.tip_files() if path.startswith('catalog/repositories/')}
            def corrupt(candidate):
                target = candidate/'catalog/repositories/nvim.yaml'
                target.write_bytes(target.read_bytes()+b'unknown: 1\n')
            fixture.run(46, tamper=corrupt)
            changed = git(fixture.base, '--git-dir', str(fixture.origin), 'diff', '--name-only', 'main-marek^', 'main-marek').splitlines()
            self.assertEqual(changed, ['catalog/status/runs.yaml'])
            self.assertEqual({path: fixture.show(path) for path in facts}, facts)
            self.assertIn('"46-1":', fixture.show('catalog/status/runs.yaml'))
            self.assertIn('stop_reason: "internal"', fixture.show('catalog/status/runs.yaml').split('"46-1":')[1])


if __name__ == '__main__':
    unittest.main()
