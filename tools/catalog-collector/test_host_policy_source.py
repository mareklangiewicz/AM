"""Recipe selection policy and collector settings follow recipe declarations."""
from pathlib import Path
import tempfile
import unittest

import recipe_policy_source as compiler
from recipe_declarations import recipe_rows


class HostPolicySource(unittest.TestCase):
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
