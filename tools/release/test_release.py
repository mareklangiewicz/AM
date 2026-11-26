"""The main-marek release sequence, against scripted git and gh replies (ticket 38)."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import release

HEAD = 'h'*40
BASE = 'b'*40
TIP = 't'*40  # ci/x behind HEAD
R = ['-R', release.REPO]
ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT/'tools/catalog-contract/examples'


class Fake:
    """Answers each expected call in order; anything else fails the test."""
    def __init__(self, script):
        self.script = list(script)
        self.calls = []

    def __call__(self, argv):
        self.calls.append(argv)
        if not self.script:
            raise AssertionError('unexpected call '+' '.join(argv))
        expected, reply = self.script.pop(0)
        if argv != expected:
            raise AssertionError('expected '+' '.join(expected)+'\n     got '+' '.join(argv))
        return reply if isinstance(reply, tuple) else (0, reply)


def ok(value):
    return json.dumps(value)


START = [
    (['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 'main-marek\n'),
    (['git', 'fetch', '--quiet', 'origin', 'main-marek'], ''),
    (['git', 'rev-parse', 'HEAD'], HEAD+'\n'),
    (['git', 'rev-parse', 'origin/main-marek'], BASE+'\n'),
    (['git', 'merge-base', '--is-ancestor', BASE, HEAD], ''),
]


def changed(*paths):
    """The paths HEAD changes since origin/main-marek."""
    return [(['git', 'diff', '--name-only', BASE, HEAD], ''.join(path+'\n' for path in paths))]


GREEN_CI = [
    (['git', 'ls-remote', 'origin', 'refs/heads/ci/x'], HEAD+'\trefs/heads/ci/x\n'),
    (['gh', 'run', 'list', '--workflow', 'long-tests.yml', '--branch', 'ci/x', '--commit', HEAD,
      '--limit', '1', '--json', 'databaseId,status,conclusion', *R],
     ok([dict(databaseId=11, status='completed', conclusion='success')])),
]


def long_tests(commit, rows):
    return (['gh', 'run', 'list', '--workflow', 'long-tests.yml', '--branch', 'ci/x', '--commit', commit,
             '--limit', '1', '--json', 'databaseId,status,conclusion', *R], ok(rows))


GREEN = [dict(databaseId=11, status='completed', conclusion='success')]


def tip_behind(diff):
    """ci/x at TIP, an ancestor of HEAD, and the paths HEAD changed since."""
    return [(['git', 'ls-remote', 'origin', 'refs/heads/ci/x'], TIP+'\trefs/heads/ci/x\n'),
            (['git', 'merge-base', '--is-ancestor', TIP, HEAD], ''),
            (['git', 'diff', '--name-only', TIP, HEAD], diff)]


DEPLOYED = ['curl', '-fsS', '--max-time', '20', release.DEPLOYED_SCHEMA]


def browser(deployed=(0, 'schema'), ours='schema'):
    """The deployed page's schema.mjs against HEAD's."""
    return [(DEPLOYED, deployed), (['git', 'show', HEAD+':'+release.SCHEMA], ours)]


PUSH = [(['git', 'push', 'origin', 'HEAD:refs/heads/main-marek'], '')]
FAST = [(['gh', 'run', 'list', '--workflow', 'tests.yml', '--event', 'push', '--commit', HEAD,
          '--limit', '1', '--json', 'databaseId', *R], ok([dict(databaseId=21)]))]


def never(head):
    raise AssertionError('validated catalog/ without a contract or catalog/ change')


def ship(script, **options):
    run = Fake(script)
    lines = []
    options.setdefault('validate', never)
    result = release.ship(run, out=lines.append, sleep=lambda s: None, **options)
    return run, result, lines


class Refusals(unittest.TestCase):
    def refused(self, script, pattern, **options):
        run = Fake(script)
        options.setdefault('validate', never)
        with self.assertRaisesRegex(release.Refused, pattern):
            release.ship(run, out=lambda line: None, sleep=lambda s: None, **options)
        self.assertFalse(any(call[:2] == ['git', 'push'] for call in run.calls))
        self.assertEqual(run.script, [], 'refused before the scripted calls ran out')

    def test_other_branch(self):
        self.refused([(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 'ci/x\n')], 'main-marek')

    def test_nothing_to_ship(self):
        self.refused(START[:3]+[(['git', 'rev-parse', 'origin/main-marek'], HEAD+'\n')], 'nothing')

    def diverged(self, origin_changed):
        """HEAD is not a fast-forward, and origin's commits HEAD lacks change `origin_changed`."""
        return START[:4]+[(['git', 'merge-base', '--is-ancestor', BASE, HEAD], (1, '')),
                          (['git', 'diff', '--name-only', HEAD+'...'+BASE], ''.join(p+'\n' for p in origin_changed))]

    def test_not_a_fast_forward(self):
        self.refused(self.diverged(['modules/a.am', 'catalog/apps.yaml']), 'fast-forward')

    def test_not_a_fast_forward_by_collector_commits_says_to_merge(self):
        self.refused(self.diverged(['catalog/apps.yaml', 'catalog/status/runs.yaml']),
                     r'fast-forward.*only catalog/.*git merge origin/main-marek')

    def test_not_a_fast_forward_by_code_does_not_suggest_a_merge(self):
        run = Fake(self.diverged(['catalog/apps.yaml', 'modules/a.am']))
        with self.assertRaises(release.Refused) as raised:
            release.ship(run, out=lambda line: None, sleep=lambda s: None, validate=never)
        self.assertNotIn('git merge', str(raised.exception))
        self.assertEqual(run.script, [])

    def test_code_change_without_ci(self):
        self.refused(START+changed('docs/a.md', 'catalog/apps.yaml', 'modules/appimage.am'), 'modules/appimage.am$')

    def test_ci_branch_elsewhere(self):
        self.refused(START+changed('modules/a.am')+tip_behind('')[:1]
                     + [(['git', 'merge-base', '--is-ancestor', TIP, HEAD], (1, ''))],
                     'ci/x is not HEAD or an ancestor', ci='x')

    def test_ci_branch_behind_head_by_code(self):
        self.refused(START+changed('modules/appimage.am')+tip_behind('docs/a.md\nmodules/appimage.am\n'),
                     'since ci/x: modules/appimage.am$', ci='x')

    def test_ci_branch_behind_head_by_docs_but_not_green(self):
        self.refused(START+changed('modules/a.am')+tip_behind('docs/a.md\n')+[long_tests(TIP, [])], 'Long tests', ci='x')

    def test_ci_branch_missing(self):
        self.refused(START+changed('modules/a.am')+[(['git', 'ls-remote', 'origin', 'refs/heads/ci/x'], '')], 'ci/x', ci='x')

    def test_long_tests_not_green(self):
        for runs in ([], [dict(databaseId=11, status='in_progress', conclusion='')],
                     [dict(databaseId=11, status='completed', conclusion='failure')]):
            with self.subTest(runs=runs):
                self.refused(START+changed('modules/a.am')+GREEN_CI[:1]+[(GREEN_CI[1][0], ok(runs))], 'Long tests', ci='x')

    def test_a_contract_change_refuses_while_catalog_fails_heads_readers(self):
        for path in sorted(release.CONTRACT):
            with self.subTest(path=path):
                self.refused(START+changed(path)+GREEN_CI, 'catalog/ fails HEAD.*repositories/a.yaml: awk: bad', ci='x',
                             validate=lambda head: ['catalog/repositories/a.yaml: awk: bad'])

    def test_a_catalog_change_is_validated_too(self):
        self.refused(START+changed('catalog/apps.yaml'), 'catalog/ fails HEAD',
                     validate=lambda head: ['catalog/apps.yaml: node: bad'])


