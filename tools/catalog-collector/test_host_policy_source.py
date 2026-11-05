"""Recipe selection policy and collector settings follow recipe declarations."""
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import recipe_policy_source as compiler
from recipe_declarations import recipe_rows


class HostPolicySource(unittest.TestCase):
    def test_recipes_are_authoritative_and_compilation_is_repeatable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'modules').mkdir()
            recipes = root/'programs/x86_64'
            recipes.mkdir(parents=True)
            for row in recipe_rows(compiler.ROOT):
                shutil.copy2(compiler.ROOT/'programs/x86_64'/row['app'],recipes/row['app'])
            policy = root/'modules/catalog-yaml-policy.am'
            shutil.copy2(compiler.ROOT/'modules/catalog-yaml-policy.am', policy)
            before={p.name:p.read_bytes() for p in recipes.iterdir()}
            with patch.object(compiler, 'ROOT', root):
                compiler.generate()
                first=policy.read_bytes()
                compiler.generate()
                self.assertEqual(first,policy.read_bytes())
                self.assertEqual(first,(Path(__file__).resolve().parents[2]/'modules/catalog-yaml-policy.am').read_bytes())
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
            for path in recipes.iterdir():
                if path.name!='emmylua':self.assertEqual(before[path.name],path.read_bytes())


    def test_nonliteral_and_inconsistent_headers_refuse(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            recipes=root/'programs/x86_64';recipes.mkdir(parents=True)
            source=(compiler.ROOT/'programs/x86_64/emmylua').read_text()
            recipe=recipes/'emmylua'
            for bad in (source.replace('CATALOG_FRESH_ONLY=true','CATALOG_FRESH_ONLY=typo'),
                        source.replace('PACKAGE_LAYOUT=toolset','PACKAGE_LAYOUT=tar'),
                        source.replace('APP=emmylua','APP=$(touch /tmp/should-not-run)'),
                        source.replace('APP=emmylua','APP=emmylua; false'),
                        source.replace('CATALOG_REPOSITORY_ID=872860168', 'CATALOG_REPOSITORY_ID=0'),
                        source.replace('CATALOG_CHANNEL=stable\n', '')):
                recipe.write_text(bad)
                with self.assertRaises(ValueError):recipe_rows(root)



if __name__ == '__main__':unittest.main()
