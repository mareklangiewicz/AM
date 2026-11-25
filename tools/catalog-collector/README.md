# Catalog collector

The catalog is the `catalog/` directory on `main-marek`
([format](../../docs/catalog-format.md), [schema](../../schemas/catalog.schema.yaml)):
`apps.yaml`, one `repositories/<name>.yaml` per GitHub repository, and
`status/runs.yaml` and `status/statistics.yaml`. Hosts (`modules/catalog-yaml.am`)
and the catalog page read those files raw from GitHub, with no pins, refs or
snapshots between them and `main-marek`
([ticket 24](../../docs/track/catalog-simplification/issues/24-cut-over-to-the-simplified-catalog.md)).
The collector is the only writer of `catalog/`; Marek's commits never touch it.

## A collector run

`.github/workflows/catalog.yml` runs hourly (`17 * * * *`; GitHub fired it only
2 to 4 times a day in November 2026) and on dispatch, never two at once. It is
two commands of `catalog_run.py`:

- `collect` (read-only job) on a checkout of `main-marek`'s tip: reads
  `catalog/`, picks the repositories whose data is oldest (the newer of
  `observed_at` and `failed_at`; never-read first), reads one page of releases
  for each, and writes a candidate: the changed documents, `removed.json` and
  `run.json`.
- `publish` (write job, the same code): checks every candidate document with
  the host's reader, commits `catalog/` on top of `main-marek`'s tip and pushes
  with the job's `GITHUB_TOKEN`. A push rejected by a newer commit is redone on
  the new tip, up to 5 times. A candidate that fails the reader commits only its
  run summary, with `stop_reason: internal`.

Locally, against saved GitHub answers and a scratch remote:

```sh
python3 -B tools/catalog-collector/catalog_run.py collect --checkout . --output /tmp/candidate \
  --evidence /path/to/saved-responses --run-id 1 --attempt 1
python3 -B tools/catalog-collector/catalog_run.py publish --candidate /tmp/candidate \
  --remote /tmp/test-remote.git --scratch /tmp/publish --run-id 1 --attempt 1
```

Saved answers are `<repository id>-releases.json` plus `<repository id>-receipt.txt`.
Without `--evidence`, `collect` reads GitHub (`GH_TOKEN` if set).

Pause collection with `gh workflow disable catalog.yml`.

## What a run reads and writes

`documents.py` turns what was read into documents and their exact bytes, and
applies retention: the kept releases are the 8 newest tags, the newest stable
tag, the newest tag with a Linux download and the newest tag with an AppImage
for each processor type (`tools/catalog-contract/platforms.json`), with every
release under a kept tag. A release a read did not return stays with its
last-seen `observed_at`, unless the read reached the end of the release list.

`host_catalog.py` holds enrollment and the bounded GitHub reads:

- Enrollment is `collection-recipes.txt` (recipe declarations) plus
  `collection-apps.json` (catalog-only apps), at most 9,000 repositories.
  `source-names.json` gives each repository its file name; `active` names are
  unique and never reuse a `retired` one, and an enrolled repository without a
  name refuses the run.
- A batch reads at most 500 repositories (`CATALOG_BATCH_SIZE` repository
  variable to change it) within 750 requests (its Git reads take more than one
  each), a 100-request primary rate
  reserve, 512 MiB of response bytes, 16 MiB per response and 900 seconds.
  401/403/429 and the budgets stop the run (`stop_reason`); no redirects or
  retries.
- Named oversized repositories (`PAGE_SIZES`) ask for smaller pages.
- `git-sources.json` adds Git tags and branch files for a few recipes
  (`git_observations.py`).
- A repository's own failure (`not_found`, `too_large`, `invalid_response`,
  `transport`) adds `failed_at`/`failed_with` to its document and leaves its
  facts as they were; the next success removes them.

To retire a repository, take it out of enrollment and move its name from
`active` to `retired` in `source-names.json`, by hand: the next run deletes its
file (Git history keeps it). Nothing checks that no recipe still selects from
it any more (`retire_sources.py` did, and went with the v3 tools).

## Host runtime

`catalog-yaml.am` (with `catalog-reader.am`, `catalog-parser.am`,
`catalog-tables.am` and `catalog-yaml-policy.am`) reads
`https://raw.githubusercontent.com/<repo>/main-marek/catalog/…` once per file
per command, validates it, and hands the policy the facts it selects from.
Data older than 14 days warns and still selects (ticket 23). The installed
runtime needs shell, awk and curl only.

## Tests and shipping

```sh
python3 -B -m unittest discover -s tools/catalog-collector -p 'test_*.py'   # fast tier
python3 -B -m unittest discover -s tools/catalog-collector -p 'tree_*.py'   # whole-tree tier
```

`test_*.py` never reads the live recipe tree; `tree_*.py` walks every live
recipe or runs the real manager for each, so run it before an upstream merge
and on demand. `test_catalog_run.py` is one run end to end (a fixture checkout,
a bare origin, saved GitHub answers); `test_documents.py` is the writer's bytes.
`tools/fast-tests.sh` runs lint and every fast suite; Long tests
(`.github/workflows/long-tests.yml`) run both tiers and the container e2e on a
`ci/<name>` push.

`tools/release/release.py ship --ci <name>` moves `main-marek` once Long tests
passed on that commit (or on an ancestor that HEAD changes only under `docs/`
and `catalog/`). When HEAD changes `catalog/` or the contract, every `catalog/`
file at HEAD must pass HEAD's awk and node readers first. `release.py plan`
prints what `ship` would do and writes nothing; `release.py watch` follows the
runs. A push that changes only `catalog/` starts no Fast tests run.

Code outside this directory imports these modules:
`tools/recipe-conversion/convert.py` and through it
`tools/upstream-merge/merge.py`, `tools/recipe-reconstruction`'s tests,
`test/e2e/scenarios.py` and the one-time seed under
`docs/track/catalog-simplification/scripts/24/`. Find the current list with
`git grep -n "catalog-collector" -- ':!tools/catalog-collector' ':!docs'`.
Other scripts under `docs/track/` are frozen research records, not kept working.

## Recipe conversion helpers

`bulk_recipes.py` converts shared wrappers to recipe declarations with literal
URL predicates; `bulk_recipe_urls.py` keeps long installers' bodies while
replacing recognized release-selection pipelines (`recipe-url-policies.json`,
compiled by `recipe_policy_source.py`). Both preview by default and write only
with `--apply`. `tools/recipe-conversion/convert.py` uses them, and the
[upstream template recognizer](../recipe-reconstruction/README.md) inventories
a pinned upstream recipe tree:

```sh
python3 tools/recipe-reconstruction/reconstruct.py inventory --recipes-revision COMMIT --summary
```
