"""Generic declarations select without implicitly widening collection."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import host_catalog
import recipe_policy_source as compiler
from recipe_declarations import recipe_rows


class Declarations(unittest.TestCase):
    def test_unenrolled_architectures_select_through_common_registry(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'modules').mkdir()
            shutil.copy2(compiler.ROOT/'modules/catalog-yaml-policy.am', root/'modules')
            enrollment = root/'tools/catalog-collector'
            enrollment.mkdir(parents=True)
            shutil.copy2(compiler.ROOT/'tools/catalog-collector/collection-recipes.txt', enrollment)
            for row in recipe_rows(compiler.ROOT):
                path = root/'programs'/row['recipe']
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(compiler.ROOT/'programs'/row['recipe'], path)
            source = (compiler.ROOT/'programs/x86_64/nvim').read_text()
            for arch in ('x86_64', 'aarch64', 'i686', 'armv7l'):
                path = root/'programs'/arch/'example'
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(source.replace('APP=nvim', 'APP=example')
                    .replace('x86_64/nvim', arch+'/example')
                    .replace('^nvim-linux-x86_64[.]appimage$', '^example-.*[.]AppImage$'))
            with patch.object(compiler, 'ROOT', root), patch.object(host_catalog, 'ROOT', root):
                compiler.generate()
                rows, sources = host_catalog.configuration()
                self.assertEqual((len(rows), len(sources)), (21, 19))
                policy = root/'modules/catalog-yaml-policy.am'
                before, rest = policy.read_text().split(compiler.START)
                generated, after = rest.split(compiler.END)
                self.assertNotIn('function ', generated)
                for arch, token in (('x86_64','x86_64'), ('aarch64','arm64'),
                                    ('i686','i686'), ('armv7l','armv7l')):
                    facts = ''
                    for i, name in enumerate(('example-windows-'+token+'.AppImage',
                                               'example-'+token+'.AppImage',
                                               'example-'+('arm64' if arch=='x86_64' else 'amd64')+'.AppImage')):
                        facts += '\t'.join(['1', str(i+1), *map(json.dumps, [
                            '2026-11-05T12:00:00Z', '2026-11-05T11:00:00Z', 'v1', name,
                            'https://github.com/neovim/neovim/releases/download/v1/'+name]), 'false'])+'\n'
                    for command in (['awk'], ['mawk'], ['gawk'], ['busybox','awk']):
                        result = subprocess.run([*command, '-f', str(policy)], input=facts,
                            text=True, capture_output=True, env={**os.environ, 'LC_ALL':'C',
                                'AM_YAML_RECIPE':arch+'/example', 'AM_YAML_REPOSITORY':'16408992',
                                'AM_YAML_NOW':'2026-11-05T12:00:00Z', 'AM_YAML_PIN':'a'*40})
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(result.stdout.splitlines()[3], '2')
                # Maintained code is unchanged when declaration data changes.
                path = root/'programs/aarch64/example'
                path.write_text(path.read_text().replace('CATALOG_CHANNEL=stable','CATALOG_CHANNEL=any'))
                compiler.generate()
                new_before, rest = policy.read_text().split(compiler.START)
                _, new_after = rest.split(compiler.END)
                self.assertEqual((before, after), (new_before, new_after))
                path.write_text(path.read_text().replace('CATALOG_REPOSITORY_ID=16408992',
                                                        'CATALOG_REPOSITORY_ID=1'))
                with self.assertRaisesRegex(ValueError, 'conflicting app identity'):
                    recipe_rows(root)
                path.write_text(path.read_text().replace('CATALOG_REPOSITORY_ID=1\n',
                                                        'CATALOG_REPOSITORY_ID=16408992\n'))
                for bad in ('x86_64/missing\n', 'x86_64/nvim\nx86_64/nvim\n'):
                    (enrollment/'collection-recipes.txt').write_text(bad)
                    with self.assertRaises(ValueError):host_catalog.configuration()


if __name__ == '__main__':
    unittest.main()
