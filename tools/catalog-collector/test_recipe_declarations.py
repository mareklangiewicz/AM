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
    def test_enrolled_candidate_declarations_select_saved_assets(self):
        import hashlib
        import tarfile
        research = compiler.ROOT/'docs/track/release-catalog/research'
        receipt = json.loads((research/'two-candidate-upstream-evidence.json').read_text())
        archive = research/receipt['evidence_archive']
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), receipt['evidence_archive_sha256'])
        rows = {r['app']:r for r in recipe_rows(compiler.ROOT)}
        enrolled, _ = host_catalog.installation_configuration()
        self.assertIn('20x', [r['app'] for r in enrolled])
        self.assertIn('2fac', [r['app'] for r in enrolled])
        with tarfile.open(archive) as evidence:
            for app in ('20x', '2fac'):
                row = rows[app]
                source = next(r for r in receipt['receipts'] if r['app']==app and r['kind']=='releases')
                raw = evidence.extractfile(app+'-releases.json').read()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), source['sha256'])
                expected = next(r['narrow_declaration_url'] for r in receipt['selection_comparison'] if r['app']==app)
                facts = ''
                now = source['observed_at'][:19]+'Z'
                for release in json.loads(raw):
                    for asset in release['assets']:
                        facts += '\t'.join([str(release['id']),str(asset['id']),*map(json.dumps,[
                            now,release['published_at'],release['tag_name'],asset['name'],
                            asset['browser_download_url']]),json.dumps(release['prerelease'])])+'\n'
                for command in (['mawk'], ['gawk'], ['busybox','awk']):
                    with self.subTest(app=app, command=command):
                        result = subprocess.run([*command,'-f',str(compiler.ROOT/'modules/catalog-yaml-policy.am')],
                            input=facts,text=True,capture_output=True,timeout=10,
                            env={**os.environ,'LC_ALL':'C','AM_YAML_RECIPE':row['recipe'],
                                 'AM_YAML_REPOSITORY':str(row['repository_id']),
                                 'AM_YAML_NOW':now,'AM_YAML_PIN':'a'*40})
                        self.assertEqual(result.returncode,0,result.stderr)
                        self.assertEqual(result.stdout.splitlines()[-1],expected)
        # Declaration compilation validates the opt-in boolean before registry generation.
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root/'programs/x86_64/20x';path.parent.mkdir(parents=True)
            path.write_text((compiler.ROOT/'programs/x86_64/20x').read_text().replace(
                'DESKTOP_STRIP_NO_SANDBOX=true','DESKTOP_STRIP_NO_SANDBOX=unknown'))
            with self.assertRaisesRegex(ValueError,'invalid recipe boolean'):
                recipe_rows(root)

    def test_architecture_labels_and_armhf_refusals(self):
        # Independent expectations for asset names, including conflicting labels.
        # armhf is not enough to establish ARMv7; unlabelled x86_64 remains allowed.
        cases = {
            'unlabelled': {'x86_64'},
            'x86_64': {'x86_64'}, 'amd64': {'x86_64'}, 'x64': {'x86_64'},
            'i386': {'i686'}, 'i686': {'i686'},
            'arm64': {'aarch64'}, 'aarch64': {'aarch64'},
            'armv7': {'armv7l'}, 'armv7l': {'armv7l'},
            'armhf': set(), 'ARMHF': set(),
            'x86_64-armhf': set(), 'amd64-armhf': set(),
            'aarch64-armhf': set(), 'arm64-ARMHF': set(),
            'i386-armhf': set(), 'i686-armhf': set(),
            'armv7-armhf': {'armv7l'}, 'ARMV7L-ARMHF': {'armv7l'},
            'aarch64-x86_64': set(), 'i686-armv7': set(),
            'windows-x86_64': set(), 'macos-arm64': set(),
        }
        architectures = ('x86_64', 'aarch64', 'i686', 'armv7l')
        with tempfile.TemporaryDirectory(prefix='armhf-declarations-') as temporary:
            root = Path(temporary)
            (root/'modules').mkdir()
            policy = root/'modules/catalog-yaml-policy.am'
            shutil.copy2(compiler.ROOT/'modules/catalog-yaml-policy.am', policy)
            source = (compiler.ROOT/'programs/x86_64/nvim').read_text()
            for arch in architectures:
                path = root/'programs'/arch/'example'
                path.parent.mkdir(parents=True)
                path.write_text(source.replace('APP=nvim', 'APP=example')
                    .replace('x86_64/nvim', arch+'/example')
                    .replace('^nvim-linux-x86_64[.]appimage$', '^example-.*[.]AppImage$'))
            with patch.object(compiler, 'ROOT', root):
                compiler.generate()
            for arch in architectures:
                for token, allowed in cases.items():
                    name = 'example-'+token+'.AppImage'
                    url = 'https://example.invalid/releases/download/v1/'+name
                    facts = '\t'.join(['1', '1', *map(json.dumps, [
                        '2026-11-06T12:00:00Z', '2026-11-06T11:00:00Z', 'v1', name, url]),
                        'false'])+'\n'
                    for command in (['mawk'], ['gawk'], ['busybox','awk']):
                        with self.subTest(arch=arch, token=token, command=command):
                            result = subprocess.run([*command, '-f', str(policy)],
                                input=facts, text=True, capture_output=True, timeout=10,
                                env={**os.environ, 'LC_ALL':'C',
                                    'AM_YAML_RECIPE':arch+'/example', 'AM_YAML_REPOSITORY':'16408992',
                                    'AM_YAML_NOW':'2026-11-06T12:00:00Z', 'AM_YAML_PIN':'a'*40})
                            if arch in allowed:
                                self.assertEqual(result.returncode, 0, result.stderr)
                                self.assertEqual(result.stdout.splitlines()[-1], url)
                            else:
                                self.assertEqual(result.returncode, 3, result.stderr)
                                self.assertEqual(result.stdout, '')
                                self.assertIn('no_matching_asset', result.stderr)

    def test_unenrolled_architectures_select_through_common_registry(self):
        baseline_rows, baseline_sources = host_catalog.installation_configuration()
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
                self.assertEqual(rows, baseline_rows)
                self.assertEqual(sources, baseline_sources)
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
