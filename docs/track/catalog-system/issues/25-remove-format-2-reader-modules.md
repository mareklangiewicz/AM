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

November 17, 2026: step B done.

- `host_catalog.collect(retained, evidence, *, batch_size, metrics,
  acquisitions, profile)` is the format-3 acquisition only: it takes the
  parent snapshot's per-source metadata (`Records(prior).metadata`), fills
  `acquisitions` and returns the report. The `revision`, `native_v3` and
  `incremental` parameters, the format-2 refresh, `candidate_tree`, the
  freshness-age metrics and `response_sha256` (format-2 only) are gone.
  `collection_interface.collect` is the only production caller.
- `validate --channel format-2` is gone, with its one test in
  `test_contracts.py`. The `format-2` channel of `incremental.py` stays: the
  fixtures still load saved format-2 documents through
  `rehearse_pipeline.seed_source` (step C), and `incremental.rules()` still
  hashes the two modules (step D).
- Tests ported, not deleted: `test_batch_collection.py` (15),
  `test_large_batch_enrollment.py` (now selects through
  `catalog-contract-reader.am` and the policy module with mawk, gawk and
  busybox awk), `test_catalog_only_enrollment.py`, one call in
  `test_git_observations.py`. Dropped: the freshness-age metrics test
  (format-2 metric) and the assertion that a failed source moves behind
  others in the next rotation: in format 3 the caller writes no document for
  a failed source, so it keeps its place (already recorded by the "live
  Wekan" test). Mutation check: sorting by id only makes the ordering test
  fail.
- `qualify_scheduling.py` deleted: a one-off ticket-14 script that drove the
  format-2 path.

November 17, 2026: step B follow-up. The first "Long tests" run on GitHub
(44071909464, ticket 34) failed the fast tier with three errors that the
targeted local runs had missed: `test_contracts` mocked `host.collect` with
the old `(tree, report)` shape, and `test_snapshot_canonicality` borrowed
format-2 fixtures from the rewritten batch helper (it now builds its own until
step D). Fixed in `585e01a69`; whole-tree tier and Debian and Fedora e2e passed
in that run. Step B sits on `ci/format-3-collection`; `main-marek` has not
moved. Pushing it needs a repin and one observed (dispatched) collection run
before steps C and D.

November 17, 2026: step B observed. `main-marek` moved to `87c025d48` (pushed
with Marek's approval, `CATALOG_SCHEDULE_REVISION` repinned to it). Dispatched
catalog run 44074650774 on it, the first collection through the format-3-only
`collect`, passed both jobs (acquire, publish); Fast tests 44074645397 passed
on the same commit. Steps C and D are unblocked.

November 20, 2026: step C done, as option A (Marek chose it over saving
generated format-3 files). `fixture_v3.repository` builds a source document
from a saved or synthetic releases response through `contracts.source`, the
projection collection uses; `fixture_v3.expanded` gives the Python oracle
(`reference_policies.select_cohort`) the releases a reader sees. Every
builder uses it: `fixture_recipes`, `fixture_appimages` (45 saved
responses; `history_complete` false for a full 30-per-page response or a
`/latest` singleton), `test_host_cutover` and the e2e `catalog_tree`, whose
tree is byte for byte the one the format-2 route produced.
`fixture_v3.publish_local` takes the documents as they are; `seed_source`
and `fixture_facts.merge_attempts` left the test stack (`624f6d15d`,
`3d8f153af`). Collector fast tier (236) and `tree_appimages` (105 subtests)
green. Left for step D: `rehearse_pipeline.seed_source` and its test,
`candidate_tree` as a format-2 parent in `test_contracts` and
`test_pipeline_publication`, `catalog-browser/review_snapshot.py`,
`schema_url`/`SCHEMA` (`yaml_publication`, `test_yaml_reader`) that
`publish_local` callers still pass.

November 20, 2026: step C shipped. `main-marek` moved to `4699d0381` (Marek
approved), `CATALOG_SCHEDULE_REVISION` repinned `fa1c00518 -> 4699d0381`.
Fast tests 44742679165 and dispatched catalog run 44742685442 passed on it;
`ci/format2-c` deleted. Found for step D: `tools/catalog-browser/review_snapshot.py`
(run by `catalog-pages.yml` on the `browser-review` branch only) decodes a
format-2 baseline `cbda9fb78` through `decode(..., 'format-2')` and
`rehearse_pipeline.seed_source`, so those cannot go until that step is
retired or rebuilt on a format-3 baseline; Marek to choose.

November 20, 2026: step D done locally, not shipped. `review_snapshot.py`
and its `browser-review` workflow step retired (Marek chose that over a
format-3 port; `b20e26e85`). Format-2 one-off scripts and
`rehearse_pipeline` deleted (`372885eee`); `qualify_status_scale` stays (it
only names the status format's `format-2` outcome, out of scope here).
Publication tests call `publish_tree` directly (`a75f594ea`). Then
`198055bcd`: `yaml_publication.py`, `retention.py`, `collect_files`,
the `format-2` channel, `select_local`, `test_yaml_reader.py`,
`test_retention.py`, `test_observation_defaults.py`, the non-contract
`validate_wire` branch and both modules are gone; `observation` moved to
`retention_v3`; `test_reader_portability` runs its forbidden-code-point
cases against `catalog-contract-reader.am` (a lax reader fails 36 subtests).
Collector fast tier 178 OK (58 fewer: 31 deleted tests, 27 duplicate runs of
`test_yaml_reader.Experiment` through imports); other suites OK. Not run:
whole-tree tier and container e2e (Long tests on the `ci/` branch). Left:
`docs/catalog-format-v2.md` (spec of the frozen ref; not in this ticket's
list) and the status format's `format-2` outcome.

November 20, 2026: Marek asked to retire format 2 fully. `0a36851a8`
deletes `docs/catalog-format-v2.md` and makes the status summary's
`compatibility_publication` optional (still written). It cannot simply go:
all 64 retained summaries on `catalog-status-v1` (`e50cc8de1`) carry it,
every run validates them through `Snapshot('status-1')`, and the deployed
browser at mareklangiewicz.pl/AM requires it (its `definitions.mjs`, read
November 20). Remaining, in order, each a ship:

1. (done locally) optional, still written; test
   `test_retiring_compatibility_publication_is_optional_in_summaries`.
2. After Marek redeploys the browser from a `main-marek` that has step 1:
   stop writing it in `pipeline_publication.summary`; drop the README note.
3. When no summary on `catalog-status-v1` has it (64 hourly runs after
   step 2's ship; check the live ref first): remove the property from
   `build.py`, regenerate, flip the test to expect refusal, close this ticket.

November 20, 2026: step D and retirement step 1 shipped. Long tests on
`ci/format2-d` first failed in both e2e containers: the tested-source
fingerprint lists in `test/e2e/scenarios.py` and `termux_scenarios.py` still
named the deleted `retention.py` (fixed in `cb854845b`, now `retention_v3.py`;
local Debian 21 and Termux 14 OK). Rerun 44774424436 green. `main-marek` moved
to `cb854845b` (Marek approved), `CATALOG_SCHEDULE_REVISION` repinned
`4699d0381 -> cb854845b`; Fast tests 44777663693 passed, but catalog run
44777669942 refused with `checkout differs from schemas input pin`: step 1
edits `schemas/catalog/*` (one `required` entry each), and
`CATALOG_SCHEMA_REVISION` was still `040614f86`. `release.py` repins only the
schedule pin. With Marek's approval `CATALOG_SCHEMA_REVISION` was set to
`cb854845b` and dispatched run 44779574439 passed: `release-catalog-v3` now
binds every input including `schemas` to `cb854845b`; all 64 summaries on
`catalog-status-v1` (run 44779574439 among them) still carry
`compatibility_publication`. `ci/format2-d` deleted. Gaps found: `release.py
plan` does not flag a change under the `schemas` input scope as needing a
`CATALOG_SCHEMA_REVISION` transition, and Long tests cannot catch it (they
never see the live pins). Next: Marek redeploys the browser, then step 2.
