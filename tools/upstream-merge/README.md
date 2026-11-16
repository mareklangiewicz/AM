# Upstream merge

Takes `upstream/main` into `main-marek` the way
[ADR 0005](../../docs/adr/0005-upstream-authoritative-converted-recipes-derived.md)
decides: upstream is authoritative for recipes, and a recipe the fork converted
is converted again from upstream's new text, never merged by hand. Terms are in
the root `GLOSSARY.md` under Recipes.

## Run a merge

```sh
git fetch upstream
python3 tools/upstream-merge/merge.py plan  --upstream upstream/main --receipt /tmp/plan.json
python3 tools/upstream-merge/merge.py apply --upstream upstream/main --receipt docs/track/<effort>/upstream-merge-<date>.json
# hand-merge APP-MANAGER, modules/install.am, README.md; git add them
python3 tools/upstream-merge/merge.py gate  --receipt docs/track/<effort>/upstream-merge-<date>.json
# run the tool tests and regress/, then commit the merge
```

- `plan` is the dry run. It reads Git objects only and changes nothing. It
  prints the counts and writes the receipt. `--recipes FILE` also writes the
  outcome of every recipe.
- `apply` needs a clean checkout. It starts `git merge --no-commit --no-ff`,
  writes every recipe and the fork-side files that follow from them, stages
  them, and stops. Only the three hand-merged files are left in conflict. It
  never commits, pushes or touches an installed host.
- `gate` checks the merge as it stands (in progress or committed) against the
  receipt. It exits 1 and lists every disagreement.

The receipt you commit holds the parents, the counts, the hashes of the
fork-side files and the `attention` section. The outcome of every recipe is a
long list nobody reads as a record: `apply` leaves it in the Git directory
(`.git/upstream-merge-recipes.json`), where `gate` finds it and checks it
against the hash in the receipt. To gate somewhere else, pass the same file
with `--recipes`. A receipt from before November 16, 2026 carries the list
itself and gates as before.

Merge, never rebase: `am` reads this branch live.

## What happens to each recipe

Every recipe path in either parent gets exactly one outcome.

| Outcome | When | Result |
| --- | --- | --- |
| `untouched` | Upstream did not change it since the merge base. | The fork's file, byte for byte. |
| `taken from upstream` | Upstream added it, or changed a recipe the fork never converted. | Upstream's text. New recipes land as originals; converting and enrolling them is a later batch. |
| `re-converted` | Upstream changed a recipe the fork converted, and the same form converts again. | Upstream's new text in the fork's form. |
| `fell back` | The same form refused. | A long recipe if that converts, else upstream's original. The refusal reasons are in the row. |
| `deleted` | Upstream deleted it. | Deleted. |
| `fork-owned kept` | The path is in `fork-owned.txt`. | The fork's file. An upstream change, deletion or same-name addition is named in the row. |

The plan stops with exit 2, changing nothing, when a person has to decide: a
fork-only recipe missing from `fork-owned.txt`, or a recipe both sides added
with different text.

`fork-owned.txt` holds one `programs/ARCH/APP` path per line. Add a recipe
there to keep hand edits across merges; without that, hand edits to a converted
recipe end at the next merge that touches it (the receipt lists them under
`hand_edits_ended`).

## Fork-side files that follow

`apply` also rewrites, from the recipe outcomes:

- `tools/catalog-collector/recipe-url-policies.json`: policies of changed
  recipes are dropped, policies of re-converted long recipes added.
- `modules/catalog-yaml-policy.am`: recompiled. The copy under
  `/opt/am/modules/` on an installed host is not touched; delivering it is a
  separate authorized step.
- `tools/catalog-collector/collection-recipes.txt` and `collection-apps.json`:
  an enrolled recipe declaration that is no longer one keeps its source
  enrolled as catalog-only.
- `tools/catalog-collector/unavailable-github-recipes.json`: entries for
  recipes upstream changed or deleted are dropped.
- `programs/<arch>-apps`: upstream's list plus the lines the fork added.

Before anything is written, the merged recipes and these files are compiled in
a scratch tree; a declaration or policy they do not support refuses there.

## Read the receipt's `attention` section

- `fell_back`: each with its refusal reasons. A new upstream template version
  shows up here until it is reviewed into
  `tools/recipe-conversion/layouts.json`.
- `fork_owned_upstream_changes`: upstream moved under a fork-owned recipe.
- `sources_to_retire`: catalog sources no surviving recipe selects from. The
  merge leaves them enrolled: the collector refuses to drop a source the
  published catalog retains, so retiring them is separate collector work.

## What the gate does not cover

Tool tests and `regress/` are run by hand after the gate, including the
collector's whole-tree tier (`-p 'tree_*.py'`, see
`tools/catalog-collector/README.md`). Tests pinned to a
recipe family upstream deleted have to be retired in the same merge. Pushing,
the schedule pin (`CATALOG_SCHEDULE_REVISION`) and any installed-host change
need Marek's authorization.

## Tests

```sh
python3 -B -m unittest discover -s tools/upstream-merge -p 'test_*.py'
```
