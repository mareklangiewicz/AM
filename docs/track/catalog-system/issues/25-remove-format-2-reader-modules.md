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

November 16, 2026: Marek approved the wider scope ("retire format 2 from the
collector"). Import map read at `8c39bf0a7`; format 2 is in four layers, and
the two modules can only go last:

1. **Live path.** `host_catalog.collect(native_v3=False)` still builds a
   format-2 tree; `collection_interface.py` always passes `native_v3=True`.
   `validate --channel format-2` and the `format-2` channel of
   `incremental.py` are the other entry points.
2. **Shared helpers that are not format-2 specific** but live in format-2
   files: `writer.document` and `retention.observation` are imported by
   `contracts.py` (format 3); `yaml_publication` also carries `SAFE_LOADER`,
   `schema_url` and a re-exported `git`.
3. **Test fixtures are authored in format 2.** `fixture_v3.publish_local`
   turns saved format-2 documents into format 3 through
   `rehearse_pipeline.seed_source`; `fixture_appimages`, `fixture_recipes`,
   `fixture_manager` and `fixture_facts` feed it. `test_yaml_reader.py` is the
   helper 14 files import.
4. **One-off scripts**: 13 `qualify_*.py` and `rehearse_pipeline.py`, written
   for tickets 14 to 16, several comparing format 2 with format 3. Nothing
   imports the `qualify_*` files.

Proposed order, each step leaving the suite green:

- A. Move the shared helpers of layer 2 to a neutral module.
- B. Make `native_v3` the only behaviour of `collect`; drop the format-2
  channel and `validate --channel format-2`; port or retire the tests that
  drive the old path (most of `test_batch_collection.py`,
  `test_publication.py`, `test_large_batch_enrollment.py`).
- C. Save the fixtures as format-3 facts, so `seed_source` and format-2
  loading leave the test stack.
- D. Delete `yaml_publication.py`, `writer.py`, format-2 `retention.py`
  leftovers, the format-2 `qualify_*` scripts, `test_yaml_reader.py`,
  `test/e2e/test_reader_portability.py` and the two modules.

Step B changes what scheduled collection runs, so it is pushed alone with a
repin and one observed scheduled run before C and D. Nothing done yet.

November 16, 2026: step A done, smaller than planned. `SAFE_LOADER` now
lives in `contracts.py`; five test and fixture files import `git` from
`publication` instead of through `yaml_publication`; `writer.py` is described
as what it is, the YAML emitter both formats share, and stays.
`retention.observation` stays where it is until step D: moving it now makes
an import cycle (`retention` to `retention_v3` to `bounded` to `retention`).
`schema_url` belongs to the format-2 path and goes with step B. Fast tier:
221 tests pass.

November 16, 2026: step B sized, not started. About 25 tests call
`host_catalog.collect` without `native_v3` (`test_batch_collection.py`,
`test_large_batch_enrollment.py`, `test_catalog_only_enrollment.py`); they
cover batch selection, budgets and the rate reserve, which the format-3 path
shares, so each needs porting, not deleting. The published status format
also still names a `format-2` outcome (`test_pipeline_publication.py`,
`pipeline_publication.py`); removing that is a status-format change and is
not part of step B.
