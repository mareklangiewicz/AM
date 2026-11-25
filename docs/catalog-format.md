# Catalog format

The catalog lives in `catalog/` on `main-marek`:

- `apps.yaml`: every app, its repository file and its recipe labels;
- `repositories/<name>.yaml`: what GitHub lists for one repository;
- `status/runs.yaml`: the last 64 collector runs;
- `status/statistics.yaml`: how old the data is.

[`schemas/catalog.schema.yaml`](../schemas/catalog.schema.yaml) defines every
kind and field and describes each one; editors show those descriptions on hover.
This page covers what the schema cannot say. The host's reader
(`modules/catalog-parser.am`) and the page's reader
(`tools/catalog-contract/parse.mjs`) enforce all of it, and the worked examples in
`tools/catalog-contract/examples/` show each rule.

## Grammar

A document is a small, fixed subset of YAML, so a reader in POSIX awk can check
every byte:

- Its first line is `$schema: "<path>#/$defs/<kind>"`. That path is relative
  to the document, and the fragment names its kind.
- Only mappings. Each line is `key: value` or `key:` with deeper lines below.
  Indentation is two spaces per level, at most 12 levels.
- Field names are bare (`[a-z][a-z0-9_]*`) and appear in the schema's order.
  Table keys (app names, IDs, run keys, Git ref names, file paths) are quoted
  strings. Numeric keys are in numeric order, run keys by run then attempt,
  and other keys in byte order.
- An empty mapping is `{}`. Values are a quoted string, `true`, `false`, or a
  decimal integer from 0 to 2^63-1 with no sign and no leading zero.
- Strings are UTF-8 in double quotes. The only escapes are `\"`, `\\`, `\n`,
  `\r`, `\t`, `\N` (U+0085), `\L` (U+2028) and `\P` (U+2029). Raw control
  characters, C1 controls, U+2028, U+2029, U+FFFE and U+FFFF are refused.
- Times are real UTC calendar times (no February 30), which the schema's
  pattern alone cannot say.
- No comments, blank lines, trailing spaces or duplicate keys. The file ends
  with one newline. A line has at most 64 KiB, except a Git file's `content`.

## Cross-field rules

A repository document:

- has `observed_at` and `history_complete` together, or neither (never
  collected);
- has `failed_at` and `failed_with` together. A never-collected repository
  has its failure and nothing else: no releases, no Git refs. When both
  times are present, `failed_at` is later than `observed_at`;
- gives a release its own `observed_at` only when it is older than the
  repository's;
- has `git_scope` and `git_refs` together. Every tag ref has a `position`, and
  positions run 0, 1, … with no gaps; tags appear only when `git_scope.tags` is
  true, and `tags_history_complete` is true only then. Branch refs have no
  position, at most 4 per repository. Ref names follow Git's rules, and file
  paths have no `.` or `..` segment and at most 1 KiB, content at most 1 MiB.

A run has `succeeded + failed ≤ selected ≤ enrolled`.

Writers also keep what readers don't check: retention (each repository's 8
newest tags, its newest stable tag and its newest tag with a Linux download),
URLs stored only when they differ from the derived ones, and a `title` only
when it differs from the tag.
