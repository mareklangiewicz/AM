"""One collector run, end to end: GitHub's answers in, a catalog/ commit on main-marek out.

The fixture is a small AM checkout (three real recipes, enrolled in
catalog/apps.yaml through never-read repository files) with a bare origin
standing in for GitHub's repository, and saved GitHub
release bodies standing in for the API. The run is the same two commands CI
runs: collect (read-only) writes a candidate; publish validates it with the
host's reader and commits it to main-marek, retrying after a rejected push.
"""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import urllib.error

import catalog_run
import pinned_recipes
import git_observations
import fixture_enrollment
from fixture_enrollment import NVIM, OBSIDIAN
import fixture_recipes
import host_catalog

ROOT = Path(__file__).resolve().parents[2]
RECIPES = ['x86_64/nvim', 'x86_64/nvim-nightly', 'x86_64/obsidian']


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
        # Copies, not the live tree: the without-upstream-recipes job deletes programs/.
        fixture_enrollment.write(self.checkout, apps=fixture_enrollment.RECIPE_APPS, recipes=RECIPES)
        self.commit_code('README.md', 'fixture\n', 'fixture checkout')
        self.evidence.mkdir()
        for rid, body in saved_bodies().items():
            (self.evidence/f'{rid}-releases.json').write_bytes(body)
            (self.evidence/f'{rid}-receipt.txt').write_text('2026-11-25T10:00:00Z\n')

    def commit_code(self, path, text, message, clone=None):
        clone = clone or self.checkout
        if git(clone, 'ls-remote', 'origin', 'main-marek'):
            git(clone, 'pull', '-q', '--ff-only', 'origin', 'main-marek')  # take the runs' catalog/ commits
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

    def test_an_app_pointing_at_a_retired_name_refuses_the_run(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(directory)
            before = fixture.tip_files()
            fixture.commit_code('tools/catalog-collector/retired-names.yaml',
                                fixture_enrollment.retired_names(['obsidian']).decode(), 'retire obsidian\'s name')
            with self.assertRaisesRegex(ValueError, 'retired source name: obsidian'):
                fixture.run(47)
            self.assertEqual(fixture.tip_files(), before)
            self.assertNotIn('catalog/status/runs.yaml', fixture.tip_files())


def answering(answers):
    """host_catalog._response replaced: answers maps a repository id to a saved
    body, or to an exception raised for it (a failed read)."""
    def response(rid, evidence, allowance, **kwargs):
        answer = answers[int(rid)]
        if isinstance(answer, Exception):
            raise answer
        return answer, '2026-11-25T10:00:00Z'
    return patch.object(host_catalog, '_response', side_effect=response)


def http(code):
    return urllib.error.HTTPError('https://api.github.com/', code, 'x', {}, None)


class Failures(unittest.TestCase):
    """A failing repository gets failure fields, keeps its facts, and loses the fields on success."""
    def test_failure_fields_round_trip(self):
        bodies = saved_bodies()
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(directory)
            with answering({NVIM: http(404), OBSIDIAN: bodies[OBSIDIAN]}), \
                    patch.object(host_catalog, 'utc', return_value='2026-11-25T10:00:01Z'):
                fixture.run(50)
            gone = fixture.show('catalog/repositories/nvim.yaml')
            self.assertIn('failed_at: "2026-11-25T10:00:01Z"\nfailed_with: "not_found"\nreleases: {}', gone)
            self.assertNotIn('observed_at', gone)
            obsidian = fixture.show('catalog/repositories/obsidian.yaml')
            with answering({NVIM: bodies[NVIM], OBSIDIAN: OSError('reset')}), \
                    patch.object(host_catalog, 'utc', return_value='2026-11-25T11:00:00Z'):
                fixture.run(51)
            fixed = fixture.show('catalog/repositories/nvim.yaml')
            self.assertIn('observed_at: "2026-11-25T10:00:00Z"', fixed)
            self.assertNotIn('failed_', fixed)
            failing = fixture.show('catalog/repositories/obsidian.yaml')
            self.assertIn('failed_at: "2026-11-25T11:00:00Z"\nfailed_with: "transport"\n', failing)
            self.assertEqual(failing.replace('failed_at: "2026-11-25T11:00:00Z"\nfailed_with: "transport"\n', ''), obsidian)

    def test_a_run_wide_stop_records_no_repository_and_says_why(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(directory)
            with answering({NVIM: http(403), OBSIDIAN: http(403)}):
                fixture.run(52)
            # Each repository file is still as enrollment wrote it: never read.
            for name, rid, repository in fixture_enrollment.RECIPE_APPS.values():
                self.assertEqual(fixture.show(f'catalog/repositories/{name}.yaml')+'\n',
                                 fixture_enrollment.never_read(rid, repository).decode())
            self.assertIn('stop_reason: "quota"', fixture.show('catalog/status/runs.yaml'))


OBSIDIAN_ENTRY = '  "obsidian":\n    repository: "repositories/obsidian.yaml"\n    x86_64: "declaration"\n'
EXAMPLE_ENTRY = '  "example":\n    repository: "repositories/example.yaml"\n'


def enroll_example(fixture, clone=None):
    """Marek's hand enrollment: a never-read repository file, then an apps.yaml entry."""
    fixture.commit_code('catalog/repositories/example.yaml', fixture_enrollment.never_read(42, 'owner/example').decode(),
                        'enroll example: its repository file', clone=clone)
    apps = fixture.show('catalog/apps.yaml')+'\n'
    fixture.commit_code('catalog/apps.yaml', apps.replace('  "nvim":\n', EXAMPLE_ENTRY+'  "nvim":\n'), 'enroll example',
                        clone=clone)


class Enrollment(unittest.TestCase):
    """Marek enrolls and drops apps by hand in catalog/apps.yaml; runs only refresh its labels."""
    def answers(self):
        bodies = saved_bodies()
        return answering({42: b'[]', NVIM: bodies[NVIM], OBSIDIAN: bodies[OBSIDIAN]})

    def test_a_hand_added_entry_is_collected_on_the_next_run(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(directory)
            fixture.run(55)
            enroll_example(fixture)
            with self.answers():
                fixture.run(56)
            self.assertIn('repository: "owner/example"\nobserved_at: "2026-11-25T10:00:00Z"',
                          fixture.show('catalog/repositories/example.yaml'))
            self.assertIn(EXAMPLE_ENTRY, fixture.show('catalog/apps.yaml')+'\n')
            self.assertIn('enrolled: 3', fixture.show('catalog/status/runs.yaml').split('"56-1":')[1])

    def test_an_entry_added_during_a_run_is_kept_and_collected_next(self):
        # The run read apps.yaml before Marek's entry landed: its publish keeps
        # the tip's apps.yaml and removes nothing.
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(directory)
            fixture.run(57)
            marek = fixture.base/'marek'
            git(fixture.base, 'clone', '-q', '-b', 'main-marek', str(fixture.origin), str(marek))
            fixture.run(58, tamper=lambda candidate: enroll_example(fixture, clone=marek))
            self.assertIn('"58-1":', fixture.show('catalog/status/runs.yaml'))
            self.assertIn(EXAMPLE_ENTRY, fixture.show('catalog/apps.yaml')+'\n')
            self.assertIn('catalog/repositories/example.yaml', fixture.tip_files())
            with self.answers():
                fixture.run(59)
            self.assertIn('observed_at', fixture.show('catalog/repositories/example.yaml'))

    def test_a_removed_entrys_file_leaves_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(directory)
            fixture.run(53)
            self.assertIn('catalog/repositories/obsidian.yaml', fixture.tip_files())
            fixture.commit_code('tools/catalog-collector/collection-recipes.txt', 'x86_64/nvim\nx86_64/nvim-nightly\n',
                                'obsidian is not installable')
            fixture.commit_code('catalog/apps.yaml', (fixture.show('catalog/apps.yaml')+'\n').replace(OBSIDIAN_ENTRY, ''),
                                'drop obsidian')
            fixture.run(54)
            self.assertNotIn('catalog/repositories/obsidian.yaml', fixture.tip_files())
            self.assertNotIn('"obsidian":', fixture.show('catalog/apps.yaml'))
            self.assertIn('catalog/repositories/nvim.yaml', fixture.tip_files())


class Budget(unittest.TestCase):
    def test_a_full_batch_and_every_git_read_fit_the_request_allowance(self):
        # Run 45658789307 read 498 of 500: the Git reads took the last two
        # repositories' requests (stop_reason request_budget). The scopes are the
        # pinned recipes' Git selections (ticket 29).
        scopes = git_observations.configuration(pinned_recipes.shared_configuration())
        self.assertEqual(len(scopes), 5)
        git_requests = sum(scope['tags'] + sum(1 + len(files) for files in scope['branches'].values())
                           for scope in scopes.values())
        self.assertLessEqual(catalog_run.BATCH_SIZE + git_requests, host_catalog.REQUEST_CAP)


if __name__ == '__main__':
    unittest.main()
