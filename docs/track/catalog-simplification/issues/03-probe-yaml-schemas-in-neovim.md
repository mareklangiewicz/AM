# Probe YAML-authored JSON Schemas in Marek's Neovim

Type: task
Label: wayfinder:task
Status: resolved
Blocked by: none

## Question

Does Marek's Neovim (yaml-language-server from mason, SchemaStore.nvim) validate,
complete and hover a catalog YAML file against a JSON Schema written as YAML,
selected by a first-line `# yaml-language-server: $schema=<url-or-path>` comment?
Check a relative path and a raw GitHub URL. Record what works, with the exact
files used, in an isolated fixture outside Marek's live config.

## Answer — November 24, 2026

Yes, both ways. A JSON Schema written as YAML and named by a first-line
`# yaml-language-server: $schema=…` modeline validates, completes and hovers in
Marek's Neovim. That works with a path relative to the YAML file
(`./repository.schema.yaml`) and with a raw GitHub URL pinned to a commit.

Fixture: [scripts/03/](../scripts/03/). `make_fixture.py` converts
`schemas/catalog/repository.schema.json` (HEAD `c0c2192fe`) to
`repository.schema.yaml`, adding a YAML comment and two descriptions (`tag`,
asset `size`; the JSON schema has none). It writes `local.yaml`
(`repositories/aether.yaml` from `origin/release-catalog-v3` at `a8922b396`),
`local-invalid.yaml` with two planted errors (a string `size`, an unknown
top-level key `bogus`), and `remote.yaml` / `remote-invalid.yaml`, which name the
schema at
`https://raw.githubusercontent.com/mareklangiewicz/AM/3dfbc36a7…/docs/track/catalog-simplification/scripts/03/repository.schema.yaml`.
Commit `3dfbc36a7` was pushed to `origin` `ci/yamlls-probe` so that URL resolves
(HTTP 200, `text/plain`).

Probe: `gndx nvim lspprobe --ask='hover:16:6;hover:30:10;completion:16:5' <file>`,
which starts a fresh headless nvim with Marek's real config, run from the AM
checkout. Server: yamlls 2.0.0 from mason.

| file | diagnostics | hover on `tag` | completion at a release key |
|---|---|---|---|
| local.yaml | 0 | (asked at 15:6) the added description, "Source: repository.schema.yaml" (file URI) | not asked |
| local-invalid.yaml | 2: `Incorrect type. Expected "integer".` (30:15), `Property bogus is not allowed.` (4:1) | same | `observed_at`, `tag`, `release` |
| remote.yaml | 0 | (asked at 16:6, which is `title` here: the schema title only, the source is the raw URL) | `observed_at`, `title` |
| remote-invalid.yaml | the same 2 | the added description; the source is the raw URL | `observed_at`, `tag`, `release` |

A comment and draft 2020-12 in the YAML schema caused no errors. yamlls
2.0.0 parses a schema as YAML when its URL path ends in `.yaml` or `.yml`
(`loadSchema` in `out/src/languageservice/services/yamlSchemaService.js`). A
YAML schema therefore needs that extension, and a raw GitHub URL keeps it.

Correcting this ticket's premise: SchemaStore.nvim is installed for LazyVim's
`lang.json` extra, but `lang.yaml` is not enabled in myvi (`lazyvim.json`).
yamlls therefore runs on nvim-lspconfig's default `lsp/yamlls.lua`, with yamlls's
own built-in schemaStore lookup. Neither matters for modelines. A catalog file
needs no editor configuration beyond its first line.

Not checked: a `$ref` from one YAML schema to another file (relevant to ticket
10 if the schemas share `$defs`), and a branch URL (`…/main-marek/…`) instead
of a commit.