class Ship(unittest.TestCase):
    def test_a_tested_change_pushes_and_names_its_fast_tests_run(self):
        run, result, lines = ship(START+changed('programs/x86_64/a')+GREEN_CI+browser()+PUSH+FAST, ci='x')
        self.assertEqual(run.script, [])
        self.assertEqual(result, dict(fast=21))
        self.assertTrue(any('21' in line for line in lines))

    def test_documentation_after_the_tested_commit_ships_on_its_long_tests(self):
        run, result, lines = ship(START+changed('modules/a.am', 'docs/a.md')+tip_behind('docs/a.md\n')
                                  + [long_tests(TIP, GREEN)]+browser()+PUSH+FAST, ci='x')
        self.assertEqual(run.script, [])
        self.assertEqual(result, dict(fast=21))
        self.assertIn('Long tests 11 green on ci/x at '+TIP+'; HEAD adds only docs/ and catalog/', lines)

    def test_documentation_only_needs_no_ci(self):
        run, result, _ = ship(START+changed('docs/a.md', 'docs/track/b.md')+browser()+PUSH+FAST)
        self.assertEqual(run.script, [])
        self.assertEqual(result, dict(fast=21))

    def test_catalog_only_needs_no_ci_and_starts_no_fast_tests(self):
        seen = []
        run, result, lines = ship(START+changed('catalog/apps.yaml')+browser()+PUSH,
                                  validate=lambda head: seen.append(head) or [])
        self.assertEqual(run.script, [])
        self.assertEqual(result, {})
        self.assertEqual(seen, [HEAD])
        self.assertIn('no Fast tests run: HEAD changes only catalog/', lines)

    def test_a_contract_change_validates_catalog_under_head_once(self):
        seen = []
        run, result, lines = ship(START+changed('modules/catalog-parser.am')+GREEN_CI+browser()+PUSH+FAST, ci='x',
                                  validate=lambda head: seen.append(head) or [])
        self.assertEqual(run.script, [])
        self.assertEqual(seen, [HEAD])
        self.assertIn("catalog/ valid under HEAD's readers", lines)


