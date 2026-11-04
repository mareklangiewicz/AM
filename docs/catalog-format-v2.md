# Catalog YAML format 2 — experiment draft

Status: local design draft, not a deployed format. The revised retained-observation prototype is on
`research/yaml-observation-default` under `tools/catalog-yaml-prototype/`.
Earlier reader/resource branches describe the superseded full-history model.
The production catalog and reader still use format 1. Detailed experiment results
are in [the findings](track/release-catalog/research/yaml-reader-experiment.md).
The [shared observation default](track/release-catalog/research/yaml-shared-observation-default.md)
records the latest agreed encoding and Git-history measurements.

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

Git publication commit time represents publication time. Repository collection
metadata describes collection scope and timing; each retained release has an
effective observation time, using a shared default or explicit override.
Neither collection nor publication time proves
that an untouched release was reobserved.

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
| collection | mapping | Most recent attempt for this repository |
| last_success? | mapping | Most recent successfully completed requested scope |
| observed_at? | timestamp | Shared default release observation time |
| releases? | mapping | Retained release records, merged across successful collections |

`collection` fields in order: `attempted_at` (timestamp), `page_size` (integer
1–100), `page_limit` (positive integer or quoted `"all"`), `reconcile`
(boolean; true requires explicit `"all"`), `status` (`"ok"` or
`"failed"`), `reason?` (string required only on failure). Reasons are
`rate_limited`, `transport`, `invalid_response`, `collection_limit`; arbitrary
diagnostics stay in logs. Source subsets are validated against configured numeric
identities at command entry; an unselected repository's file is unchanged.

`last_success` fields in order: `completed_at` (timestamp), `page_size` (integer
1–100), `page_limit` (positive integer or quoted `"all"`), `reconcile`
(boolean), `pages_fetched`
(positive integer), `history_complete` (boolean). These describe that successful
collection, not the total retained history. A finite scope starts at page 1 and
completes on its page limit or an earlier end of pagination. With finite limits,
`pages_fetched <= page_limit`; stopping below the limit requires
`history_complete: true`. `"all"` succeeds only with `history_complete: true`.
An empty response still counts as one fetched page. Even a finite limit can reach
the end of history; `history_complete` reports that fact independently of intent.

`last_success`, repository `observed_at` and `releases` are either all present or
all absent, including a successful empty retained set. A successful
attempt requires all three, matching page size/limit/reconcile between the attempt and success,
and no reason. With no successful collection yet, a failure omits all three. Later
failures preserve all three exactly, including overrides and omitted observations;
only current attempt metadata changes. Each repository commits staged changes
atomically after the entire requested scope and merged catalog pass validation
and resource budgets. Other successful sources need not roll back if one fails.
An unattempted source is left unchanged; aggregate exhaustion must be reported
for requested sources that were not attempted, without inventing an attempt time.

Timestamps are quoted UTC `YYYY-MM-DDTHH:MM:SSZ`, whole-second precision, valid
calendar dates, years 1970–9999 in the trial. No duplicate epoch fields. Completion
must not precede attempt time on success. Every release observation must be no
later than the last successful completion time. The shared default obeys the same
bound, even when every release has an override or the retained set is empty.
Failed-attempt timestamps do not
refresh the previous observation. Clock regressions that invalidate these
relationships fail the attempt rather than minting misleading freshness.

A successful empty fetch retains prior records. `releases: {}` means the retained
set is empty (for example, an initially empty repository), not that a partial
fetch proved every previously observed release absent.

## Release and asset records

Release fields, in order:

| Field | Type | Meaning |
| --- | --- | --- |
| observed_at? | timestamp | Override of the shared observation default; omit when equal |
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

## Requested collection and retention

Collection parameters are a configured source subset (default all), page size
1–100 (default 100), and page limit as a positive count or `all` (default 1).
Scheduled collection defaults to all configured sources, one page of 100
published releases, including prereleases and excluding drafts. Manual runs can
request other subsets, page sizes and page limits. There is no separate GitHub
latest request, and page order is not a client selection guarantee.

Explicit request, response-byte, total-byte and time budgets apply independently
of requested scope, even with `all`. Completing the limited requested scope is
success despite unvisited pages. Hitting a safety budget before completing it is
failure. Reject duplicate release IDs across fetched pages, malformed data and
detectable pagination inconsistencies. A failure after one good page commits no
staged release updates and advances no retained timestamps. Do not label a
budget-truncated `all` request as a successful limited request.

Merge fetched releases by numeric release ID into retained records. Replace a
fetched release's normalized facts and complete embedded-asset mapping with its
new response values, removing optional fields/assets no longer supplied for that
release. Preserve unfetched facts and effective observation times. A release's
effective `observed_at` is the
UTC time the response containing it was received (after the body was acquired),
not the attempt start, normalization completion or publication time. Commit it
only if the requested scope succeeds. An unchanged release included in a fresh
response is reobserved; mere absence, a 304 without a release body, or reuse of
cached facts cannot advance `observed_at`. Drafts are not merged as published
release facts. Selection and freshness use retained facts, not upstream page
position or recent collection status.

The repository-level `observed_at` supplies the shared default. A release uses
its own `observed_at` override when present, otherwise the shared timestamp.
Writers omit overrides equal to the default; the strict trial reader rejects
redundant equal overrides. Before changing the default, materialize the old
effective timestamp for every previously implicit retained release that was not
fetched. Then replace fetched records, retaining each page's actual receipt
timestamp, and omit only observations equal to the new default. All of these
changes stage and commit atomically; failure preserves the previous default and
release representation exactly. A new default never refreshes untouched records.

The local prototype chooses the final fetched page's receipt time as the new
shared default after scope success, including an empty page. Earlier pages use
explicit overrides when their receipt times differ. An empty fetch can therefore
materialize old implicit records without changing their effective times; it does
not refresh them. This deterministic writer choice is independent of completion
or publication timestamps, and does not claim every retained release was observed
on the final page.

Absence from a partial fetch never deletes a release. Full-history absence is
not a transactional deletion proof. The reconciliation policy is specified in
[the retention revision](track/release-catalog/research/yaml-retention-revision.md);
default retention applies even after full history; explicit `reconcile: true`
removes absent IDs only after a successful `"all"` scope. The last-success flag
records whether reconciliation was requested. A finite scope with reconciliation
is rejected before acquisition, even if it could reach EOF. Successful empty full
reconciliation removes all retained releases; any failure rolls back deletions as
well as updates. No eviction may silently bound
retained size: if the staged merged document exceeds its limit, fail and retain
the previous observation. Catalog size, line length, client memory and spool
output remain independently bounded; one-page acquisition does not bound the
size of an accumulated retained catalog.

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
successful values including false, zero and empty strings return 0. A release
`get ... observed_at` and `rows releases observed_at` return the effective
observation timestamp, resolving the shared default even when no release override
is stored. A missing release still returns 3; optional upstream fields retain
their ordinary missing-field behavior. `get observed_at` returns the shared default.

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
48-hour installation rule and explicit stale override, measured against the
selected release's `observed_at`. A recently collected repository or newly
published catalog cannot make an older untouched release fresh. Clients can
select an older stable release directly from the current catalog; stale policy
still applies to that record. Browsing can display older observations with status. Publication and exact source repin are separate
operations; this draft does not authorize deployment.
