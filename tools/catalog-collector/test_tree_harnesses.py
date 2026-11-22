"""Every whole-tree class built on a manager harness runs it on the live tree.

The harnesses install pinned recipes unless `live` is set (ticket 28), so a
tree_*.py class without `live = True` would still pass, on the pinned recipes.
"""
import importlib
import inspect
from pathlib import Path
import unittest


class TreeHarnesses(unittest.TestCase):
    def test_every_harness_class_of_the_tree_tier_sets_live(self):
        checked = []
        for path in sorted(Path(__file__).parent.glob('tree_*.py')):
            module = importlib.import_module(path.stem)
            for name, value in vars(module).items():
                if (inspect.isclass(value) and value.__module__ == module.__name__
                        and issubclass(value, unittest.TestCase) and hasattr(value, 'live')):
                    checked.append(path.stem+'.'+name)
                    with self.subTest(harness=checked[-1]):
                        self.assertIs(value.live, True)
        self.assertTrue(checked, 'no tree_*.py class has a harness with a live flag')


if __name__ == '__main__':
    unittest.main()