class Plan(unittest.TestCase):
    """plan answers from the same decision as ship and never writes (ticket 40)."""
    def plan(self, script, **options):
        run = Fake(script)
        lines = []
        options.setdefault('validate', never)
        release.plan(run, out=lines.append, **options)
        self.assertEqual(run.script, [])
        self.assertFalse(any(call[:2] == ['git', 'push'] for call in run.calls))
        return '\n'.join(lines)

    def test_a_tested_change_would_push_and_start_fast_tests(self):
        text = self.plan(START+changed('programs/x86_64/a', 'modules/b.am')+GREEN_CI+browser(), ci='x')
        self.assertIn('Long tests 11 green on ci/x', text)
        self.assertIn('would push '+HEAD, text)
        self.assertIn('Fast tests would run', text)

    def test_catalog_only_would_start_no_fast_tests(self):
        text = self.plan(START+changed('catalog/apps.yaml')+browser(), validate=lambda head: [])
        self.assertIn('would push '+HEAD, text)
        self.assertIn('no Fast tests run: HEAD changes only catalog/', text)

    def test_a_contract_change_would_validate_catalog_first(self):
        text = self.plan(START+changed('schemas/catalog.schema.yaml')+GREEN_CI+browser(), ci='x', validate=lambda head: [])
        self.assertIn("catalog/ valid under HEAD's readers", text)

    def test_a_drifted_browser_says_to_redeploy(self):
        text = self.plan(START+changed('programs/x86_64/a')+GREEN_CI+browser(deployed=(0, 'old'), ours='new'), ci='x')
        self.assertIn('deployed page schema differs from HEAD', text)
        self.assertIn('catalog-pages.yml', text)

    def test_a_matching_browser_says_so(self):
        text = self.plan(START+changed('programs/x86_64/a')+GREEN_CI+browser(), ci='x')
        self.assertIn('deployed page schema matches HEAD', text)

    def test_an_unreachable_browser_is_reported_not_fatal(self):
        text = self.plan(START+changed('programs/x86_64/a')+GREEN_CI+browser(deployed=(22, ''))[:-1], ci='x')
        self.assertIn('would push', text)
        self.assertIn('deployed page schema unreadable (curl exit 22)', text)

    def test_a_refusal_is_printed_not_raised(self):
        text = self.plan(START+changed('modules/appimage.am'))
        self.assertIn('would refuse: changes outside docs/ and catalog/', text)
        self.assertNotIn('would push', text)


