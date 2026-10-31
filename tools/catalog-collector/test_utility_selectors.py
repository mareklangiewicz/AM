"""Utility recipes against accepted live bytes and their original selectors; no HTTP."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tarfile
import unittest

from delivery import unpack_artifact
from storage import validate

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'docs/track/release-catalog/research/am-utils-live-20261031-evidence.tar.gz'
ALIAS = 'https://api.github.com/repos/ivan-hc/am-utils/releases'
BASELINE = 'c787efe3a42fac015f743255006fddd7ea9b3817'


def accepted_tree():
    with tarfile.open(EVIDENCE) as archive:
        raw = archive.extractfile('collection.zip').read()
        artifacts = json.load(archive.extractfile('artifacts.json'))['artifacts']
    artifact = next(a for a in artifacts if a['name'].startswith('restricted-'))
    assert 'sha256:' + hashlib.sha256(raw).hexdigest() == artifact['digest']
    files = unpack_artifact(raw)
    tree = {p.removeprefix('candidate/'): b for p, b in files.items() if p.startswith('candidate/')}
    validate(tree)
    return tree


def selector_script(path):
    return path.read_text().replace('/opt/am/modules/appimage.am', str(ROOT/'modules/appimage.am')).replace(
        'am_package "$0" "$@"', 'am_appimage_select_asset')


class UtilitySelectors(unittest.TestCase):
    def test_all_356_selectors_preserve_original_policy_and_select_real_accepted_assets(self):
        tree = accepted_tree()
        index = validate(tree)
        rid = index['aliases'][ALIAS]['request_id']
        raw = tree[index['entries'][rid]['observation']['path']]
        assets = {a['browser_download_url'] for r in json.loads(raw) for a in r['assets']}
        rows = json.loads((ROOT/'docs/track/release-catalog/research/recipe-family-inventory.json').read_bytes())['plain_utility_batch']
        self.assertEqual(len(rows), 356)
        for row in rows:
            path = ROOT/row['path']
            with self.subTest(recipe=row['path']):
                old = subprocess.check_output(['git', 'show', BASELINE+':'+row['path']], cwd=ROOT).decode()
                versions = re.findall(r'^version=\$\(curl[^|]+\| (.*)\)$', old, re.M)
                self.assertEqual(len(versions), 2)
                self.assertEqual(versions[0], versions[1])
                source = path.read_text()
                self.assertEqual(source.count('APP='), 1)
                self.assertIn('APP='+path.name+'\n', source)
                self.assertIn('select_asset() {\n\t'+versions[0]+'\n}', source)
                self.assertEqual(source.count('# AM-CATALOG-RECIPE 1'), 1)
                self.assertNotRegex(source, r'(?m)^\s*(?:curl|wget|chmod|ln|cat >>)\s|AM-updater|/opt/\$APP')
                before = subprocess.run(['sh', '-c', versions[0]], input=raw,
                    env={'PATH':'/usr/bin:/bin', 'LC_ALL':'C', 'APP':path.name}, capture_output=True, check=True)
                after = subprocess.run(['sh', '-c', selector_script(path)], input=raw,
                    env={'PATH':'/usr/bin:/bin', 'LC_ALL':'C'}, capture_output=True, check=True)
                self.assertEqual(after.stdout, before.stdout)
                self.assertIn(after.stdout.decode().strip(), assets)

    def test_cxxfilt_and_dot_identity_keep_original_regex_matching_and_order(self):
        for arch in ('aarch64', 'x86_64'):
            for app, component in (('c++filt', 'c%2B%2Bfilt'), ('ld.bfd', 'ldXbfd')):
                # The original dot is a regex wildcard; retain that behavior and order.
                urls = [f'https://github.com/ivan-hc/am-utils/releases/download/{arch}-20261031/{component}_{n}-{arch}-static' for n in (2, 1)]
                raw = json.dumps([{'assets':[{'browser_download_url':u} for u in urls]}]).encode()
                result = subprocess.run(['sh', '-c', selector_script(ROOT/'programs'/arch/app)],
                    input=raw, capture_output=True, check=True)
                self.assertEqual(result.stdout.decode().strip(), urls[0])


if __name__ == '__main__':
    unittest.main()
