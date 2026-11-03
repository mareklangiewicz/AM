# Catalog YAML format 2 — experiment draft

Status: local design draft, not a deployed format. The prototype is captured on
the `research/yaml-reader-prototype` branch under `tools/catalog-yaml-prototype/`.
The production catalog and reader still use format 1. Detailed experiment results
are in [the findings](track/release-catalog/research/yaml-reader-experiment.md).

## Purpose and trust

Publish normalized GitHub release facts for clients to browse or select. The
catalog does not choose a version, asset, architecture, package type or definition
of latest. No raw API responses, derived JSON/TSV indexes, or catalog-body
hash/size ledger are published. Upstream asset digests are separate source facts.

Clients resolve one publication Git commit and use it for every file in that
command. GitHub HTTPS and the reviewed GitHub-hosted publication workflow are the
trust boundary. Structural validity does not prove workflow provenance or the
continued availability of an upstream download.

## Documents and identities

`repositories/ID.yaml` contains one numeric upstream repository identity.
`apps.yaml` maps AM names to those identities. Each document starts with `format`
and `schema`; the latter links to this document at an exact source commit:

```yaml
format: 2
schema: "https://raw.githubusercontent.com/OWNER/REPO/FULL_SOURCE_COMMIT/docs/catalog-format-v2.md"
```

The uppercase placeholders are illustrative. The actual reference uses an owner,
repository and 40-character lowercase hexadecimal source revision. Readers
recognize the format locally; they do not download the schema. A file's path ID
must agree with `repository_id`; the publisher checks app-map references.

Git publication commit time represents publication time. Source validation time
is explicit per repository and may be older than publication.

## Exact YAML subset

- UTF-8 without BOM; LF-delimited physical lines. Writers terminate the final
  line with LF; the trial reader also accepts an unterminated final line.
- Two spaces per nesting level; no tabs, blank lines, comments, trailing spaces,
  document markers, sequences, anchors, aliases, tags, directives or block scalars.
- Fixed schema keys are unquoted. All dynamic keys (release IDs, asset IDs, app
  names) are double-quoted, avoiding YAML implicit typing even for names like
  `"on"`, `"null"` or `"123"`.
- A mapping entry is `key:` followed by children on subsequent lines. An empty
  mapping is exactly `key: {}`; an implicit empty/null mapping is invalid.
- A scalar entry has exactly one space after the colon. Scalar forms are a
  double-quoted string, a canonical unsigned decimal integer, or `true`/`false`.
  No nulls, floats, signed values, leading zeroes or alternative boolean forms.
- Integers are bounded by 9223372036854775807. IDs are positive; sizes may be zero.
  Readers compare IDs as decimal text, without floating-point conversion.
- Numeric record keys are ascending by numeric ID; app keys are ascending by
  ASCII byte order. Fields follow the order specified below. Duplicate, unknown
  and out-of-order keys are rejected.
- All strings fit one physical line. The agreed escapes are `\"`, `\\`, `\n`,
  `\r`, `\t`. **Accepted extension:** `\N`, `\L`, `\P` represent
  Unicode U+0085/U+2028/U+2029. Literal Unicode line-break characters are rejected
  because YAML folding can change their values or adjacent whitespace. This
  extension was accepted by Marek after the round-trip experiment; it is
  currently implemented in the prototype only.
- Other ASCII/C1 control characters and U+FFFE/U+FFFF are not representable.
  Unsupported input fails source normalization; it must not be silently changed.
  Publisher validation enforces UTF-8 and YAML validity. The trial shell reader
  checks framing and structure but does not implement general UTF-8 validation.

Strings are never shell code. Consumers must not `source` or `eval` the data.
Resource limits apply independently of structural validity. The experiment's
32 MiB/file and 64 KiB/line limits are not approved production collection budgets.

## Repository fields

Fields occur in this order; `?` means omit if unavailable/inapplicable:

