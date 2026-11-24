# Choose the schemas' form and editor wiring

Type: grilling
Label: wayfinder:grilling
Status: resolved
Blocked by: 03, 04

## Question

Where do the YAML JSON Schemas live, what are their `$id` URLs (pinned or
branch), how does each catalog file name its schema, and what happens to the
prose specs (`docs/catalog-format-v3.md`, `docs/catalog-status-v1.md`)?

## Answer — November 24, 2026

Marek's answers to two grilling rounds.

Evidence ([scripts/10/](../scripts/10/), `make_fixture.py`, probed with `gndx nvim
lspprobe --ask='hover:16:6' <file>` at main-marek `0a3dba867`, yamlls 2.0.0):

- The catalog grammar forbids comments (`docs/catalog-format-v3.md`, Grammar),
  so ticket 03's first-line modeline is not available to catalog files.
- yamlls takes the schema from an inline first key `$schema:` (relative path and
  raw GitHub URL both validate, complete and hover), follows a cross-file `$ref`
  between YAML schemas, and honors a `#/$defs/<kind>` fragment in `$schema`
  (control: the same file without the fragment, against a schema whose root
  accepts anything, gets 0 diagnostics; with it, the 2 planted errors).
- A closed schema must list `$schema` itself, or yamlls reports "Property
  $schema is not allowed".
- Today `build.py` (a Python DSL) generates 8 JSON schemas, each with a full copy
  of every `$defs`, plus `definitions.json`/`.mjs` and the awk tables. Every
  document's `schema:` names the prose spec at a commit, which the host checks
  against `inputs.schemas` (`modules/catalog-yaml.am`); `.vscode/settings.json`
  associates schemas by path, which Marek's Neovim does not read.

Decisions:

- **The source is one hand-written YAML schema**, `schemas/catalog.schema.yaml`,
  every kind (catalog and status) under `$defs`. `build.py` becomes a generator
  that reads it and writes the awk tables and `definitions.mjs`; the generated
  JSON schemas are deleted. Field order in `properties` is the canonical order.
- **A document names its schema with `$schema:`**, its first key, replacing
  `schema:`, pointing to the YAML schema with the kind as fragment
  (`#/$defs/repository`). Readers accept the `$` key; the schema lists it.
- **A relative path, no hash**, once the catalog is inside `main-marek`
  (ticket 16): `../../schemas/catalog.schema.yaml#/$defs/repository` resolves in
  a checkout and over raw GitHub at whatever commit the reader pinned. The
  schema-URL pin leaves ticket 05's scope.
- **No `$id`**: relative references resolve against where the schema was read.
- **Prose specs**: each field's meaning moves into schema `description`s (hover
  shows it); the field prose of `catalog-format-v3.md` and
  `catalog-status-v1.md` is removed; only what JSON Schema cannot say (byte
  grammar, canonical order, reader obligations) stays as a short doc, shaped by
  ticket 09.
- **`.vscode/settings.json` is deleted**: every file names its own schema.

Implementation: [Author the catalog schema in YAML](20-author-catalog-schema-in-yaml.md)
(unblocked, nothing published changes) and, in
[ticket 16](16-move-catalog-into-main-marek.md), the switch to relative
`$schema:` and deleting `.vscode/settings.json`.
