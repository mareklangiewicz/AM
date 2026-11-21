# Unpin tests from live recipes

Type: task
Label: implementation:task
Status: resolved
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

November 16, 2026: the two pure count pins are gone: `len(APPIMAGES)==105`
is now "not empty", and the unavailable-recipes test checks every entry
without asserting how many there are. The named live recipes and the
whole-tree loops remain; see the tier proposal on
[ticket 30](30-add-ci-fast-test-tier.md).

November 16, 2026: the whole-tree checks moved out of the unit suite into
`tree_*.py` (see [ticket 30](30-add-ci-fast-test-tier.md)):
`tree_appimages.py`, `tree_host_cutover.py`, `tree_host_policy_source.py`,
`tree_unavailable_recipes.py`. Still open here: the fast tier reads named live
recipes (`20x`, `nvim`, `obsidian`, `0xfx`, `emmylua` and the enrolled rows in
`test_recipe_declarations.py`), so an upstream change to one of those can
still fail a `test_*.py`; and nothing was moved into `merge.py gate`.

November 17, 2026: another face of the live-recipe coupling. With 579
recipe edits uncommitted, 17 fast-tier tests errored with "recipe changed since
discovery" (`catalog_sources.py` compares the working-tree file with the
same path at a commit). They pass once the change is committed. Until this
ticket lands, run either tier on a committed tree; CI always does.

November 21, 2026: measured instead of grepped. Two throwaway worktrees, each
with one commit over every recipe an upstream merge can touch (11,781 paths
under `programs/{x86_64,aarch64,i686,armv7l}/`, minus `fork-owned.txt`): one
appends a comment line to each, one deletes them all. The Fast tests suites
were run in each. Before: the edit failed 3 tests (`test_reconstruct` x2 on
the live obsidian short recipe, the provenance test in `test_contracts` on
live 20x); the deletion failed 90 (with subtests) across about 15 files.
`recipe-conversion`, `upstream-merge`, `release` and `test/e2e` read no live
recipe.

Fixed in `efb2449cd` and `5ff5fa709`: new `tools/catalog-collector/pinned_recipes.py`
reads recipe text at one commit (`3b9b91862`, whose `programs/` equals HEAD's)
and both suites use it for every named recipe used as material (obsidian,
20x, nvim, 0xfx, ageha-editor, am, and the batch lifecycle recipes).
`pinned_recipes.repository()` makes a temporary Git repo that borrows this
checkout's objects, for code that reads a recipe from Git and from the working
tree. `test_recipe_refresh` pinned HEAD, which was the live tree. After, at
`5ff5fa709` with ruff clean: HEAD and the edit pass every suite; the deletion
leaves 7 collector errors, all one class.

Still open, the derived-file class: tests that read the live enrollment
(`collection-recipes.txt`, `collection-apps.json`) together with the recipes
it lists, through `host_catalog.configuration()` and `recipe_rows(ROOT)`:
`test_catalog_only_enrollment` (2), `test_host_cutover` (setUpClass),
`test_large_batch_enrollment` and `test_next_ten_enrollment`, and two in
`test_recipe_declarations`. A real merge rewrites those files with the recipes
(`merge.py` moves a deleted or no-longer-declared enrolled recipe to
catalog-only), so they are coupled even where the deletion mutation
overstates it; `test_large_batch_enrollment` still hard-codes the recipes the
2026-11-16 merge reverted. Options put to Marek: run them on a pinned snapshot
of the whole configuration, move the live-state statements to the tree tier,
or wait for ticket 29.

November 21, 2026: resolved. `572bac279` closes the derived-file class:
`pinned_recipes.configuration()` unpacks every recipe and the enrollment
files at the pinned commit, and the seven enrollment-coupled tests run on it
(the cutover `apply` test on a pinned checkout whose HEAD is that commit, so
its source check still holds). None of the seven was a pure live-state check,
so none moved to the tree tier. It also fixes a regression from `5ff5fa709`:
the tree tier had started installing pinned recipes; a `live` flag on the
manager harness now keeps `tree_host_cutover.py` and `tree_appimages.py` on
the live tree (control: 107 errors there with every upstream recipe deleted).
Final, at `572bac279`: ruff clean; every Fast suite passes on HEAD, with every
upstream recipe edited, and with every upstream recipe deleted; Long tests
44936940091 green on `ci/ticket28`. Not done: nothing was moved into `merge.py
gate`; the live-tree statements stay in the tree tier (ticket 30). Not
covered by the mutations: an upstream change to a fork-side derived file in
`test-data/` (`appimage-policies.json`), which unit tests still read live.
