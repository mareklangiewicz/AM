"""Pinned reconstruction and refusal contracts; no incoming shell is executed."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import reconstruct as tool

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]


class Reconstruction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template, cls.metadata = tool.load_template(tool.TEMPLATE)
        cls.source = (ROOT/'fixtures/obsidian').read_bytes().decode()

    def test_real_fixture_hashes_and_complete_round_trips(self):
        for fixture in self.metadata['fixtures']:
            with self.subTest(path=fixture['path']):
                data = (ROOT/'fixtures'/Path(fixture['path']).name).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), fixture['sha256'])
                result = tool.check(self.template, data.decode(), tool.TEMPLATE)
                self.assertEqual(result['status'], 'exact')
                self.assertEqual(result['compatibility'], 'unassessed')
                self.assertEqual(tool.render(self.template, result['declaration']).encode(), data)

    def test_parameter_changes(self):
        modified = self.source.replace('APP=obsidian\n', 'APP=example-app\n').replace(
            'obsidianmd/obsidian-releases', 'example-owner/example-releases')
        result = tool.check(self.template, modified, tool.TEMPLATE)
        self.assertEqual(result['status'], 'exact')
        self.assertEqual(result['declaration']['app'], 'example-app')
        self.assertEqual(result['declaration']['repository'], 'example-owner/example-releases')

    def test_repository_names_are_not_reinterpreted_as_template_slots(self):
        value = dict(template=tool.TEMPLATE, app='example', repository='SAMPLE/FUNCTION')
        rendered = tool.render(self.template, value)
        self.assertIn('SITE="SAMPLE/FUNCTION"', rendered)
        self.assertIn('https://api.github.com/repos/SAMPLE/FUNCTION/releases', rendered)
        self.assertEqual(tool.check(self.template, rendered, tool.TEMPLATE)['status'], 'exact')

    def test_all_content_accounted_for(self):
        edits = [
            self.source.replace('# LINK TO PATH', 'touch /tmp/unexpected\n# LINK TO PATH'),
            self.source.replace('version0=$(cat', 'touch /tmp/unexpected\nversion0=$(cat'),
            self.source.replace('VERSION 3.5', 'VERSION 3.6'),
            self.source.replace('APP=obsidian', 'APP=different', 1),
            self.source+'# New comment\n',
            self.source.replace('\n', '\r\n'),
            self.source[:-1],
        ]
        for modified in edits:
            with self.subTest(modified=modified[:80]):
                try:
                    result = tool.check(self.template, modified, tool.TEMPLATE)
                except tool.Unsupported:
                    continue
                self.assertEqual(result['status'], 'review')
                self.assertTrue(result['diff'])
                self.assertNotIn('declaration', result)
                self.assertEqual(result['compatibility'], 'unassessed')
        result = tool.check(self.template, self.source[:-1], tool.TEMPLATE)
        self.assertIn('No newline at end of file', result['diff'])

    def test_updater_parameter_drift(self):
        start, updater = self.source.split("cat >> ./AM-updater << 'EOF'\n")
        for old, new in [('APP=obsidian', 'APP=other'), ('obsidianmd/obsidian-releases', 'other/repo')]:
            with self.subTest(field=old):
                result = tool.check(self.template, start+"cat >> ./AM-updater << 'EOF'\n"+updater.replace(old, new), tool.TEMPLATE)
                self.assertEqual(result['status'], 'review')
                self.assertIn(new, result['diff'])

    def test_nonliteral_input(self):
        for assignment in ['APP=$(touch /tmp/unexpected)', 'APP="obsidian"', 'APP=obsidian;whoami']:
            modified = self.source.replace('APP=obsidian', assignment)
            with self.subTest(assignment=assignment), self.assertRaises(tool.Unsupported):
                tool.check(self.template, modified, tool.TEMPLATE)

    def test_render_rejects_unknown_identity_and_parameters(self):
        base = dict(template=tool.TEMPLATE, app='obsidian', repository='obsidianmd/obsidian-releases')
        for key, value in [('template','unknown'), ('app','$(whoami)'), ('repository','other/repo;exit'),
                           ('app',None), ('updater','custom command')]:
            with self.subTest(key=key), self.assertRaises(tool.Unsupported):
                tool.render(self.template, dict(base, **{key:value}))
        for value in [[], 'text', {}, dict(base, app='app\n')]:
            with self.subTest(value=value), self.assertRaises(tool.Unsupported):
                tool.render(self.template, value)

    def test_short_recipe_maps_current_literals(self):
        short = (REPO/'programs/x86_64/obsidian').read_text()
        value = tool.from_short(short, tool.TEMPLATE)
        self.assertEqual(tool.render(self.template, value), self.source)

    def test_short_recipe_refuses_code_and_other_layouts(self):
        short = (REPO/'programs/x86_64/obsidian').read_text()
        edits = [short.replace('APP=obsidian', 'APP=$(whoami)'),
                 short.replace('APP=obsidian', 'APP=obsidian\nAPP=obsidian'),
                 short.replace('APP=obsidian', 'APP=obsidian\nPATH=/tmp'),
                 short+'touch /tmp/unexpected\n',
                 short.replace('APP=obsidian', 'APP=obsidian\nPACKAGE_KIND=executable'),
                 short.replace('APP=obsidian', 'APP=obsidian\nPACKAGE_LAYOUT=tar'),
                 short.replace('CATALOG_RECIPE="x86_64/obsidian"', 'CATALOG_RECIPE="aarch64/obsidian"'),
                 short.replace('CATALOG_RECIPE="x86_64/obsidian"', 'CATALOG_RECIPE="x86_64/other"'),
                 short.replace('EXTRA_APP_LAUNCHERS=obsidian-gui', 'EXTRA_APP_LAUNCHERS="$(whoami)"')]
        for modified in edits:
            with self.subTest(modified=modified[:100]), self.assertRaises(tool.Unsupported):
                tool.from_short(modified, tool.TEMPLATE)

    def test_template_integrity(self):
        real = tool.read_text
        def changed(path):
            result = real(path)
            return result+'# drift\n' if Path(path).name == 'AM-SAMPLE-AppImage' else result
        with patch.object(tool, 'read_text', side_effect=changed), self.assertRaises(ValueError):
            tool.load_template(tool.TEMPLATE)

    def test_upstream_verification_checks_source_bytes(self):
        # Normal tests work in source archives/shallow clones as well. The real
        # pinned-object CLI verification is a separate documented operation.
        metadata = dict(self.metadata)
        excerpt = (ROOT/'upstream/github-appimage-function.txt').read_bytes()
        metadata['generator_line'] = 1
        metadata['generator_sha256'] = hashlib.sha256(excerpt).hexdigest()
        objects = {metadata['upstream_commit']+':'+metadata['template_source']:
                   (ROOT/'upstream/AM-SAMPLE-AppImage').read_bytes(),
                   metadata['upstream_commit']+':'+metadata['generator_source']: excerpt}
        objects.update({metadata['fixture_commit']+':'+row['path']:
                        (ROOT/'fixtures'/Path(row['path']).name).read_bytes()
                        for row in metadata['fixtures']})
        with patch.object(tool.subprocess, 'check_output', side_effect=lambda args, **kw: objects[args[-1]]):
            result = tool.verify_upstream(REPO, metadata)
            self.assertEqual(result['status'], 'exact')
            self.assertEqual(result['fixtures_verified'], 5)
            objects[metadata['upstream_commit']+':'+metadata['template_source']] += b'# drift\n'
            with self.assertRaises(ValueError):
                tool.verify_upstream(REPO, metadata)

    def test_generator_integrity(self):
        real = tool.read_text
        def changed(path):
            result = real(path)
            return result+'# drift\n' if Path(path).name == 'github-appimage-function.txt' else result
        with patch.object(tool, 'read_text', side_effect=changed), self.assertRaises(ValueError):
            tool.load_template(tool.TEMPLATE)

    def test_cli_json_declaration_round_trip_and_errors(self):
        value = dict(template=tool.TEMPLATE, app='obsidian', repository='obsidianmd/obsidian-releases')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'declaration.json'
            command = [sys.executable, str(ROOT/'reconstruct.py'), 'render',
                       '--template', tool.TEMPLATE, '--declaration', str(path)]
            path.write_text(json.dumps(value))
            result = subprocess.run(command, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, self.source.encode())
            for body, expected in [('{', 3), (json.dumps(dict(value, updater='custom')), 2), ('[]', 2)]:
                path.write_text(body)
                result = subprocess.run(command, capture_output=True)
                self.assertEqual(result.returncode, expected)
                self.assertEqual(result.stdout, b'')
                self.assertIn(json.loads(result.stderr)['status'], ('error', 'unsupported'))

    def test_cli_status_codes_and_output_channels(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'recipe'
            def run(body, *args):
                path.write_bytes(body)
                return subprocess.run([sys.executable, str(ROOT/'reconstruct.py'), 'check', str(path), *args], capture_output=True)
            for body, code, status in [(self.source.encode(),0,'exact'),
                                       ((self.source+'# drift\n').encode(),1,'review'),
                                       (b'APP=$(whoami)\n',2,'unsupported'),
                                       (b'\xff',2,'unsupported'), (b'\0',2,'unsupported'),
                                       (b'x'*(tool.LIMIT+1),2,'unsupported')]:
                result = run(body)
                self.assertEqual(result.returncode,code,result.stderr)
                self.assertEqual(json.loads(result.stdout)['status'],status)
                self.assertEqual(result.stderr,b'')
            result = run(self.source.encode(),'--template','unknown')
            self.assertEqual(result.returncode,2)
            self.assertEqual(json.loads(result.stdout)['status'],'unsupported')
            result = subprocess.run([sys.executable,str(ROOT/'reconstruct.py'),'check',str(path/'missing')],capture_output=True)
            self.assertEqual(result.returncode,3)
            self.assertEqual(json.loads(result.stdout)['status'],'error')
            rendered = subprocess.run([sys.executable,str(ROOT/'reconstruct.py'),'render','--template',tool.TEMPLATE,
                                       '--short-recipe',str(REPO/'programs/x86_64/obsidian')],capture_output=True)
            self.assertEqual(rendered.returncode,0,rendered.stderr)
            self.assertEqual(rendered.stdout,self.source.encode())
            self.assertEqual(rendered.stderr,b'')
            bad = subprocess.run([sys.executable,str(ROOT/'reconstruct.py'),'render','--template','unknown',
                                  '--short-recipe',str(path)],capture_output=True)
            self.assertEqual(bad.returncode,2)
            self.assertEqual(bad.stdout,b'')
            self.assertEqual(json.loads(bad.stderr)['status'],'unsupported')


if __name__ == '__main__':
    unittest.main()
