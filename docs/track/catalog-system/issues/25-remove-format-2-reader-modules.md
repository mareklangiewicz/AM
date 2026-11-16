# Remove the format-2 reader modules

Type: task
Label: implementation:task
Status: open
Triage: needs-info
Blocked by: none

## Outcome

`modules/catalog-yaml-reader.am` and `modules/catalog-yaml-parser.am` are gone
from the repo, with the tests that exist only for them, and the remaining
suites pass.

## Why

The manager deletes both modules from `/opt/am/modules` on sync; no client
reads format 2. Decided in
[ticket 24](24-simplify-and-unify-catalog-process.md#answer--november-16-2026).

## Scope

Four places still name them (`grep`, November 16, 2026, at `4bafdb6be`):

- `tools/catalog-collector/incremental.py` line 25, a list of module paths;
- `tools/catalog-collector/wire_validation.py` line 19, the non-contract parser
  branch;
- `tools/catalog-collector/qualify_selections.py` line 70, an old-facts
  comparison;
- `test/e2e/test_reader_portability.py`, which tests the reader itself.

For each, decide whether the code path is format-2 only (delete it) or needs
the format-3 module instead. `tools/catalog-collector/test_yaml_reader.py` and
`test_large_batch_enrollment.py` also reference them.

## Comments

November 16, 2026 (claimed, then released): the premise "only collector tests
use them" is wrong, so the two modules cannot be deleted by themselves.
Read at `479574930`:

- `wire_validation.validate_wire` without `contract=True` runs
  `catalog-yaml-parser.am`; `yaml_publication.decode_document` calls it, and
  `incremental.decode` uses that for the `format-2` channel.
- `host_catalog.collect` still has both paths: `native_v3` returns early, the
  other builds a format-2 tree with `yaml_publication.candidate_tree`.
  `collection_interface validate` still accepts `--channel format-2`.
- `incremental.rules()` hashes both module files into the validation rule id.
- `test_yaml_reader.py` is also a shared helper: 14 tests and fixtures import
  `repository`, `SCHEMA`, `Experiment` or `document` from it.
- About 30 files in `tools/catalog-collector` mention format 2
  (`grep -l "yaml_publication\|format-2"`).

So the real change is "retire format 2 from the collector": `writer.py`,
`yaml_publication.py`, the `format-2` channel, the non-`native_v3` path of
`collect`, the `qualify_*` and rehearsal scripts that compare against format
2, and their tests. That touches the live collection path and needs Marek's
go-ahead as a scope, not as a two-file deletion. Nothing was changed.
