"""The committed policy module is exactly what the live recipes compile to.

Copies the whole `programs/` tree. Run before an upstream merge and on demand:
`-p 'tree_*.py'`.
"""
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import recipe_policy_source as compiler
from recipe_declarations import recipe_rows


class TreeHostPolicySource(unittest.TestCase):
    def test_no_live_recipe_sets_the_removed_fresh_only_flag(self):
        # Old data warns, never refuses (catalog-simplification ticket 23); the
        # parser ignores the flag only so historical trees still replay.
        found=[row['recipe'] for row in recipe_rows(compiler.ROOT) if 'CATALOG_FRESH_ONLY' in row['settings']]
        self.assertEqual(found,[])

    def test_recipes_are_authoritative_and_compilation_is_repeatable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'modules').mkdir()
            recipes = root/'programs/x86_64'
            shutil.copytree(compiler.ROOT/'programs',root/'programs',symlinks=True)
            policy = root/'modules/catalog-yaml-policy.am'
            shutil.copy2(compiler.ROOT/'modules/catalog-yaml-policy.am', policy)
            before={p:p.read_bytes() for p in (root/'programs').rglob('*') if p.is_file()}
            with patch.object(compiler, 'ROOT', root):
                compiler.generate()
                first=policy.read_bytes()
                compiler.generate()
                self.assertEqual(first,policy.read_bytes())
                # A recipe edit survives regeneration and controls both consumers.
                recipe=recipes/'emmylua'
                recipe.write_text(recipe.read_text().replace(
                    'emmylua_ls emmylua_check emmylua_doc_cli luafmt', 'emmylua_ls luafmt'))
                compiler.generate()
                row=next(r for r in recipe_rows(root) if r['app']=='emmylua')
                self.assertEqual(row['tools'],['emmylua_ls','luafmt'])
                self.assertEqual(row['archive']['launchers'],['emmylua_ls:emmylua_ls','luafmt:luafmt'])
                self.assertIn('recipes_tools["x86_64/emmylua"]="emmylua_ls luafmt"',policy.read_text())
                self.assertEqual(recipe.read_text().count('emmylua_ls luafmt'),1)
            for path,raw in before.items():
                if path!=recipes/'emmylua':self.assertEqual(raw,path.read_bytes())


if __name__=='__main__':unittest.main()
