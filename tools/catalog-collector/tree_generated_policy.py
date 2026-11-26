"""The committed catalog-yaml-policy.am is exactly what its sources generate.

Hosts fetch the policy module from the branch, so it stays committed although
it is derived (ticket 29) from the recipes: their declarations and the URL and
AppImage policy lines (ticket 26). A hand edit, or a source change without regeneration,
fails here. It follows
whatever the tree holds: `-p 'tree_*.py'`.
"""
from pathlib import Path
import shutil
import tempfile
import unittest

import appimage_policy_source
import recipe_policy_source

ROOT = Path(__file__).resolve().parents[2]
POLICY = 'modules/catalog-yaml-policy.am'


class GeneratedPolicy(unittest.TestCase):
    def test_committed_policy_equals_a_regeneration(self):
        with tempfile.TemporaryDirectory(prefix='generated-policy-') as temporary:
            root = Path(temporary)
            # Read the live sources through links; write only the copy.
            (root/'programs').symlink_to(ROOT/'programs')
            (root/'modules').mkdir()
            shutil.copy2(ROOT/POLICY, root/POLICY)
            # The order merge.py uses: declarations and URL policies, then AppImage policies.
            recipe_policy_source.generate(root)
            appimage_policy_source.generate(root)
            self.assertEqual((root/POLICY).read_bytes(), (ROOT/POLICY).read_bytes(),
                             'regenerate: python3 tools/catalog-collector/recipe_policy_source.py '
                             'and appimage_policy_source.py')


if __name__ == '__main__':
    unittest.main()
