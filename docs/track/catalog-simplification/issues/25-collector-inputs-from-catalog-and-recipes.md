# Derive the collector's inputs from catalog/ and the recipes, in YAML

Type: grilling
Label: wayfinder:grilling
Status: open
Triage: needs-triage
Blocked by: none

## Question

The hourly collector and the recipe tools keep about 1.9 MB of JSON under
`tools/`. AM hosts read none of it: `am` reads only `catalog/` and the
recipes. Most of it is a second copy of facts that `catalog/` or `programs/`
already hold. Which facts must be kept, where should each live, and in what
YAML?

## Direction (Marek, November 26, 2026)

- Data we must keep lives in YAML, not JSON.
- Simplify it where possible; a fact that `catalog/` or a recipe already holds
  is derived, not stored a second time.
- YAML that a shell script must parse gets the extra structural constraints
  that make that easy, as `catalog/` already has (`docs/catalog-format.md`,
  read in awk by `modules/catalog-parser.am`).
- Later, recipes themselves become very simple YAML files parsed by a reusable
  shell script: see the yamx project (`~/code/shell/yamx`, a parameterized
  family of YAML subsets built to be easy to validate, parse and generate in
  POSIX shell). Choices here should fit that: a per-recipe fact (its Git source,
  its URL rules) belongs in the recipe, not in a separate registry, and a
  constrained form chosen here should be one a yamx profile can state.

## Evidence

From `scripts/25/measure.py`, run on `ab4d305ae` (rerun it from the
repository root):

| File | Size | Read by | Facts found nowhere else |
| --- | --- | --- | --- |
| `tools/catalog-collector/source-names.json` | 269 KB | collector | Only the 25 `retired` names. All 8,288 `active` rows equal a `catalog/repositories/<name>.yaml` file's name and its `repository_id`. |
| `tools/catalog-collector/collection-apps.json` | 767 KB | collector (enrollment) | Possibly none: all 8,412 apps are in `catalog/apps.yaml` and all their repositories in `source-names.json`. But the collector writes `apps.yaml`, so whether it can also be the enrollment input is the open question below. |
| `tools/catalog-collector/recipe-url-policies.json` | 804 KB | collector, conversion tools | None: generated from `programs/` (all 1,464 rows carry their recipe's sha256; `tree_generated_policy` fails when stale). The collector reads it only to learn the repository of each inline-form script (1,072 x86_64 scripts still call `catalog-yaml.am`). |
| `tools/catalog-collector/appimage-policies.json` | 52 KB | tests, `tools/upstream-merge` | None: generated, 105 rows, each with its recipe's sha256. |
| `tools/catalog-collector/git-sources.json` | 5 entries | collector (`git_observations.py`) | Yes: which 5 repositories are read from Git tags or branch files. A per-recipe fact. |
| `tools/recipe-conversion/layouts.json`, `tools/recipe-reconstruction/provenance.json` | 24 KB, 1 KB | one-off conversion tools | Inputs to those tools only. |
| `tools/catalog-contract/platforms.json` | 0.4 KB | page, collector, e2e | Yes: the four processor types. Shared by Python, JS and shell readers. |

The collector's modules (`catalog_run.py` and its imports: `bounded`,
`documents`, `git_observations`, `host_catalog`, `recipe_declarations`) name
`collection-apps.json`, `git-sources.json`, `platforms.json`,
`recipe-url-policies.json` and `source-names.json`, plus its own run outputs
`removed.json` and `run.json`.

Not in scope: tool configuration whose format the tool fixes
(`package.json`, `package-lock.json`, `renovate.json`). Ticket 10 said the
`.vscode` schema associations go; `.vscode/settings.json` still has them, so
check that separately. `tools/catalog-contract/examples/bad.json` is a test
fixture.

## To decide

1. **Enrollment's source of truth.** Can `catalog/apps.yaml` (plus
   `collection-recipes.txt`) be what the collector reads to choose its
   repositories, given that the collector also writes it? Or does enrollment
   stay a hand-edited list, as a YAML file?
2. **Repository file names.** Derive them from `catalog/repositories/` (each
   file already holds its `repository_id`) and keep only the retired names,
   in YAML or in Git history?
3. **The URL policies.** Retire `recipe-url-policies.json` by converting the
   inline-form scripts to recipe declarations (kitty's form)? That is the same
   work as the 1,072-script conversion, and the step before recipes become
   YAML.
4. **Git sources.** Move the 5 entries into those apps' recipes?
5. **Run outputs.** Should `removed.json` and `run.json` be YAML too?
6. **The shell-parseable form.** For each YAML file that a shell reads: the
   catalog's existing grammar, a yamx profile, or a new constraint set?
   Collector-only inputs (read by Python) may need none.

## Comments
