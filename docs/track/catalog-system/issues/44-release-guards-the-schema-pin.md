# `release.py` guards the schema pin

Type: task
Label: implementation:task
Status: resolved
Blocked by: none

## Outcome

`release.py plan` and `ship` compare the collector's `schemas` input scope
with `CATALOG_SCHEMA_REVISION`. A change there refuses unless
`--repin-schemas` says the contract transition was reviewed; with it, `ship`
moves both pins before dispatching the catalog run. A ship can no longer
leave every catalog run refusing on `checkout differs from schemas input pin`.

## Why

Ticket 25, November 20, 2026: the step-1 ship changed `schemas/catalog/*`.
`release.py` repinned only `CATALOG_SCHEDULE_REVISION`, and catalog run
44777669942 refused until `CATALOG_SCHEMA_REVISION` was moved by hand. Long
tests cannot see this (they never read the live pins), and `plan` listed the
schema files among ordinary collection inputs. Retirement step 3 changes the
schemas again.

## Scope

- The scope list comes from `collection_interface.INPUT_SCOPES['schemas']`,
  raw, as `verify_checkout_inputs` compares it (no README exclusion).
- `--repin-schemas` with no schemas change refuses: the pin stays stable on
  unrelated changes (`docs/catalog-format-v3.md`).
- Tests in `tools/release/test_release.py` against scripted `gh` replies.

## Comments

## Answer — November 20, 2026

`decide` reads `CATALOG_SCHEMA_REVISION` and diffs it against HEAD over the
raw `schemas` scope. A non-empty diff without `--repin-schemas` is a refusal
naming the pin, the files and the flag; the flag without a diff is a refusal
too. With both, `ship` sets the schedule pin, then the schema pin, then
dispatches; a schemas change always dispatches, even one the schedule gate
ignores (a README under `tools/catalog-contract` still fails
`verify_checkout_inputs`). `plan` prints either `would repin
CATALOG_SCHEMA_REVISION A -> B` or that the pin stays.

Tests: `test_release.py` 29 OK (7 new). Mutants that drop the refusal (3
tests fail) or skip the dispatch for a gate-ignored schemas change (failed
none at first; a README test was added, now 1 fails) are caught. Run for
real on `22cffd611`: `plan` says both pins stay; `plan --repin-schemas`
refuses with nothing to repin.

November 20, 2026: shipped with Marek's approval as `a41a654ce` (Long tests 44814344503 on `ci/release-schema-pin`, Fast tests 44816128213 green; neither pin moved, no catalog run). The new `plan` was used for real in that ship; `ci/release-schema-pin` deleted.
