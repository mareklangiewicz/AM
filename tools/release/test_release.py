"""The main-marek release sequence, against scripted git and gh replies (ticket 38)."""
import json
import unittest

import release

HEAD = 'h'*40
BASE = 'b'*40
PIN = 'p'*40
SCHEMA_PIN = 's'*40
TIP = 't'*40  # ci/x behind HEAD
R = ['-R', release.REPO]
GATE = ['git', 'diff', '--name-only', PIN, HEAD, '--', *release.schedule_gate_paths()]
# The collector refuses a checkout whose schemas scope differs from this pin.
SCHEMA_GATE = ['git', 'diff', '--name-only', SCHEMA_PIN, HEAD, '--', *release.INPUT_SCOPES['schemas']]


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


PUSH = [(['git', 'push', 'origin', 'HEAD:refs/heads/main-marek'], '')]
PIN_READ = [(['gh', 'variable', 'get', 'CATALOG_SCHEDULE_REVISION', *R], PIN+'\n')]


def pins(gate='', schemas='', deployed=(0, 'defs'), ours='defs'):
    """Both pin reads and their diffs against HEAD, then the deployed browser
    definitions against HEAD's, as decide makes them."""
    return PIN_READ+[(GATE, gate),
                     (['gh', 'variable', 'get', 'CATALOG_SCHEMA_REVISION', *R], SCHEMA_PIN+'\n'),
                     (SCHEMA_GATE, schemas),
                     (DEPLOYED, deployed),
                     (['git', 'show', HEAD+':'+release.DEFINITIONS], ours)]


DEPLOYED = ['curl', '-fsS', '--max-time', '20', release.DEPLOYED_DEFINITIONS]


SCHEMA_REPIN = [(['gh', 'variable', 'set', 'CATALOG_SCHEMA_REVISION', '--body', HEAD, *R], '')]
FAST = [(['gh', 'run', 'list', '--workflow', 'tests.yml', '--event', 'push', '--commit', HEAD,
          '--limit', '1', '--json', 'databaseId', *R], ok([dict(databaseId=21)]))]
DISPATCHED = ['gh', 'run', 'list', '--workflow', 'catalog.yml', '--event', 'workflow_dispatch', '--commit', HEAD,
              '--json', 'databaseId', *R]
REPIN = [
    (['gh', 'variable', 'set', 'CATALOG_SCHEDULE_REVISION', '--body', HEAD, *R], ''),
    (DISPATCHED, ok([dict(databaseId=5)])),
    (['gh', 'workflow', 'run', 'catalog.yml', '--ref', 'main-marek', *R], ''),
    (DISPATCHED, ok([dict(databaseId=31), dict(databaseId=5)])),
]


def ship(script, **options):
    run = Fake(script)
    lines = []
    options.setdefault('validate', lambda run: [])
    result = release.ship(run, out=lines.append, sleep=lambda s: None, **options)
    return run, result, lines


class Refusals(unittest.TestCase):
    def refused(self, script, pattern, **options):
        run = Fake(script)
        options.setdefault('validate', lambda run: [])
        with self.assertRaisesRegex(release.Refused, pattern):
            release.ship(run, out=lambda line: None, sleep=lambda s: None, **options)
        self.assertFalse(any(call[:2] == ['git', 'push'] or call[:3] == ['gh', 'variable', 'set']
                             or call[:3] == ['gh', 'workflow', 'run'] for call in run.calls))
        self.assertEqual(run.script, [], 'refused before the scripted calls ran out')

    def test_other_branch(self):
        self.refused([(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 'ci/x\n')], 'main-marek')

    def test_nothing_to_ship(self):
        self.refused(START[:3]+[(['git', 'rev-parse', 'origin/main-marek'], HEAD+'\n')], 'nothing')

    def test_not_a_fast_forward(self):
        self.refused(START[:4]+[(['git', 'merge-base', '--is-ancestor', BASE, HEAD], (1, ''))], 'fast-forward')

    def test_code_change_without_ci(self):
        self.refused(START+[(['git', 'diff', '--name-only', BASE, HEAD], 'docs/a.md\nmodules/appimage.am\n')],
                     'modules/appimage.am')

    def test_ci_branch_elsewhere(self):
        self.refused(START+tip_behind('')[:1]+[(['git', 'merge-base', '--is-ancestor', TIP, HEAD], (1, ''))],
                     'ci/x is not HEAD or an ancestor', ci='x')

    def test_ci_branch_behind_head_by_code(self):
        self.refused(START+tip_behind('docs/a.md\nmodules/appimage.am\n'), 'since ci/x: modules/appimage.am$', ci='x')

    def test_ci_branch_behind_head_by_docs_but_not_green(self):
        self.refused(START+tip_behind('docs/a.md\n')+[long_tests(TIP, [])], 'Long tests', ci='x')

    def test_ci_branch_missing(self):
        self.refused(START+[(['git', 'ls-remote', 'origin', 'refs/heads/ci/x'], '')], 'ci/x', ci='x')

    def test_long_tests_not_green(self):
        for runs in ([], [dict(databaseId=11, status='in_progress', conclusion='')],
                     [dict(databaseId=11, status='completed', conclusion='failure')]):
            with self.subTest(runs=runs):
                self.refused(START+GREEN_CI[:1]+[(GREEN_CI[1][0], ok(runs))], 'Long tests', ci='x')

    def test_a_schemas_scope_change_needs_a_reviewed_schema_repin(self):
        # The collector compares the raw scope, so a README there counts too.
        for path in ('schemas/catalog/summary.schema.json', 'tools/catalog-contract/README.md'):
            with self.subTest(path=path):
                self.refused(START+GREEN_CI+pins(path+'\n', path+'\n')[:4], 'CATALOG_SCHEMA_REVISION.*--repin-schemas',
                             ci='x')

    def test_a_schema_repin_refuses_while_live_refs_fail_heads_contract(self):
        changed = 'schemas/catalog/summary.schema.json\n'
        script = START+GREEN_CI+pins(changed, changed)[:4]
        self.refused(script, 'catalog-status-v1 .*summary', ci='x', repin_schemas=True,
                     validate=lambda run: ['catalog-status-v1 '+'c'*40+': summary property'])

    def test_repin_schemas_without_a_schemas_scope_change(self):
        self.refused(START+GREEN_CI+pins('programs/x86_64/a\n', '')[:4], 'nothing to repin', ci='x', repin_schemas=True)


