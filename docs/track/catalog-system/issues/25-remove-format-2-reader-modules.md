# Remove the format-2 reader modules

Type: task
Label: implementation:task
Status: open
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
