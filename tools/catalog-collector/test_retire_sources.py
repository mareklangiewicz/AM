"""The explicit step that takes a catalog source out of collection (ticket 21)."""
import json
from pathlib import Path
import tempfile
import unittest

import pinned_recipes
import retire_sources as r
from recipe_declarations import rows_json

HERE = Path(__file__).parent
DECLARED = '1186679146'


class Retire(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.folder = self.root/'tools/catalog-collector'
        self.folder.mkdir(parents=True)
        self.write('collection-apps.json', rows_json([
            dict(app='keep', repository_id=1, repository='o/keep'),
            dict(app='gone', repository_id=2, repository='o/gone'),
            dict(app='gone-cli', repository_id=2, repository='o/gone'),
            dict(app='gone.src-3', repository_id=3, repository='o/alt'),
            dict(app='old-name', repository_id=4, repository='o/plain')]))
        self.write('source-names.json', json.dumps(dict(active={'1': 'keep', '2': 'gone', '3': 'alt', '4': 'plain',
                                                                DECLARED: '0xfx'},
                                                        retired=['older']), indent=2)+'\n')
        self.write('recipe-url-policies.json', rows_json([dict(recipe='x86_64/keep', repository_id=1)]))
        self.write('appimage-policies.json', rows_json([dict(recipe='x86_64/alt', repository_id=3)]))
        # One real declaration: 0xfx selects from source 1186679146.
        pinned_recipes.write('x86_64/0xfx', self.root)
        # A plain recipe upstream renamed still downloads from o/plain.
        (self.root/'programs/aarch64').mkdir(parents=True)
        (self.root/'programs/aarch64/new-name').write_text(
            'version=$(curl -Ls https://api.github.com/repos/O/Plain/releases | grep -o x)\n', encoding='utf-8')

    def write(self, name, text):
        (self.folder/name).write_text(text, encoding='utf-8')

    def read(self, name):
        return (self.folder/name).read_text(encoding='utf-8')

    def test_rows_leave_enrollment_and_the_name_moves_to_retired(self):
        files = r.retire(self.root, [2])
        self.assertEqual(sorted(files), [r.APPS, r.NAMES])
        self.assertEqual([row['app'] for row in json.loads(files[r.APPS])], ['keep', 'gone.src-3', 'old-name'])
        self.assertEqual(json.loads(files[r.NAMES]), dict(active={'1': 'keep', '3': 'alt', '4': 'plain', DECLARED: '0xfx'},
                                                          retired=['older', 'gone']))
        self.assertEqual(files[r.APPS], rows_json(json.loads(files[r.APPS])))

    def test_nothing_is_written_without_write(self):
        before = self.read('collection-apps.json'), self.read('source-names.json')
        self.assertEqual(r.main(['--root', str(self.root), '2']), 0)
        self.assertEqual((self.read('collection-apps.json'), self.read('source-names.json')), before)
        self.assertEqual(r.main(['--root', str(self.root), '--write', '2']), 0)
        self.assertNotIn('"2"', self.read('source-names.json'))

    def test_a_source_a_recipe_still_selects_from_refuses(self):
        for rid, by in ((1, 'x86_64/keep'), (3, 'x86_64/alt')):
            with self.subTest(rid=rid), self.assertRaisesRegex(r.Refused, 'still selected by '+by):
                r.retire(self.root, [rid])
        with self.assertRaisesRegex(r.Refused, 'still selected by x86_64/0xfx'):
            r.retire(self.root, [int(DECLARED)])

    def test_a_source_only_a_recipe_url_names_retires_with_a_warning(self):
        # Upstream renamed the app; its plain recipe still downloads from o/plain.
        self.assertEqual([row['app'] for row in json.loads(r.retire(self.root, [2, 4])[r.APPS])], ['keep', 'gone.src-3'])
        self.assertEqual(r.still_named(self.root, [2, 4]), ['source 4 o/plain is still named by programs/aarch64/new-name'])
        self.assertEqual(r.still_named(self.root, [2]), [])

    def test_an_unknown_or_repeated_source_refuses(self):
        with self.assertRaisesRegex(r.Refused, 'not an active source: 9'):
            r.retire(self.root, [2, 9])
        with self.assertRaisesRegex(r.Refused, 'named twice: 2'):
            r.retire(self.root, [2, 2])

    def test_the_committed_files_keep_their_bytes_through_a_rewrite(self):
        names = (HERE/'source-names.json').read_text(encoding='utf-8')
        apps = (HERE/'collection-apps.json').read_text(encoding='utf-8')
        self.assertEqual(r.names_json(json.loads(names)), names)
        self.assertEqual(rows_json(json.loads(apps)), apps)


if __name__ == '__main__':
    unittest.main()
