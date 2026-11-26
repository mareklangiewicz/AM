# Platforms and run outputs as YAML

Type: task
Label: implementation:task
Status: open
Triage: ready-for-agent
Blocked by: none

## Outcome

As decided in [Derive the collector's inputs](25-collector-inputs-from-catalog-and-recipes.md) (items 5, 8 and 9):
`tools/catalog-contract/platforms.json` becomes `platforms.yaml` in the
catalog grammar (`linux_words`: word → `true`; `architecture_words`: word →
processor), with a schema `$defs` entry, read by `documents.py` and the page
through `parse.mjs`; the e2e scenarios and `tools/catalog-browser/stage.py`
copy the new file. The guess rule is unchanged (its tests in
`test_catalog.mjs` and the collector pass as they are). The collector writes
`removed.yaml` and `run.yaml` in the catalog grammar instead of
`removed.json` and `run.json`, and its publish step reads them.
