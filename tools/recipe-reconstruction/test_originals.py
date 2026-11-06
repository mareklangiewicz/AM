"""Every discovered original drives the same reconstruction/refusal contract."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from originals import Catalogue, Originals, Template, functions, migration_summary

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]


class TemplateFamilies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metadata = json.loads((ROOT/'provenance.json').read_text())
        cls.originals = Originals(REPO)
        cls.catalogue = Catalogue(cls.originals, [cls.metadata['fixture_commit'], cls.metadata['upstream_commit']])

    def example(self, template):
        defaults = sorted(functions(template.generator, 'example/project'))
        return ['example-app' if marker == 'SAMPLE' else
                defaults[0] if marker == 'FUNCTION' else
                'example/project' if marker in ('REPLACETHIS', 'USER/REPO', 'DOMAIN/REPOSITORY') else 'example'
                for marker in template.slots]

    def test_every_original_template_is_discovered(self):
        expected = {(revision, path)
                    for revision in (self.metadata['fixture_commit'], self.metadata['upstream_commit'])
                    for path in self.originals.paths(revision, 'templates/')}
        self.assertEqual({(t.commit,t.path) for t in self.catalogue.templates}, expected)
        self.assertGreaterEqual(len(expected), 15)

    def test_all_families_round_trip_and_reject_added_steps(self):
        for template in self.catalogue.templates:
            with self.subTest(template=template.identity):
                values = self.example(template)
                recipe = template.render(values)
                result = template.match(recipe)
                self.assertIsNotNone(result)
                self.assertEqual(result['status'], 'instance')
                self.assertEqual(template.render(result['parameters']), recipe)
                self.assertIsNone(template.match(recipe+'\ntouch /tmp/custom\n'))
                self.assertIsNone(template.match(recipe.replace('\n', '\ntouch /tmp/custom\n', 1)))

    def test_function_parameters_cannot_hide_custom_logic(self):
        for template in self.catalogue.templates:
            if 'FUNCTION' not in template.slots:
                continue
            with self.subTest(template=template.identity):
                values = self.example(template)
                values[template.slots.index('FUNCTION')] += '; touch /tmp/custom'
                result = template.match(template.render(values))
                self.assertEqual(result['status'], 'parameter_review')
                self.assertTrue(result['parameter_review'])

    def test_nonliteral_data_is_not_blessed_as_standard(self):
        template = next(t for t in self.catalogue.templates if 'REPLACETHIS' in t.slots)
        values = self.example(template)
        values[template.slots.index('REPLACETHIS')] = '$(touch /tmp/custom)'
        result = template.match(template.render(values))
        self.assertEqual(result['status'], 'parameter_review')

    def test_real_app_instances_from_originals(self):
        for app in ('obsidian','actual','5ire','acreom','actiona','20x'):
            with self.subTest(app=app):
                recipe = self.originals.read(self.metadata['fixture_commit'], 'programs/x86_64/'+app)
                result = self.catalogue.check(recipe)
                self.assertIn(result['status'], ('instance','parameter_review'))
                for match in result['matches']:
                    self.assertEqual(self.catalogue.render(match['template'],match['parameters']),recipe)

    def test_unknown_content_and_changed_repeated_app_refuse(self):
        template = next(t for t in self.catalogue.templates if t.path.endswith('/AM-SAMPLE-AppImage'))
        source = template.render(self.example(template))
        self.assertEqual(self.catalogue.check('custom script\n')['status'], 'unmatched')
        self.assertIsNone(template.match(source.replace('APP=example-app', 'APP=other-app', 1)))

    def test_generator_derived_appimage_candidates(self):
        for app in ('20x', '2fac', '4nier-patrimonio'):
            with self.subTest(app=app):
                source = self.originals.read(self.metadata['fixture_commit'], 'programs/x86_64/'+app)
                result = self.catalogue.check(source)
                self.assertEqual(result['status'], 'instance')
                match = next(m for m in result['matches'] if m['status'] == 'instance')
                self.assertTrue(match['template'].endswith('/AM-SAMPLE-AppImage-in-archive'))
                self.assertEqual(self.catalogue.render(match['template'], match['parameters']), source)

    def test_archive_selector_changes_remain_review(self):
        source = self.originals.read(self.metadata['fixture_commit'], 'programs/x86_64/20x')
        mutations = [
            source.replace(' | head -1)', '; touch /tmp/custom)'),
            source.replace('/releases |', '/releases/latest |'),
            source.replace('grep -i "appimage$"', 'grep -i "appimage$\\|zip$"'),
            source.replace(' | grep -i "appimage$" | head -1', ' | head -1 | grep -i "appimage$"'),
            source.replace('peakflo/20x', '$(touch /tmp/custom)'),
            source.replace('grep -i "appimage$" | head -1', 'head -1', 1),
            source.replace('SITE="peakflo/20x"', 'SITE="example/project"', 1),
        ]
        for mutated in mutations:
            with self.subTest(source=mutated):
                self.assertNotEqual(mutated, source)
                self.assertEqual(self.catalogue.check(mutated)['status'], 'parameter_review')
        self.assertEqual(self.catalogue.check(source+'\ntouch /tmp/custom\n')['status'], 'unmatched')
        # Both commands fit approved forms individually, but cannot disagree.
        mismatch = self.catalogue.check(mutations[5])['matches'][0]
        self.assertIn('installer/updater parameters differ',
                      [item['reason'] for item in mismatch['parameter_review']])

    def test_archive_disagreement_is_explicit(self):
        source = self.originals.read(self.metadata['fixture_commit'], 'programs/x86_64/pyuploadtool')
        result = self.catalogue.check(source)
        self.assertEqual(result['status'], 'parameter_review')
        self.assertTrue(any(item['marker'] == 'FUNCTION'
                            and item['reason'] == 'installer/updater parameters differ'
                            for match in result['matches'] for item in match['parameter_review']))

    def test_selector_profile_requires_inspected_originals(self):
        source = self.originals.read(self.metadata['fixture_commit'], 'programs/x86_64/20x')
        template = next(t for t in self.catalogue.templates
                        if t.commit == self.metadata['fixture_commit']
                        and t.path.endswith('/AM-SAMPLE-AppImage-in-archive'))
        for body, generator, recipe in (
                (template.body, template.generator+'\n# changed\n', source),
                (template.body+'\n# changed\n', template.generator, source+'\n# changed\n')):
            with self.subTest(body=body[-20:], generator=generator[-20:]):
                changed = Template(template.commit, template.path, body, generator)
                self.assertEqual(changed.match(recipe)['status'], 'parameter_review')

    def test_inventory_is_read_only_and_bound_to_source(self):
        commit = self.metadata['fixture_commit']
        # Exact path scope exercises real Git streaming without a second corpus.
        rows = list(self.catalogue.inventory(commit, 'programs/x86_64/obsidian'))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['source_commit'], commit)
        self.assertEqual(rows[0]['recipe'], 'programs/x86_64/obsidian')
        self.assertEqual(rows[0]['status'], 'instance')

    def test_migration_summary_groups_review_work(self):
        row = next(self.catalogue.inventory(self.metadata['fixture_commit'], 'programs/x86_64/obsidian'))
        summary = migration_summary([row])
        self.assertEqual(summary['counts'], {'instance':1})
        self.assertFalse(summary['automatic_conversion'])
        self.assertEqual(row['migration_action'], 'review_runtime_policy')
        review = dict(row, status='parameter_review')
        self.assertEqual(migration_summary([row, review])['counts'], {'instance':1,'parameter_review':1})

    def test_expansion_rejects_malformed_parameter_containers(self):
        template = self.catalogue.templates[0]
        for value in (None, {}, 'x'*len(template.slots), [], ['multi\nline']*len(template.slots)):
            with self.subTest(value=value), self.assertRaises(ValueError):
                template.render(value)

    def test_missing_originals_fail_without_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'originals unavailable'):
                Catalogue(Originals(directory), [self.metadata['fixture_commit']])

    def test_cli_classify_expand_and_inventory(self):
        source = self.originals.read(self.metadata['fixture_commit'], 'programs/x86_64/obsidian')
        cli = [sys.executable, str(ROOT/'reconstruct.py')]
        with tempfile.TemporaryDirectory() as directory:
            recipe = Path(directory)/'recipe'; recipe.write_text(source)
            result = subprocess.run([*cli,'classify',str(recipe)],capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            match = json.loads(result.stdout)['matches'][0]
            declaration = Path(directory)/'declaration.json';declaration.write_text(json.dumps(match))
            expanded = subprocess.run([*cli,'expand',str(declaration)],capture_output=True)
            self.assertEqual(expanded.returncode,0,expanded.stderr)
            self.assertEqual(expanded.stdout,source.encode())
            inventory = subprocess.run([*cli,'inventory','--recipes-revision',self.metadata['fixture_commit'],
                                        '--prefix','programs/x86_64/obsidian'],capture_output=True)
            self.assertEqual(inventory.returncode,0,inventory.stderr)
            self.assertEqual(json.loads(inventory.stdout)['status'],'instance')
            summary = subprocess.run([*cli,'inventory','--recipes-revision',self.metadata['fixture_commit'],
                                      '--prefix','programs/x86_64/obsidian','--summary'],capture_output=True)
            self.assertEqual(summary.returncode,0,summary.stderr)
            self.assertEqual(json.loads(summary.stdout)['counts'], {'instance':1})
            recipe.write_text('arbitrary custom shell\n')
            result = subprocess.run([*cli,'classify',str(recipe)],capture_output=True)
            self.assertEqual(result.returncode,1)
            self.assertEqual(json.loads(result.stdout)['status'],'unmatched')


if __name__ == '__main__':
    unittest.main()
