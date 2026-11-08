# Public YAML contracts and revision consistency

Design selected November 7, 2026 under Marek's explicit “you decide” delegation.
Owner: [Choose public YAML contracts and revision consistency](issues/03-choose-public-yaml-contracts-and-revision-consistency.md).
This is the target contract sketch, not an implemented schema or migration.

Recovery amendment, November 7, 2026: Marek explicitly accepted redoing unfinished
work after runner loss and final-summary-only public health, with no public start
record. There is no separate checkpoint store or cross-run acquisition recovery
requirement.
See the [current recovery baseline](progress-and-scheduling-decision.md#current-accepted-baseline--november-7-2026).

## Two publication channels

Keep immutable release snapshots separate from operational status snapshots.
Initially use a new `release-catalog-v3` ref for format 3 and `catalog-status-v1`
for status format 1. These are target names, not refs to create now. Leave the
deployed `release-catalog` format-2 channel unchanged during compatibility work.
Both new channels use exact-parent publication. The resolved
[storage decision](issues/05-choose-scalable-snapshot-and-history-storage.md#answer--november-8-2026)
and [final targets](issues/10-agree-system-acceptance-and-implementation-roadmap.md#answer--november-8-2026)
own Git/history policy; checkpoint infrastructure is not required.

A client resolves each needed ref once to a full commit, C for catalog and S for
status, then reads only paths at that commit. Catalog-only clients need no status
request. The browser defaults to C and lazy repository reads. It resolves S only
for health/contextual attempt information; status failure cannot invalidate
otherwise valid catalog facts. No generated app index is introduced.

Status may advance after a failed acquisition, validation or publication while
C remains unchanged. This independent failure reporting is the reason for two
channels. Putting health into the release tree would couple visibility of failure
to publication of new release facts and break the current whitelist.

## Document boundaries

| Channel | Paths | Responsibility |
| --- | --- | --- |
| Catalog C | `catalog.yaml` | Contract/source/policy/schema pins and collection-producing run identity. No enclosing commit hash. |
| Catalog C | `apps.yaml` | AM names → explicit `repositories/<name>.yaml` references. |
| Catalog C | `repositories/<name>.yaml` | One verified numeric GitHub source and retained release/asset observations. |
| Catalog C | `provenance.yaml` | Revision-bound app/architecture recipe bindings and classification evidence, when available. Unknown classifications remain explicit. |
| Status S | `status.yaml` | Last reported run and publication confirmation known to that report; links to retained final summaries. Never an assertion about the latest attempt. |
| Status S | `runs/<run-id>/summary.yaml` | Final reported outcome, run inputs, original timestamps, explicit catalog publication result and investigation links. No start record or intermediate updates. |
| Status S | `runs/<run-id>/sources/<name>.yaml` | Bounded final per-source evidence when available; absence alone proves nothing. No continuous progress feed. |
| Status S | `statistics.yaml` | Optional bounded aggregates with measurement times and gaps. |

Each document begins with `format`, `schema`, `kind`, in that order. Catalog kinds
use format 3; status kinds use format 1. `schema` remains an immutable Markdown
contract URL, preserving its meaning. Kinds distinguish document roles within
their own version family. Versions are recognized locally; readers never fetch
schemas to decide whether untrusted input is acceptable.

`catalog.yaml` binds exact source, collection-policy, recipe-provenance input and
schema-set revisions. Policies at different source commits need distinct pins;
do not pretend all inputs came from the collector checkout. Document role and
field order, required/optional fields and limits will be written in the executable
contract slice after the health/provenance decisions supply their semantics.
This table fixes boundaries, not speculative metric/classification fields.

## Revision rules and publication races

The enclosing commit C is the catalog identity supplied by resolution or a shared
link, never a self-reference in `catalog.yaml`. Source/recipe/policy pins refer
to other immutable inputs. Keep source collection time, release observation time,
attempt times and publication time distinct; Git commit publication metadata
does not advance an observation. Preserve ADR 0002 effective observation times.

Every run summary binds its full input catalog commit, source/policy revisions,
requested scope identity and run identity. A successful publication result binds
the exact resulting catalog commit only after remote acceptance is confirmed.
Creating a local candidate is not success. The catalog descriptor can name its
producer run before publication; the later run summary can point to C without
either document embedding its own enclosing commit.

At S, `last confirmed publication` means exactly that: confirmation known to that
status snapshot, not an atomic assertion about the current catalog ref. C can
advance before S does. A public UI that resolved C and sees status pointing to an
older catalog must show “Status has not yet confirmed this snapshot” and keep the
two contexts separate. If S describes a newer catalog than a deliberately pinned
C, label it as newer operational context; do not splice its release facts into C.

A source-attempt result can explain facts at C only when its input/output binding
establishes that relationship and its numeric identity agrees. Otherwise show it
as separately labelled operational context. A known failed attempt based on C may
explain why C remains usable; failure never changes C's observation timestamps.

No public start record or in-progress report. Attempt a final summary for every
normal outcome, including collection, validation and publication failures. Abrupt
termination or failure to publish the summary may leave no public report. Preserve
the previous report's original timestamps and label it “last reported run”. Do not
infer that it is the latest attempt, that no newer run exists, or that the system
is currently healthy/idle. If no report is available, say so without a synthetic
outcome. A newer catalog C may coexist with an older report S.

Every report links to its specific Actions run, using the actual run identity,
and recent collection runs. For the current workflow these are
`https://github.com/mareklangiewicz/AM/actions/runs/<run-id>` and
`https://github.com/mareklangiewicz/AM/actions/workflows/catalog.yml`.
Keep the recent-runs destination aligned if the collection workflow is renamed.
Actions pages may require GitHub sign-in; the public YAML and rendered summary
remain readable without it. Investigation links supplement the public report;
they do not substitute for its plain-language outcome and available measurements.

Custom run-order allocation, registration and missing-run reconciliation are not
required. One collection runs at a time without automatically cancelling the active
run on a new trigger. Use the actual workflow run identity; rerun-attempt metadata
and exact report fields belong to the health/interface contract. “Last reported”
only describes recorded summaries, never completeness of attempts. Catalog
publication confirmation follows its lineage; an ambiguous result stays unknown
until evidenced. No durable publication-intent service is required.

On a confirmed exact-parent catalog publication conflict, stop that run's
publication and preserve the newer remote catalog. A later scheduled run starts
from the current parent; no automatic merge/rebase/retry is required. An ambiguous
network result remains unknown unless confirmed by evidence.

## Readable names and rename behavior

Use `[a-z0-9][a-z0-9_.+-]*`, maximum 64 ASCII bytes, for source names, excluding
the exact `.` and `..` components. Paths have exactly one component between
`repositories/` and `.yaml`; reject slashes, percent escapes, traversal, absolute
paths and external URLs. The filename is an allocated stable label, not a derived
GitHub path. Prefer a representative AM app name at initial allocation.

Allocate in a reviewed registry keyed by numeric GitHub ID; require uniqueness of
both names and numeric identity. On collision use `<preferred>-<numeric-id>`,
shortening the preferred prefix to fit. If that too is reserved, require explicit
allocation rather than automatic reassignment. Retire names permanently instead
of rebinding them to another numeric source. Validate both directions at publication.

Upstream owner/repository renames update readable metadata after identity
verification and leave the source filename unchanged. App renames update app-map
keys explicitly; retained old app names, if desired, point directly to the same
file, never to another app key. Stable/nightly entries share facts without sharing
selection policy. Source-label renames are exceptional versioned migrations with
all references changed atomically; old pinned snapshots remain valid. Unpinned
raw file paths have no permanent-redirect promise. No duplicate source documents.

## Lossless compact URLs and media types

Keep original upstream URL bytes after the existing supported string decoding.
For uploaded assets choose an optional per-release `download_base` from literal
prefixes ending in `/` shared by at least two asset URLs. Choose the prefix with
greatest total canonical encoded-byte savings, counting the base field and changed
asset fields; tie-break by longest prefix, then ASCII byte order. Use it only
when savings are positive. With no positive savings, keep full URLs.
Each asset has exactly one of `url_suffix` or full `url`; suffix requires the
release base. Reconstruct by literal concatenation, never URL joining, decoding,
re-encoding or interpolation from tag/name. Validate the reconstructed full HTTPS
URL under the domain validator, as well as base/suffix structure. A suffix may
be empty; it remains distinct from a missing field. Full `url` is the escape hatch
for exceptional hosts/paths. Generated source archives keep their full URL fields.

Example shapes, with the remaining required fields omitted for readability:

```yaml
download_base: "https://github.com/example/tool/releases/download/v1/"
assets:
  "101":
    name: "tool.zip"
    url_suffix: "tool.zip"
    media_type: "zip"
  "102":
    name: "tool.bin"
    url_suffix: "tool.bin"
  "103":
    name: "special"
    url: "https://downloads.example.org/exact?key=a%2Fb"
    media_type: ""
```

Use `media_type`, not `type`, for the upstream media-type fact. Omission means
exactly `application/octet-stream`; empty string preserves an explicit empty
upstream value. Initial exact alias table: unescaped `zip` → `application/zip` only.
Ordinary full MIME values preserve original case and parameters.

**Accepted literal amendment — November 8, 2026:** Marek selected a leading `=` in
this same compact field to preserve an upstream value literally. Strip exactly
one leading `=` and return the rest without applying aliases or recursively
stripping another escape: `=raw` → `raw`, `=zip` → `zip`, `==raw` → `=raw`.
The writer prefixes `=` for bare literal values and original values already
starting with `=`; the existing alias/full-type/omission/empty rules remain.
Readers still reject unrecognized **unescaped** bare aliases. A future alias-table
expansion needs a versioned contract update; escaped literals remain unambiguous.
Never infer media type from the filename. Missing upstream media type fails
normalization unless the acquisition contract supplies an explicit evidenced value;
omission must not invent the octet-stream default.

Reader query APIs expose reconstructed full `url` and expanded `media_type`
values so selection logic need not implement encoding rules. A compatibility
projection may retain `content_type` for migrated consumers; its exact API belongs
to the compatibility decision. Pin round-trip fixtures including escapes, Unicode,
query strings, differing hosts and empty/default MIME values before migration.

## Validation, schemas and unavailable data

Retain the supported mapping-only YAML grammar, exact decimal integers, quoting,
ordering and observation rules. No new nulls, comments, aliases or sequences.
Split grammar parsing from explicit kind/version domain validation, without
weakening either. Unknown fields/kinds/versions fail closed. Resource bounds and
path whitelists apply per channel and document kind, independently of schema validity.

Use JSON Schema draft 2020-12 for immutable schemas for every kind, with descriptions,
examples, defaults and closed object structures. Associate them through editor
configuration by channel/path; no YAML modeline or `$schema` field. The schema
set is pinned by the descriptor (status root for status schemas) and checked into
the maintained source. Structural schemas supplement canonical grammar/order,
integer precision, cross-document identities and semantic validation. Shared
positive/negative fixtures must check writer, strict shell reader, browser domain
validator and editor schemas; record deliberate schema-only validation limits.

Optional absent fields mean unavailable/inapplicable only as that kind explicitly
defines. Where a distinction matters, use an explicit state plus optional reason
and value fields; unknown never equals false, empty, zero, custom or success.
Network-unavailable documents are a transport state; missing required files in a
successfully fetched snapshot invalidate that snapshot. Refuse invalid new data
and keep separately identified prior valid data. Never combine arbitrary cached
documents from different pins. Shell absence/error exit behavior remains distinct.

Public summaries use an explicit sanitized field allowlist: no credentials,
arbitrary exception messages, headers, environment dumps or private checkpoint
paths. Exact enums, measurement definitions, per-document bounds and retention
counts belong to the health and storage decisions. Preserve gaps if evidence is
unavailable or removed; the latest summary identifies retained detail coverage.

## Compatibility and delivery gates

Format 2 keeps its existing whitelist, numeric filenames, semantics and reader.
Format 3 gets a separate explicit whitelist and reader validation path; never
accept new health/provenance files by relaxing format-2 validation. Installed
consumers retain shell/awk operation without Python/jq runtime requirements.

Build and verify the v3 candidate privately from the same acquisition/normalized
records; dual-format output must not cause a second upstream acquisition. Before
activation, require semantic equivalence fixtures, exact ID/observation and URL/
MIME round trips, shell/browser bounded-reader compatibility, actual DOM/fetch
checks, and tested format-2 rollback. Migration/cutover timing and any dual-channel
operation must be settled by the compatibility ticket, rather than assumed here.

Acceptance scenarios: a handled whole-collection failure leaves C unchanged but
attempts a final S summary; source-isolated partial outcomes report only known facts;
validation failure cannot publish C and still attempts a final summary; a confirmed
publication conflict reports refused, while an ambiguous result reports unknown;
abrupt termination may leave no report; successful C publication followed by failed
S update leaves the prior “last reported run” with its original timestamps;
old C links remain internally pinned; unsupported schema versions are refused;
unavailable S leaves browsing C useful. No production schemas, refs, reader changes,
publication dispatch or installed-host operations are performed by this decision.

## Accepted per-source provenance amendment — November 8, 2026

Marek accepted per-source provenance after the 5,000-app preflight measured the
central document at 2.30–13.42 MB against the existing 2 MiB allowance. This
supersedes the global `provenance.yaml` row above. The executable
[format-3 contract](../../catalog-format-v3.md#documents-at-c) now requires
`provenance/<source-label>.yaml` for each app-referenced source, containing exactly
its app/channel identities and their unchanged architecture/evidence bindings.
Derive its path from the validated source path and read it at the same C.
No second index, format-2 change or weakened evidence/byte check is introduced.
[Implementation and measured partition results](preflight-14.md#accepted-correction-and-partition-check--november-8-2026)
record the scope and remaining qualification limits. Old unpublished candidates
must be rebuilt. This does not activate collection or public v3/status channels.
