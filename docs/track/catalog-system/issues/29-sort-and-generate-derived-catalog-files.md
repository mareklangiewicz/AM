# Sort the fork-side catalog files and generate the derived ones

Type: task
Label: implementation:task
Status: open
Blocked by: none

## Outcome

Each of the five files an upstream merge rewrites is classified as source of
truth, derived, or unused. Derived files are generated when the collector
runs and are no longer committed; unused ones are deleted. `merge.py apply`
rewrites only what remains.

## Why

One merge rewrites about 380,000 committed lines in these files. Rule decided
in [ticket 24](24-simplify-and-unify-catalog-process.md#answer--november-16-2026):
commit only what is a source of truth or what a client fetches from the
branch.

## Scope

What is known (`grep` and `wc -l`, November 16, 2026, at `4bafdb6be`):

| File | Lines | Known |
| --- | --- | --- |
| `tools/catalog-collector/recipe-url-policies.json` | 249,234 | Holds the verified source identities re-conversion reads back (`policy_identities`), so at least partly a source of truth. |
| `modules/catalog-yaml-policy.am` | 86,199 | Fetched by hosts through `am -s`; stays committed unless it can ship with the published catalog. |
| `tools/catalog-collector/collection-apps.json` | 43,082 | Read by `bulk_enrollment.py`, `host_catalog.py`, `collection_interface.py`. |
| `tools/catalog-collector/collection-recipes.txt` | 55 | Read by `collection_interface.py`, `host_catalog.py`. |
| `tools/catalog-collector/unavailable-github-recipes.json` | 5 | Read only by `merge.py` and tests; likely unused. |

- Start with the classification and put it to Marek before removing anything
  from Git.
- A generated file must be produced inside the scheduled collection run
  without lengthening it noticeably; measure.
- This changes what `CATALOG_SCHEDULE_REVISION` reviews; read
  [ticket 22](22-keep-collection-running-across-doc-pushes.md) first.

## Comments
