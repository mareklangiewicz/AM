# Decide which commit pins are needed

Type: grilling
Label: wayfinder:grilling
Status: resolved
Blocked by: 01, 04

## Question

Which commit hashes in the catalog and status (schema URLs, `inputs`, recipe,
rules and module bindings in provenance, input/output catalog per source) have
a clear benefit once the catalog is a directory of `main-marek`, and how is each
remaining one inherited down the structure instead of repeated?

## Answer — November 25, 2026

Marek's answers to two grilling rounds: store no commit hash unless it is really
necessary, and none is, once the catalog lives in `main-marek` (ticket 16).
Pins P1–P17 are ticket 01's inventory rows.

Dropped from catalog and status data:

- `inputs.source`, `.policy`, `.recipes`, `.rules` (P2–P5; always the run's
  code commit) and the summary's five input pins (P11). Which code wrote a
  catalog commit is its Git ancestry (with ticket 17's rebase-and-retry, code
  commits in between show in `git log`); `producer` keeps only `id` and
  `attempt`, which link to the run.
- `inputs.schemas` and `status.yaml schemas` (P6, P16); the schema URL (P1) is
  already replaced by ticket 10's relative `$schema:`.
- Provenance `recipe.commit`, `recipe.blob`, `evidence.rules` and every
  dependency `commit` (P8–P10), templates included: content is identified by
  `recipe_sha256` and each dependency's `sha256`, which the reuse check
  compares; the review link uses the catalog commit the reader pinned.
- `input_catalog`/`input_catalog_state`, `output_catalog`, `freshness.catalog`,
  `publication.commit` and `last_confirmed_publication` (P12–P15): the run's own
  commit or its Git parent.

Dropped from the workflow: both repo variables. `CATALOG_SCHEDULE_REVISION`
goes: `release.py` already refuses untested code on `main-marek`, and a bad
collector fails its own validation before committing, so scheduled runs
collect at HEAD. `CATALOG_SCHEMA_REVISION` goes with `release.py
--repin-schemas`; `release.py` keeps, as a pre-push check, its refusal to ship a
schema change while the live catalog fails HEAD's contract.

Kept, none of them our commit pins: upstream Git facts (refs' `commit`, files'
`blob`), content hashes (`sha256pre`, `recipe_sha256`, dependency `sha256`),
the run `id`/`attempt`, and the commit a reader resolves at read time (host per
command, page per tab), never stored.

Implementation: [Drop the commit pins and pin variables](21-drop-commit-pins-and-pin-variables.md),
blocked by ticket 16.

## Comments

November 23, 2026, from ticket 04: catalog and code share one `main-marek`
commit, but `catalog.yaml`'s `inputs` record the code commit the collector ran
at, an ancestor of the catalog commit, not the same one. Decide whether that
pin is still needed.

November 24, 2026, from ticket 10: the schema URL pin is decided there (a
relative `$schema:` path, no hash, once the catalog is in `main-marek`). Left
for this ticket: whether `inputs.schemas` and `CATALOG_SCHEMA_REVISION` are
still needed, given that a catalog commit's `schemas/` can be newer than the
contract the collector validated against.
