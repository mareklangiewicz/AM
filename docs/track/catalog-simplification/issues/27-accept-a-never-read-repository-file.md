# Accept a never-read repository file

Type: task
Label: implementation:task
Status: claimed
Triage: ready-for-agent
Blocked by: none

## Outcome

As decided in [Derive the collector's inputs](25-collector-inputs-from-catalog-and-recipes.md) (item 6): a repository
document with `$schema`, `repository_id`, `repository` and `releases: {}`,
and no `observed_at` or `failed_at`, means "enrolled, not yet read".
`schemas/catalog.schema.yaml`, `modules/catalog-parser.am` and
`tools/catalog-contract/parse.mjs` accept it; `docs/catalog-format.md`'s
cross-field rules state it; the page and `am` show it as no data yet. Each
reader has a test that accepts the never-read file and still rejects a
never-collected file with releases or Git refs.
