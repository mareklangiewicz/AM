"""Actual c++filt recipe selectors against retained public metadata, no HTTP."""
import json
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
BODY = ROOT / 'docs/track/release-catalog/research/am-utils-release-20261028/body.json'


class UtilitySelectors(unittest.TestCase):
    def test_cxxfilt_install_and_update_select_encoded_assets_for_both_architectures(self):
        raw = BODY.read_bytes()
        assets = {a['browser_download_url'] for r in json.loads(raw) for a in r['assets']}
        for arch in ('aarch64', 'x86_64'):
            path = ROOT / 'programs' / arch / 'c++filt'
            source = path.read_text()
            app = re.findall(r'^APP=(.*)$', source, re.M)
            self.assertEqual(app, ['c++filt', 'c++filt'])
            selectors = [l for l in source.splitlines() if l.startswith('version=')]
            self.assertEqual(len(selectors), 2)
            for line in selectors:
                self.assertTrue(line.startswith('version=$(curl -Ls https://api.github.com/repos/ivan-hc/am-utils/releases | sed '))
                suffix = line.split('| sed ', 1)[1][:-1]
                # Only the trusted selector suffix executes; no recipe mutation,
                # installer/updater body, network or downloaded executable.
                result = subprocess.run(['sh', '-c', 'sed ' + suffix], input=raw,
                    env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'APP': app[0]},
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                selected = result.stdout.decode().strip()
                with self.subTest(arch=arch, selector=line):
                    self.assertTrue(selected, 'c++filt selector returned no asset')
                    self.assertIn(selected, assets)
                    self.assertEqual(selected,
                        f'https://github.com/ivan-hc/am-utils/releases/download/{arch}-20260526/c%2B%2Bfilt_2.46-3-{arch}-static')


if __name__ == '__main__':
    unittest.main()
