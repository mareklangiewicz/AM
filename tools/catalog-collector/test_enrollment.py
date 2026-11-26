"""Enrollment is catalog/apps.yaml: each app's identity comes from the
repository file it points to (catalog-simplification ticket 28)."""
import tempfile
import unittest

import fixture_enrollment as fixture
from fixture_enrollment import NVIM, OBSIDIAN
import host_catalog

APPS = dict(fixture.RECIPE_APPS, example=('example', 42, 'owner/example'))
RECIPES = ['x86_64/nvim', 'x86_64/nvim-nightly', 'x86_64/obsidian']


class Enrollment(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = fixture.write(temporary.name, apps=APPS, recipes=RECIPES, retired=['thorium'])

    def edit(self, relative, old, new):
        path = self.root/relative
        text = path.read_text()
        self.assertEqual(text.count(old), 1, (relative, old))
        path.write_text(text.replace(old, new))

    def test_every_app_in_apps_yaml_is_enrolled_with_its_files_identity(self):
        rows, sources, names = host_catalog.enrollment(root=self.root)
        self.assertEqual({row['app']: (row['repository_id'], row['repository']) for row in rows},
                         {app: (rid, repository) for app, (_, rid, repository) in APPS.items()})
        self.assertEqual({row['app'] for row in rows if 'recipe' in row}, {'nvim', 'nvim-nightly', 'obsidian'})
        self.assertEqual(sources, {str(NVIM): 'neovim/neovim', str(OBSIDIAN): 'obsidianmd/obsidian-releases',
                                   '42': 'owner/example'})
        self.assertEqual(names, {str(NVIM): 'nvim', str(OBSIDIAN): 'obsidian', '42': 'example'})
        self.assertEqual(host_catalog.configuration(root=self.root), (rows, sources))
        installed, _ = host_catalog.installation_configuration(root=self.root)
        self.assertEqual([row['app'] for row in installed], ['nvim', 'nvim-nightly', 'obsidian'])

    def test_an_app_without_a_recipe_needs_only_its_entry_and_file(self):
        (self.root/'tools/catalog-collector/collection-recipes.txt').write_text('')
        rows, sources, _ = host_catalog.enrollment(root=self.root)
        self.assertEqual(len(rows), 4)
        self.assertFalse([row for row in rows if 'recipe' in row])
        self.assertEqual(len(sources), 3)

    def test_inconsistent_enrollment_refuses(self):
        apps, recipes = 'catalog/apps.yaml', 'tools/catalog-collector/collection-recipes.txt'
        cases = {
            'retired source name': [(apps, '"repositories/example.yaml"', '"repositories/thorium.yaml"')],
            'missing repository file': [(apps, '"repositories/example.yaml"', '"repositories/elsewhere.yaml"')],
            'repository pointer': [(apps, '"repositories/example.yaml"', '"example.yaml"')],
            # Two files for one repository: obsidian's identity copied under example's name.
            'conflicting repository identity': [('catalog/repositories/example.yaml', 'repository_id: 42\nrepository: "owner/example"',
                                                 f'repository_id: {OBSIDIAN}\nrepository: "obsidianmd/obsidian-releases"')],
            # The recipe says neovim/neovim; the file it is enrolled through says otherwise.
            'recipe identity': [('catalog/repositories/nvim.yaml', '"neovim/neovim"', '"neovim/other"')],
            'unknown collection app': [(apps, '  "obsidian":\n    repository: "repositories/obsidian.yaml"\n', '')],
            'unknown collection recipe': [(recipes, 'x86_64/obsidian\n', 'x86_64/obsidian\nx86_64/missing\n')],
            'duplicate collection recipe': [(recipes, 'x86_64/obsidian\n', 'x86_64/obsidian\nx86_64/obsidian\n')],
            'retired names': [('tools/catalog-collector/retired-names.yaml', '"thorium": true', '"thorium": false')],
        }
        for reason, edits in cases.items():
            with self.subTest(reason=reason):
                saved = {relative: (self.root/relative).read_text() for relative, _, _ in edits}
                for edit in edits:
                    self.edit(*edit)
                with self.assertRaisesRegex(ValueError, reason):
                    host_catalog.enrollment(root=self.root)
                for relative, text in saved.items():
                    (self.root/relative).write_text(text)

    def test_no_apps_refuses_rather_than_emptying_catalog(self):
        # Every repository file would be unpointed, and the run would delete them all.
        (self.root/'tools/catalog-collector/collection-recipes.txt').write_text('')
        (self.root/'catalog/apps.yaml').write_text('$schema: "../schemas/catalog.schema.yaml#/$defs/apps"\napps: {}\n')
        with self.assertRaisesRegex(ValueError, 'empty enrollment'):
            host_catalog.enrollment(root=self.root)

    def test_more_sources_than_the_cap_refuse(self):
        with self.assertRaisesRegex(ValueError, 'manifest scope'):
            host_catalog.enrollment(root=self.root, source_cap=2)


if __name__ == '__main__':
    unittest.main()
