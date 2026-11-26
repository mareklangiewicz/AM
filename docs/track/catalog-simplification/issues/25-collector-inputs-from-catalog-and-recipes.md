# Derive the collector's inputs from catalog/ and the recipes, in YAML

Type: grilling
Label: wayfinder:grilling
Status: resolved
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

## Answer

Decided with Marek in two grilling rounds (November 26, 2026; the details are in
Comments). Enrollment is the app set in `catalog/apps.yaml`, and identities come
from the repository files. A new app starts as a never-read repository file
(`releases: {}`, nothing observed). File names are derived from the `apps.yaml`
pointers, and the 25 retired names are kept in `retired-names.yaml`. Both
policy files' rows move into their recipes as `CATALOG_*` assignments (the
correction in Comments replaces "generated in memory"). The 5 Git sources become `CATALOG_GIT_*` assignments in their
scripts. `platforms.json`, `removed.json` and `run.json` become YAML. Every new
YAML file uses the catalog grammar, with lists written as maps; no shell reads
any of them. `collection-recipes.txt` stays. Implemented in
[26](26-move-policy-rows-into-recipes.md),
[27](27-accept-a-never-read-repository-file.md),
[28](28-enroll-from-apps-yaml.md) (after 27),
[29](29-derive-git-sources-from-recipes.md),
[30](30-convert-inline-form-scripts-to-declarations.md),
[31](31-platforms-and-run-outputs-as-yaml.md) and
[32](32-drop-vscode-schema-associations.md).

## Comments

### November 26, 2026: grilling round 1 (Marek: yes to all)

1. Enrollment: `catalog/apps.yaml` becomes the enrollment list. Each app's
   identity is `repository_id` and `repository` in its repository file, and
   `collection-apps.json` goes. The collector still rewrites `apps.yaml`, but
   only to refresh the per-architecture labels, never the set of apps.
   `collection-recipes.txt` stays (it marks readiness to install, ticket 137).
   Adding an app means an `apps.yaml` entry plus a stub repository file.
   Checked afterwards: the stub breaks the current grammar. The schema requires
   `releases`, and `modules/catalog-parser.am` rejects a never-collected
   document without a failure. That goes to round 2.
2. Repository file names come from the `apps.yaml` pointers. The 25 retired
   names move to `tools/catalog-collector/retired-names.yaml`, and
   `source-names.json` goes. Git history won't do as the guard, because CI
   checkouts are shallow.
3. The 1,072 inline-form scripts get converted to recipe declarations in a
   follow-up ticket, which retires `recipe-url-policies.json`. Until then the
   collector and the tests generate both policy files in memory from
   `programs/`, and the committed copies and `tree_generated_policy` go. If
   that measures too slow for an hourly run, the copies stay committed until
   the conversion.
4. The 5 `git-sources.json` entries move into their recipes. Checked
   afterwards: all 5 (junest, translate-shell, mediaurl-js, anything-llm,
   cursor-ai-downloads) are `script` form, and a declaration is a set of
   `CATALOG_*` shell assignments, not YAML. That goes to round 2.
5. `removed.json` and `run.json` become YAML.

### November 26, 2026: grilling round 2 (Marek: yes to all)

6. New enrollments: a third repository-file state, "enrolled, not yet read":
   `$schema`, `repository_id`, `repository` and `releases: {}`, with no
   `observed_at` and no `failed_at`. The schema, `modules/catalog-parser.am`
   and `tools/catalog-contract/parse.mjs` each accept it, with a test in each.
   This settles the stub question from round 1.
7. Git facts: the 5 scripts get `CATALOG_GIT_*` assignments (for example
   `CATALOG_GIT_TAGS=true`, `CATALOG_GIT_BRANCH_FILES='master:VERSION'`), and
   the policy generator reads them. Install conversion waits for the
   follow-up ticket. When recipes become yamx YAML, each assignment maps to a
   key. This replaces round 1's "convert those 5 now".
8. `tools/catalog-contract/platforms.json` becomes
   `tools/catalog-contract/platforms.yaml`. It stays out of `catalog/`
   because AM hosts don't need it. Its readers are the collector and the page;
   no shell reads it (the e2e tests only copy it).
9. Every new YAML file (`retired-names.yaml`, the run outputs,
   `platforms.yaml`) uses the catalog grammar from `docs/catalog-format.md`,
   each with a schema `$defs` entry. Lists become maps: in `platforms.yaml`,
   `linux_words` maps each word to `true` and `architecture_words` maps each
   word to its processor; each retired name maps to `true`. No new YAML file
   is read by a shell.

### November 26, 2026: correction, item 3 superseded (Marek: yes)

The Evidence table is wrong about `recipe-url-policies.json` and
`appimage-policies.json`. They are not generated from `programs/`; they are
the only place the facts live. `bulk_recipe_urls.py` pulled each recipe's
URL rules out of its `curl | grep` pipeline, then replaced the pipeline with a
`catalog-yaml.am` call. `programs/aarch64/6502-emulator`, for example, keeps no
repository or rules. `source_sha256` only detects that a recipe changed since
its row was written. `scripts/25/measure.py` took it for proof of generation.
`appimage_policy_source.py` says outright that its JSON "is a source of truth".
Both compile into `modules/catalog-yaml-policy.am`, which hosts fetch.

Item 3 is replaced: each of the 1,569 rows (1,464 + 105) moves into its own
recipe as `CATALOG_*` assignments, kitty's identity lines plus the URL rules.
The generator reads the recipes, and both JSON files go. Install bodies don't
change. Until that lands, the JSON stays committed and unchanged, with no
interim YAML. This is [ticket 26](26-move-policy-rows-into-recipes.md),
rewritten.

### November 26, 2026: item 7 replaced (Marek: yes)

The Git scopes are derived from the recipes' existing Git selection lines,
with no new `CATALOG_GIT_*` assignments, and `git-sources.json` is deleted
([ticket 29](29-derive-git-sources-from-recipes.md)).

### November 26, 2026: items 5, 8 and 9 replaced (Marek: Q16)

`platforms.json` and the run outputs stay JSON
([ticket 31](31-platforms-and-run-outputs-as-yaml.md)). The catalog grammar
itself is to become a yamx profile (mareklangiewicz/yamx#22,
[ticket 33](33-read-the-catalog-with-yamx.md)), and `platforms.json` moves to
YAM(B) then. No new catalog-grammar files are added for collector inputs.
