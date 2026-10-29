"""Round-trip the real installer encoder through sed and shell evaluation."""
from pathlib import Path
import subprocess
import tempfile
import unittest


class RecipeReplacement(unittest.TestCase):
    def test_literal_values_survive_both_interpreters(self):
        module = Path(__file__).resolve().parents[2] / 'modules/install.am'
        source = module.read_text()
        start = source.index('am_recipe_replacement() {')
        helper = source[start:source.index('\n}', start) + 2]
        with tempfile.TemporaryDirectory() as directory:
            for value in ('', 'with spaces', r'a\b', '"`$&|', '$(touch INJECTED)', '`touch INJECTED`'):
                with self.subTest(value=value):
                    script = helper + '''
encoded=$(am_recipe_replacement "$1")
printf 'value="PLACEHOLDER"\\nprintf \'%%s\' "$value"\\n' > recipe
sed -i "s|PLACEHOLDER|$encoded|" recipe
sh recipe
'''
                    result = subprocess.run(['bash', '-c', script, 'test', value],
                                            cwd=directory, capture_output=True, check=True)
                    self.assertEqual(result.stdout, value.encode())
                    self.assertFalse((Path(directory)/'INJECTED').exists())