| Field | Type | Meaning |
| --- | --- | --- |
| format | integer | Exactly 2 |
| schema | string | Immutable description URL |
| repository_id | positive integer | Stable numeric upstream identity |
| repository | string | Readable owner/name |
| checked_at? | timestamp | Last successful complete release validation |
| check_status | string | `ok` or `failed` |
| check_reason? | string | Failure reason, only with `failed` |
| releases? | mapping | Quoted release IDs to release records |

Timestamps are quoted UTC `YYYY-MM-DDTHH:MM:SSZ`, with whole-second precision
and valid calendar dates. The trial supports years 1970–9999. There are no
duplicate epoch fields. Optional missing facts differ from empty strings.

A successful check requires `checked_at` and `releases`, and omits `check_reason`.
An empty successful history is `releases: {}`. A failed check retains the previous
complete observation and its check time, if any. With no successful observation,
both `checked_at` and `releases` are absent. The trial reason vocabulary is
`rate_limited`, `transport`, `invalid_response`, `collection_limit`; detailed
diagnostics remain in workflow logs, not arbitrary catalog error strings.

## Release and asset records

Release fields, in order:

| Field | Type | Meaning |
| --- | --- | --- |
| tag | string | Upstream tag |
| title? | string | Release name, omitted if unavailable |
| url | string | HTTPS release page URL |
| created_at? | timestamp | Upstream creation time when supplied |
| published_at | timestamp | Upstream publication time |
| updated_at? | timestamp | Upstream update time when supplied |
| prerelease | boolean | Upstream prerelease flag |
| source_zip_url? | string | HTTPS generated ZIP archive URL |
| source_tar_url? | string | HTTPS generated tar archive URL |
| assets | mapping | Quoted asset IDs to asset records; `{}` when empty |

Asset fields, in order: `name` (string), `url` (HTTPS string), `size` (integer),
`content_type` (string), `digest?` (upstream string). These are original upstream
facts; the catalog does not infer an architecture or select a preferred asset.
Names and content types can be actual empty strings; an unavailable digest is
omitted. Release notes, author profiles and unused response fields are omitted.

Collect all published release pages, including prereleases and excluding drafts.
No separate GitHub latest request. Explicit request/byte/runtime ceilings may
prevent completing a source; mark failure and retain the previous observation.
Reject detectable pagination inconsistencies such as duplicate release IDs.
The result is not a transactional snapshot across mutable upstream pages.

Assets are the lists embedded in release responses, without extra per-release
asset requests. Complete release pagination does not assert independently audited
asset completeness. Generated source archives are separate from uploaded assets.

## App map

After `format` and `schema`, the only root field is `apps`. Its quoted keys
match `[a-z0-9][a-z0-9_.+-]*`, and values are positive repository IDs:

```yaml
apps:
  "example": 123
  "example-beta": 123
```

No aliases are hardcoded into the reader. `apps: {}` is a valid empty map.

## Trial reader contract

`validate FILE`, `releases FILE`, `assets FILE RELEASE`, `apps FILE`, and
`get FILE KEY...`, and `rows FILE COLLECTION FIELD...` are implemented locally
by the prototype. ID/name enumeration
is one entry per line. Scalar lookup writes exact decoded bytes with no added
newline. Missing data returns status 3; invalid data/query/usage returns 2;
successful values including false, zero and empty strings return 0.

No output is emitted until the whole file validates. Quoting and escape decoding
are shared; recipes do not each implement another parser. Shell command
substitution removes trailing newlines, so redirect to preserve exact scalar bytes
when necessary. `rows` validates once and projects scalar fields for every record
in `releases` or `releases/ID/assets`. Output has one ID and TAB-separated
canonical YAML scalar tokens per LF-terminated row; string escapes remain
encoded, so embedded tabs/newlines do not break framing. A missing optional
field has an empty column; an actual empty string is the token `""`. This is
query output, not a separately published representation. A client can compare
quoted fixed-format timestamps and booleans in one awk pass, then look up the
chosen record. Repeated individual scalar invocations are not an efficient
large-history selection loop.

The reader supplies facts. Clients apply freshness policy: initially the existing
48-hour installation rule and explicit stale override, while browsing can display
older observations with status. Publication and exact source repin are separate
operations; this draft does not authorize deployment.
