# Accept a never-read repository file

Type: task
Label: implementation:task
Status: resolved
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

## Answer

The never-collected rule in `modules/catalog-parser.am` and
`tools/catalog-contract/parse.mjs` now reads "a never-collected repository has
no releases or Git refs". It no longer requires a failure, and
`docs/catalog-format.md` says so. The schema needed no change: it already
accepted `releases: {}` with no `observed_at` or `failed_at`. Tests:
- `examples/repository-never-read.yaml` is accepted by every reader: mawk,
  gawk, busybox awk, the page's JS and the schema.
- `bad-never-read-with-git.yaml` and `bad-never-collected-with-release.yaml`
  are refused with the new message.
- The host reader gives no fact rows for the never-read file
  (`test_host_facts`).
- The collector turns it into a valid first failure or first read
  (`test_documents`).

The page shows it as "Never collected" with no failure line; that's the same
branch it already had for a file without `observed_at`.

For [ticket 28](28-enroll-from-apps-yaml.md): hosts validate the catalog with
their installed `catalog-parser.am`, so this change must reach every host
(`am -s`) before the first never-read file is committed to `catalog/`. An older
parser refuses such a file.
