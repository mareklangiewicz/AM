# Author the catalog schema in YAML

Type: task
Label: implementation:task
Status: merged into 24
Triage: needs-triage
Blocked by: none

## Outcome

As decided in [Choose the schemas' form and editor wiring](10-choose-schema-form-and-wiring.md):
`schemas/catalog.schema.yaml` is the hand-written source of the catalog and
status contract, every kind under `$defs`, each field with a one-line
`description` written for ticket 13's test reader. `tools/catalog-contract/build.py`
reads it and generates the awk tables (`modules/catalog-contract-tables.am`) and
`definitions.json`/`.mjs`, byte-identical to today's for the same contract; the
generated `schemas/catalog/*.schema.json` are deleted, with their references in
tests and docs. The field prose in `docs/catalog-format-v3.md` and
`docs/catalog-status-v1.md` is removed as its descriptions land; the grammar and
reader obligations stay until ticket 09. Published documents do not change (the
`schema:` to `$schema:` switch is ticket 16's).

## Comments

November 25, 2026, from ticket 09: the grammar doc keeps E9 unchanged plus the
`$schema` first key; write it from 09's Answer.

Merged into [Cut over to the simplified catalog in one change](24-cut-over-to-the-simplified-catalog.md)
(November 25, 2026): this Outcome is part of its spec; steps that only bridge v3
and the new layout are dropped.
