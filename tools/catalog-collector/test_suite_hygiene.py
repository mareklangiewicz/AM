"""Test modules never bind another test module's TestCase (ticket 25 retro).

`from test_x import SomeCase` puts SomeCase in a second module's namespace,
so discovery runs every one of its tests twice (27 duplicate runs of
test_yaml_reader.Experiment until that module went). Share helpers through
fixture_* modules, or a deliberate subclass (`class C(test_x.Case)`), instead.
"""
import ast
from pathlib import Path
import unittest

TOOLS = Path(__file__).resolve().parents[1]


def test_classes(modules):
    """{module: TestCase class names}, following bases across the given modules."""
    trees = {name: ast.parse(source) for name, source in modules.items()}
    found = {name: set() for name in modules}
    grew = True
    while grew:
        grew = False
        for name, tree in trees.items():
            for node in tree.body:
                if not isinstance(node, ast.ClassDef) or node.name in found[name]:
                    continue
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        hit = base.id.endswith('TestCase') or base.id in found[name]
                    elif isinstance(base, ast.Attribute):
                        owner = base.value.id if isinstance(base.value, ast.Name) else ''
                        hit = base.attr.endswith('TestCase') or base.attr in found.get(owner, ())
                    else:
                        hit = False
                    if hit:
                        found[name].add(node.name)
                        grew = True
                        break
    return found


def violations(modules):
    """'importer: from source import Name' for each TestCase bound by import."""
    classes = test_classes(modules)
    bad = []
    for name, source in modules.items():
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ImportFrom) and node.module in classes:
                for alias in node.names:
                    if alias.name == '*' or alias.name in classes[node.module]:
                        bad.append(name+': from '+node.module+' import '+alias.name)
    return bad


def suite_modules(directory):
    return {path.stem: path.read_text(encoding='utf-8')
            for pattern in ('test_*.py', 'tree_*.py') for path in sorted(directory.glob(pattern))}


class SuiteHygiene(unittest.TestCase):
    def test_no_tool_suite_imports_another_modules_test_case(self):
        for directory in sorted(path for path in TOOLS.iterdir() if path.is_dir()):
            with self.subTest(suite=directory.name):
                self.assertEqual(violations(suite_modules(directory)), [])

    def test_the_check_sees_direct_inherited_and_star_imports(self):
        modules = {
            'test_a': 'import unittest\nclass Case(unittest.TestCase): pass\nclass More(Case): pass\ndef helper(): pass\n',
            'test_b': 'import test_a\nclass Again(test_a.More): pass\n',
            'test_c': 'from test_a import Case, helper\nfrom test_b import Again\n',
            'test_d': 'from test_a import *\n',
            'test_e': 'from test_a import helper\nimport test_a\nclass Sub(test_a.Case): pass\n',
        }
        self.assertEqual(sorted(violations(modules)), [
            'test_c: from test_a import Case', 'test_c: from test_b import Again', 'test_d: from test_a import *'])


if __name__ == '__main__':
    unittest.main()
