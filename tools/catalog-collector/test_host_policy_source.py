"""The manifest compiler retains recipe-owned launcher/refresh choices."""
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import host_policy_source as compiler


class HostPolicySource(unittest.TestCase):
    def test_generated_recipes_preserve_configuration_and_are_repeatable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'modules').mkdir()
            recipes = root/'programs/x86_64'
            recipes.mkdir(parents=True)
            policy = root/'modules/catalog-yaml-policy.am'
            shutil.copy2(compiler.ROOT/'modules/catalog-yaml-policy.am', policy)
            with patch.object(compiler, 'ROOT', root):
                compiler.generate()
                first = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
                compiler.generate()
                second = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(first, second)
            obsidian = (recipes/'obsidian').read_text()
            self.assertIn('EXTRA_APP_LAUNCHERS=obsidian-gui\n', obsidian)
            self.assertIn('DESKTOP_EXEC=installed\n', obsidian)
            self.assertEqual((recipes/'nvim-nightly').read_text().count('REFRESH_ALWAYS=true\n'), 1)
            self.assertNotIn('EXTRA_APP_LAUNCHERS', (recipes/'neovide').read_text())
            for recipe in recipes.iterdir():
                self.assertEqual(recipe.read_bytes(), (Path(__file__).resolve().parents[2]/'programs/x86_64'/recipe.name).read_bytes())


if __name__ == '__main__':
    unittest.main()
