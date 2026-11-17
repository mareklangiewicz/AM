"""Scheduled collection runs only while its inputs equal the reviewed pin (ticket 22)."""
import subprocess
import tempfile
import unittest
from pathlib import Path

import collection_interface as interface


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


class ScheduleGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(self.repo, 'init', '-q')
        git(self.repo, 'config', 'user.email', 'gate@example.invalid')
        git(self.repo, 'config', 'user.name', 'gate')
        for path in ('docs/notes.md', 'programs/x86_64/example', '.github/workflows/catalog.yml',
                     '.github/actions/catalog-collect/action.yml', 'modules/catalog-contract-tables.am'):
            self.write(path, 'reviewed\n')
        self.pin = self.commit()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, path, text):
        file = self.repo/path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text)

    def commit(self):
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-q', '--allow-empty', '-m', 'change')
        return git(self.repo, 'rev-parse', 'HEAD')

    def test_same_commit_passes(self):
        self.assertEqual(interface.schedule_gate(self.repo, self.pin, self.pin), [])

    def test_documentation_push_passes(self):
        self.write('docs/notes.md', 'edited\n')
        self.assertEqual(interface.schedule_gate(self.repo, self.pin, self.commit()), [])

    def test_readme_under_an_input_passes(self):
        self.write('tools/catalog-collector/README.md', 'edited\n')
        self.write('tools/recipe-reconstruction/README.md', 'edited\n')
        self.assertEqual(interface.schedule_gate(self.repo, self.pin, self.commit()), [])

    def test_each_collection_input_change_is_named(self):
        for path in ('programs/x86_64/example', '.github/workflows/catalog.yml',
                     '.github/actions/catalog-collect/action.yml', 'modules/catalog-contract-tables.am',
                     'tools/catalog-collector/new.py', 'docs/catalog-format-v3.md',
                     'tools/catalog-collector/notes.md'):
            with self.subTest(path=path):
                self.write(path, 'unreviewed '+path+'\n')
                self.assertEqual(interface.schedule_gate(self.repo, self.pin, self.commit()), [path])
                git(self.repo, 'reset', '-q', '--hard', self.pin)

    def test_gate_covers_every_input_scope(self):
        paths = interface.schedule_gate_paths()
        for scope in interface.INPUT_SCOPES.values():
            self.assertLessEqual(set(scope), set(paths))

    def test_cli_fails_naming_the_change_and_the_pin(self):
        self.write('programs/x86_64/example', 'unreviewed\n')
        head = self.commit()
        with self.assertRaises(SystemExit) as raised:
            interface.main(['schedule-gate', '--repo', str(self.repo), '--pin', self.pin, '--head', head])
        self.assertIn('programs/x86_64/example', str(raised.exception.code))
        self.assertIn(self.pin, str(raised.exception.code))
        interface.main(['schedule-gate', '--repo', str(self.repo), '--pin', self.pin, '--head', self.pin])

    def test_pin_must_be_an_exact_revision(self):
        with self.assertRaises(SystemExit):
            interface.main(['schedule-gate', '--repo', str(self.repo), '--pin', '', '--head', self.pin])


if __name__ == '__main__':
    unittest.main()
