# Unpin tests from live recipes

Type: task
Label: implementation:task
Status: open
Blocked by: none

## Outcome

An upstream change to any recipe cannot fail a test. Tests read frozen fixture
copies; statements about the whole live tree are checked by `merge.py gate`.

## Why

The first merge needed hand edits to tests that pin live counts and names: 115
AppImage policies (`test_yaml_appimages.py`), 49 unavailable recipes
(`test_unavailable_recipes.py`), `mercury`, `obs-studio`, enrollment
baselines. Decided in
[ticket 24](24-simplify-and-unify-catalog-process.md#answer--november-16-2026).

## Scope

- List every test that reads `programs/` or a fork-side derived file from the
  live tree. The merge commit `8f3bd0cf3` names the ones that broke.
- For each: freeze the input as a fixture, or turn the assertion into an
  invariant the gate computes (for example "every enrolled declaration
  compiles"), or delete it if it only restated a count.
- The corpus tests in `tools/recipe-conversion` already pin Git objects
  (`7b4f831e6`, `6277377ae`), not the live tree; leave them.

## Comments