class Ship(unittest.TestCase):
    def test_tested_change_to_collection_inputs_repins_and_dispatches(self):
        run, result, lines = ship(START+GREEN_CI+pins('programs/x86_64/a\n')+PUSH+REPIN+FAST, ci='x')
        self.assertEqual(run.script, [])
        self.assertEqual(result, dict(fast=21, catalog=31))
        self.assertTrue(any('31' in line for line in lines) and any('21' in line for line in lines))

    def test_tested_change_outside_collection_inputs_keeps_the_pin(self):
        run, result, lines = ship(START+GREEN_CI+pins('')+PUSH+FAST, ci='x')
        self.assertEqual(run.script, [])
        self.assertEqual(result, dict(fast=21))
        self.assertIn('CATALOG_SCHEMA_REVISION stays '+SCHEMA_PIN, '\n'.join(lines))

    def test_reviewed_schemas_change_repins_both_pins_before_the_dispatch(self):
        changed = 'schemas/catalog/summary.schema.json\n'
        run, result, lines = ship(START+GREEN_CI+pins(changed, changed)+PUSH+REPIN[:1]+SCHEMA_REPIN+REPIN[1:]+FAST,
                                  ci='x', repin_schemas=True)
        self.assertEqual(run.script, [])
        self.assertEqual(result, dict(fast=21, catalog=31))
        self.assertIn('CATALOG_SCHEMA_REVISION '+SCHEMA_PIN+' -> '+HEAD, '\n'.join(lines))

    def test_a_schema_repin_dispatches_even_when_the_gate_ignores_the_change(self):
        # The gate skips READMEs, but the collector checks the raw schemas scope.
        run, result, _ = ship(START+GREEN_CI+pins('', 'tools/catalog-contract/README.md\n')+PUSH+REPIN[:1]
                              + SCHEMA_REPIN+REPIN[1:]+FAST, ci='x', repin_schemas=True)
        self.assertEqual(run.script, [])
        self.assertEqual(result, dict(fast=21, catalog=31))

    def test_documentation_after_the_tested_commit_ships_on_its_long_tests(self):
        run, result, lines = ship(START+tip_behind('docs/a.md\n')+[long_tests(TIP, GREEN)]+pins('')+PUSH+FAST, ci='x')
        self.assertEqual(run.script, [])
        self.assertEqual(result, dict(fast=21))
        self.assertIn('Long tests 11 green on ci/x at '+TIP+'; HEAD adds only docs/', lines)

    def test_documentation_only_needs_no_ci(self):
        run, result, _ = ship(START+[(['git', 'diff', '--name-only', BASE, HEAD], 'docs/a.md\ndocs/track/b.md\n')]
                              + pins('')+PUSH+FAST)
        self.assertEqual(run.script, [])
        self.assertEqual(result, dict(fast=21))


WRITES = (['git', 'push'], ['gh', 'variable', 'set'], ['gh', 'workflow', 'run'])