class ValidateCatalog(unittest.TestCase):
    """HEAD's catalog/ through HEAD's own awk and JS readers, in a real repository."""
    def commit(self, repo, files):
        for path in release.READERS:
            (repo/path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT/path, repo/path)
        for path, source in files.items():
            (repo/path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(EXAMPLES/source, repo/path)
        git = ['git', '-C', str(repo), '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'core.hooksPath=/dev/null']
        subprocess.run(['git', 'init', '-q', str(repo)], check=True)
        subprocess.run(git+['add', '.'], check=True)
        subprocess.run(git+['commit', '-qm', 'x'], check=True)
        return subprocess.check_output(git+['rev-parse', 'HEAD'], text=True).strip()

    def test_each_reader_names_the_file_it_refuses(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            head = self.commit(repo, {'catalog/apps.yaml': 'apps.yaml', 'catalog/repositories/a.yaml': 'repository.yaml',
                                      'catalog/status/statistics.yaml': 'bad-null.yaml'})
            problems = release.validate_catalog(head, repo=str(repo))
        self.assertEqual([problem.split(':')[0] for problem in problems],
                         ['catalog/status/statistics.yaml (awk)', 'catalog/status/statistics.yaml (node)'], problems)

    def test_a_valid_catalog_has_no_problems(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            head = self.commit(repo, {'catalog/apps.yaml': 'apps.yaml', 'catalog/status/runs.yaml': 'runs.yaml'})
            self.assertEqual(release.validate_catalog(head, repo=str(repo)), [])

    def test_no_catalog_is_a_problem(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            head = self.commit(repo, {})
            self.assertEqual(release.validate_catalog(head, repo=str(repo)), ['HEAD has no catalog/ files'])


def view(run_id, status, conclusion=''):
    return (['gh', 'run', 'view', str(run_id), '--json', 'status,conclusion', *R],
            ok(dict(status=status, conclusion=conclusion)))


class Output(unittest.TestCase):
    def test_lines_reach_a_pipe_as_they_happen(self):
        import io
        from unittest.mock import patch
        stream = io.StringIO()
        flushed = []
        stream.flush = lambda: flushed.append(stream.getvalue())
        with patch('sys.stdout', stream):
            release.say('one')
        self.assertEqual(flushed, ['one\n'])


class Watch(unittest.TestCase):
    def watch(self, script, minutes=10, out=lambda line: None):
        now = [0.0]
        run = Fake(script)
        def sleep(seconds): now[0] += seconds
        good = release.watch(run, dict(fast=21, catalog=31), minutes, out=out,
                             sleep=sleep, clock=lambda: now[0])
        self.assertEqual(run.script, [])
        return good

    def test_all_green(self):
        self.assertEqual(self.watch([view(21, 'in_progress'), view(31, 'queued'),
                                     view(21, 'completed', 'success'), view(31, 'completed', 'success')]), release.GREEN)

    def test_one_failure(self):
        self.assertEqual(self.watch([view(21, 'completed', 'failure'), view(31, 'completed', 'success')]), release.RED)

    def test_deadline_is_not_a_failure_and_says_how_to_continue(self):
        polls = int(60/release.POLL_SECONDS)
        lines = []
        state = self.watch([view(21, 'completed', 'success')]+[view(31, 'in_progress')]*(polls+1),
                           minutes=1, out=lines.append)
        self.assertEqual(state, release.RUNNING)
        self.assertIn('release.py watch 31', lines[-1])
        self.assertNotIn('21', lines[-1])

    def test_the_continue_command_keeps_the_watch_length(self):
        polls = -int(-90//release.POLL_SECONDS)
        lines = []
        self.watch([view(21, 'completed', 'success')]+[view(31, 'in_progress')]*(polls+1),
                   minutes=1.5, out=lines.append)
        self.assertTrue(lines[-1].endswith(' --minutes 1.5'), lines[-1])

    def test_a_failure_is_reported_even_if_another_run_is_still_going(self):
        polls = int(60/release.POLL_SECONDS)
        self.assertEqual(self.watch([view(21, 'completed', 'failure')]+[view(31, 'in_progress')]*(polls+1),
                                    minutes=1), release.RED)


class Resume(unittest.TestCase):
    def test_without_ids_it_watches_every_run_on_the_pushed_commit(self):
        run = Fake([
            (['git', 'fetch', '--quiet', 'origin', 'main-marek'], ''),
            (['git', 'rev-parse', 'origin/main-marek'], HEAD+'\n'),
            (['gh', 'run', 'list', '--commit', HEAD, '--limit', '20', '--json', 'databaseId,workflowName', *R],
             ok([dict(databaseId=21, workflowName='Fast tests'),
                 dict(databaseId=31, workflowName='YAML release catalog'),
                 dict(databaseId=12, workflowName='Fast tests')])),  # gh lists newest first
        ])
        self.assertEqual(release.pushed_runs(run), {'Fast tests': 21, 'YAML release catalog': 31})
        self.assertEqual(run.script, [])

    def test_ci_finds_the_long_tests_run_of_head_not_the_latest_on_the_branch(self):
        listed = (['gh', 'run', 'list', '--workflow', 'long-tests.yml', '--branch', 'ci/x', '--commit', HEAD,
                   '--limit', '1', '--json', 'databaseId', *R])
        run = Fake([(['git', 'rev-parse', 'HEAD'], HEAD+'\n'), (listed, ok([])), (listed, ok([dict(databaseId=13)]))])
        self.assertEqual(release.long_tests_run(run, 'x', sleep=lambda s: None), {'Long tests': 13})
        self.assertEqual(run.script, [])

    def test_given_ids_are_watched_as_they_are(self):
        self.assertEqual(release.named(['44', '45']), {'44': 44, '45': 45})



VIEW = ['gh', 'run', 'view', '7', '--json', 'status,conclusion', *R]
DENIED = (1, '')  # HTTP 401 "Bad credentials" with a valid login (ticket 48)


class Retrying(unittest.TestCase):
    """A transient gh failure is retried a bounded number of times (ticket 48)."""
    def test_one_failure_then_success_completes_after_one_pause(self):
        pauses = []
        run = Fake([(VIEW, DENIED), (VIEW, 'done')])
        self.assertEqual(release.retrying(run, sleep=pauses.append)(VIEW), (0, 'done'))
        self.assertEqual(run.script, [])
        self.assertEqual(pauses, [release.RETRY_SECONDS])

    def test_repeated_failures_stop_after_three_attempts_and_name_the_command(self):
        pauses = []
        run = Fake([(VIEW, DENIED)]*3)
        with self.assertRaises(RuntimeError) as raised:
            release.gh(release.retrying(run, sleep=pauses.append), 'run', 'view', '7', '--json', 'status,conclusion')
        self.assertEqual(run.script, [])
        self.assertEqual(len(pauses), 2)
        self.assertIn('after 3 attempts', str(raised.exception))
        self.assertIn('gh run view 7', str(raised.exception))

    def test_git_is_tried_once_since_its_exit_codes_are_answers(self):
        ancestor = ['git', 'merge-base', '--is-ancestor', BASE, HEAD]
        run = Fake([(ancestor, (1, ''))])
        self.assertEqual(release.retrying(run, sleep=self.fail)(ancestor), (1, ''))
        self.assertEqual(run.script, [])

    def test_watch_survives_a_failed_run_view_while_the_run_is_going(self):
        from unittest.mock import patch
        run = Fake([(VIEW, DENIED), (VIEW, ok(dict(status='completed', conclusion='success')))])
        with patch.object(release, 'system', run), patch.object(release, 'RETRY_SECONDS', 0), self.assertRaises(SystemExit) as done:
            release.main(['watch', '7'])
        self.assertEqual(done.exception.code, 0)
        self.assertEqual(run.script, [])

if __name__ == '__main__':
    unittest.main()
