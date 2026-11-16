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
November 16, 2026: first pass, read only (`grep programs` over
`tools/catalog-collector/test_*.py` and `fixture_*.py` at `7ce058b06`). Tests
that read recipes from the live tree, as opposed to a pinned Git object or a
recipe they write themselves:

| File | Reads live |
| --- | --- |
| `test_yaml_appimages.py` | every recipe in the AppImage policy table, and pins its length (105) |
| `test_host_policy_source.py` | copies the whole `programs/` tree; `emmylua` |
| `test_recipe_declarations.py` | `20x`, `nvim`, and each enrolled recipe row |
| `test_bulk_recipe_urls.py` | `20x` (as a stand-in declaration) |
| `test_catalog_sources.py` | `0xfx` |
| `fixture_manager.py`, `test_yaml_manager_integration.py` | `obsidian` and the recipes it installs |
| `test_unavailable_recipes.py` | pins the length of `unavailable-github-recipes.json` (0) |

Already pinned to Git objects and fine: `test_bulk_recipes.py`,
`test_recipe_refresh.py`, parts of `test_bulk_recipe_urls.py` and
`test_catalog_sources.py`. Not yet looked at: tests that read the fork-side
derived files, and `test/e2e`.
