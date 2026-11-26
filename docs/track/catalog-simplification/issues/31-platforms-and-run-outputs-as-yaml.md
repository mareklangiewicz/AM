# Platforms and run outputs as YAML

Type: task
Label: implementation:task
Status: resolved
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

## Answer

Not done now (Marek, November 26: Q16). Both stay JSON.

`platforms.json` in the catalog grammar would cost too much for a 0.4 KB file
that hosts never read:
- a new schema kind, which regenerates `schema.mjs` and `catalog-tables.am`,
  with a coordinated page redeploy;
- an async load replacing the page's static import;
- a changed guess: sorted keys would check the `aarch64` and `arm64` words
  before the `x86_64` words.

`removed.json` and `run.json` are a handoff between two steps of one Python
job, never committed.

`platforms.json` moves to YAM(B) (yamx) when the page first uses yamx: B fits
it as it is, with lowercase keys, ASCII words and ordered lists. That's
[ticket 33](33-read-the-catalog-with-yamx.md). The run outputs stay JSON.
