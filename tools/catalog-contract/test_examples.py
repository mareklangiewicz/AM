"""Worked examples of the catalog contract, read by every validator.

Each examples/*.yaml is a whole document. One named bad-*.yaml must be refused
by every validator; any other must be accepted by all of them. The validators
are the host's awk reader (under each awk AM supports), the page's JS reader,
and the hand-written schema itself, through jsonschema.
"""
from pathlib import Path
import json
import os
import shutil
import subprocess
import unittest

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = Path(__file__).resolve().parent/'examples'
SCHEMA = yaml.safe_load((ROOT/'schemas/catalog.schema.yaml').read_text())
AWKS = (['mawk'], ['gawk'], ['busybox', 'awk'])


def examples():
    return sorted(EXAMPLES.glob('*.yaml'))


def awk(command, raw):
    """The host reader's validate operation, under one awk."""
    return subprocess.run(
        [*command, '-f', str(ROOT/'modules/catalog-tables.am'), '-f', str(ROOT/'modules/catalog-parser.am')],
        input=raw, capture_output=True, env=dict(os.environ, LC_ALL='C', AM_YAML_OPERATION='validate'))


def node(raw):
    """The page's reader."""
    js = ("import {parseDocument} from './tools/catalog-contract/parse.mjs';"
          "let s='';for await(const b of process.stdin)s+=b;"
          "try{parseDocument(s)}catch(e){console.error(e.message);process.exitCode=2}")
    return subprocess.run(['node', '--input-type=module', '-e', js], input=raw, capture_output=True, cwd=ROOT)


def schema_accepts(raw):
    """The schema, applied to the document the fragment of its first key names.

    None when the bytes are not YAML at all, so no schema applies.
    """
    try:
        document = yaml.safe_load(raw)
    except yaml.YAMLError:
        return None
    reference = document.get('$schema', '') if isinstance(document, dict) else ''
    kind = reference.partition('#/$defs/')[2]
    if kind not in SCHEMA['$defs']:
        return False
    schema = dict(SCHEMA, **{'$ref': '#/$defs/'+kind})
    checker = jsonschema.Draft202012Validator.FORMAT_CHECKER
    return jsonschema.Draft202012Validator(schema, format_checker=checker).is_valid(document)


BAD = json.loads((EXAMPLES/'bad.json').read_text())


class Examples(unittest.TestCase):
    def test_every_bad_example_names_its_refusal(self):
        bad = {path.name for path in examples() if path.name.startswith('bad-')}
        self.assertEqual(bad, set(BAD))
        self.assertTrue(any(not path.name.startswith('bad-') for path in examples()))

    def test_shell_reader_under_every_awk(self):
        for command in AWKS:
            self.assertIsNotNone(shutil.which(command[0]), command)
            for path in examples():
                with self.subTest(awk=command[0], example=path.name):
                    run = awk(command, path.read_bytes())
                    self.assertEqual(run.returncode, 2 if path.name in BAD else 0, run.stderr)
                    self.assertEqual(run.stdout, b'')
                    if path.name in BAD:
                        self.assertIn(BAD[path.name]['refusal'].encode(), run.stderr)

    def test_page_reader(self):
        for path in examples():
            with self.subTest(example=path.name):
                run = node(path.read_bytes())
                self.assertEqual(run.returncode, 2 if path.name in BAD else 0, run.stderr)
                if path.name in BAD:
                    self.assertIn(BAD[path.name]['refusal'].encode(), run.stderr)

    def test_schema(self):
        # The schema refuses what it can see and accepts the rest: grammar and
        # cross-field rules are the readers' alone (docs/catalog-format.md).
        for path in examples():
            with self.subTest(example=path.name):
                sees = path.name in BAD and BAD[path.name]['schema_sees']
                accepted = schema_accepts(path.read_bytes())
                if accepted is None:
                    self.assertFalse(sees, 'not YAML, yet marked as a schema refusal')
                else:
                    self.assertEqual(accepted, not sees)


class Generated(unittest.TestCase):
    def test_reader_tables_match_the_schema(self):
        import build
        defs = build.load()
        self.assertEqual(build.TABLES.read_text(), build.tables(defs), 'run tools/catalog-contract/build.py')
        self.assertEqual(build.MODULE.read_text(), build.module(defs), 'run tools/catalog-contract/build.py')


if __name__ == '__main__':
    unittest.main()