class Plan(unittest.TestCase):
    """plan answers from the same decision as ship and never writes (ticket 40)."""
    def plan(self, script, **options):
        run = Fake(script)
        lines = []
        options.setdefault('validate', lambda run: [])
        release.plan(run, out=lines.append, **options)
        self.assertEqual(run.script, [])
        self.assertFalse(any(call[:len(w)] == w for call in run.calls for w in WRITES))
        return '\n'.join(lines)

    def test_tested_change_to_collection_inputs_would_push_and_repin(self):
        text = self.plan(START+GREEN_CI+pins('programs/x86_64/a\nmodules/b.am\n'), ci='x')
        self.assertIn('Long tests 11 green on ci/x', text)
        self.assertIn('would push '+HEAD, text)
        self.assertIn('would repin', text)
        self.assertIn('programs/x86_64/a', text)
        self.assertIn('modules/b.am', text)

    def test_a_long_list_of_changed_inputs_is_cut_to_a_count(self):
        paths = ['programs/x86_64/a%02d' % i for i in range(25)]
        text = self.plan(START+GREEN_CI+pins('\n'.join(paths)+'\n'), ci='x')
        self.assertIn('25 collection inputs changed', text)
        self.assertIn(paths[release.SHOWN-1], text)
        self.assertNotIn(paths[release.SHOWN], text)
        self.assertIn('and 5 more', text)

    def test_documentation_only_would_keep_the_pin(self):
        text = self.plan(START+[(['git', 'diff', '--name-only', BASE, HEAD], 'docs/a.md\n')]+pins(''))
        self.assertIn('would push '+HEAD, text)
        self.assertIn('stays '+PIN, text)
        self.assertNotIn('would repin', text)

    def test_a_schemas_scope_change_would_refuse_and_name_the_files(self):
        changed = 'schemas/catalog/summary.schema.json\n'
        text = self.plan(START+GREEN_CI+pins(changed, changed)[:4], ci='x')
        self.assertIn('would refuse:', text)
        self.assertIn('CATALOG_SCHEMA_REVISION', text)
        self.assertIn('schemas/catalog/summary.schema.json', text)

    def test_a_reviewed_schemas_change_would_repin_both(self):
        changed = 'schemas/catalog/summary.schema.json\n'
        text = self.plan(START+GREEN_CI+pins(changed, changed), ci='x', repin_schemas=True)
        self.assertIn('would repin CATALOG_SCHEMA_REVISION '+SCHEMA_PIN+' -> '+HEAD, text)
        self.assertIn('would repin CATALOG_SCHEDULE_REVISION', text)

    def test_a_reviewed_schemas_change_validates_live_refs_first(self):
        changed = 'schemas/catalog/summary.schema.json\n'
        seen = []
        text = self.plan(START+GREEN_CI+pins(changed, changed), ci='x', repin_schemas=True,
                         validate=lambda run: seen.append(run) or [])
        self.assertEqual(len(seen), 1)
        self.assertIn('live refs valid under HEAD', text)

    def test_live_refs_are_not_validated_without_a_schemas_change(self):
        self.plan(START+GREEN_CI+pins('programs/x86_64/a\n', ''), ci='x',
                  validate=lambda run: self.fail('validated live refs'))

    def test_a_drifted_browser_says_to_redeploy(self):
        text = self.plan(START+GREEN_CI+pins('programs/x86_64/a\n', '', deployed=(0, 'old'), ours='new'), ci='x')
        self.assertIn('deployed browser definitions differ from HEAD', text)
        self.assertIn('catalog-pages.yml', text)

    def test_a_matching_browser_says_so(self):
        text = self.plan(START+GREEN_CI+pins('programs/x86_64/a\n', ''), ci='x')
        self.assertIn('deployed browser definitions match HEAD', text)

    def test_an_unreachable_browser_is_reported_not_fatal(self):
        text = self.plan(START+GREEN_CI+pins('programs/x86_64/a\n', '', deployed=(22, ''))[:-1], ci='x')
        self.assertIn('would push', text)
        self.assertIn('deployed browser definitions unreadable (curl exit 22)', text)

    def test_an_unchanged_schemas_scope_says_its_pin_stays(self):
        text = self.plan(START+GREEN_CI+pins('programs/x86_64/a\n', ''), ci='x')
        self.assertIn('CATALOG_SCHEMA_REVISION stays '+SCHEMA_PIN, text)

    def test_a_refusal_is_printed_not_raised(self):
        text = self.plan(START+[(['git', 'diff', '--name-only', BASE, HEAD], 'modules/appimage.am\n')])
        self.assertIn('would refuse: changes outside docs/', text)
        self.assertNotIn('would push', text)


def view(run_id, status, conclusion=''):
    return (['gh', 'run', 'view', str(run_id), '--json', 'status,conclusion', *R],
            ok(dict(status=status, conclusion=conclusion)))


class ReadTree(unittest.TestCase):
    def test_every_blob_comes_back_byte_exact(self):
        import subprocess
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as repo:
            files = {'a.yaml': b'one\ntwo\n', 'runs/1-1/summary.yaml': b'', 'b c.bin': bytes(range(256))*3,
                     'nl.yaml': b'\n\n'}
            for path, data in files.items():
                (Path(repo)/path).parent.mkdir(parents=True, exist_ok=True)
                (Path(repo)/path).write_bytes(data)
            git = ['git', '-C', repo, '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'core.hooksPath=/dev/null']
            subprocess.run(['git', 'init', '-q', repo], check=True)
            subprocess.run(git+['add', '.'], check=True)
            subprocess.run(git+['commit', '-qm', 'x'], check=True)
            sha = subprocess.check_output(git+['rev-parse', 'HEAD'], text=True).strip()
            self.assertEqual(release.read_tree(sha, repo), files)


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


if __name__ == '__main__':
    unittest.main()
