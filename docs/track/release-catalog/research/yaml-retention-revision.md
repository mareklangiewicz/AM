# Retained releases and scoped collection — November 3, 2026

Status: user-directed revision of the accepted YAML design; local design and
experiments only. Supersedes mandatory full-history collection and replacement-only
release windows. [Schema](../../../catalog-format-v2.md) and
[ADR 0002](../../../adr/0002-retained-release-observations.md) describe the new model.

November 4 agreed encoding revision: a repository `observed_at` supplies the shared
default; release overrides are omitted when equal and included otherwise. Resolve
the effective observation before judging freshness. Before advancing the default,
materialize old effective times for untouched implicit releases; failure preserves
the prior default and release observations exactly. Per-page receipt times remain
distinct through overrides. The schema and ticket 77 describe the implementation;
the completed November 3 experiment below is historical evidence for the earlier
fully explicit encoding.

## Parameters and outcomes

A collection chooses configured source identities (default all), page size
1–100 (default 100), and a positive page limit or `all` (default 1). A finite
scope starts at page 1 and succeeds when its limit is reached or pagination ends
earlier. Scheduled defaults are all configured sources, one page of 100 releases;
manual runs can choose other scopes. Empty explicit source subsets are valid
no-ops; unknown or duplicate identities and invalid parameters fail before work.

Safety request/byte/time budgets are independent stop conditions. Reaching them
before scope completion is failure, never an implicit smaller successful scope.
An `all` request still has finite safety budgets. Page metadata records whether
history ended; finite scope success need not mean full-history success. No GitHub
latest request or release selection policy is added to collection.

## Merge and time semantics

Stage a per-source merge by release identity. Replace fetched normalized release
facts, including its returned asset mapping and optional-field omissions. Preserve
every unfetched release's facts and effective timestamps. Its stored timestamp
may become explicit to preserve the old value when the default changes. Commit only when the complete
requested scope and merged document fit validation and safety budgets. On failure
retain the previous releases and last-success metadata exactly; publish only the
latest attempt status/scope/time/reason. Unselected source files are unchanged.
Other independently successful sources can commit their own observations.

The effective per-release `observed_at` is the response-receipt time for the body actually
including that release, committed only after scope success. Different pages can
have different observation times. Inclusion with unchanged facts advances time;
absence, publication, a recent repository collection, a 304 with no release body,
or copying a cached record does not. A failed multi-page request does not advance
even the records included in its early successful pages. Timestamp comparisons
must not hide a clock regression by manufacturing a newer time.

Repository `collection` describes the latest attempt; `last_success` describes
the last completed requested scope, with completion time, requested page size and
limit, reconciliation flag, actual fetched pages and history-completion flag. `releases` is the retained
set, not a representation of only that last fetch. No `checked_at` survives as an
ambiguous proxy for all release freshness. The former draft was never deployed;
format remains 2 and its immutable schema reference distinguishes the revision.

Example: catalog contains stable A observed Monday. Tuesday's one-page fetch
contains prerelease B, but not A. Tuesday collection succeeds; A remains with
Monday `observed_at`, and B has Tuesday `observed_at`. A client can select A from
the current catalog. Installation checks A's age against the existing 48-hour
limit, with the explicit stale override, rather than using Tuesday collection or
publication time. A deeper manual refresh can reobserve A if it lies outside the
scheduled scope, subject to budgets. Ordinary daily collection does not promise
all retained releases are fresh.

## Exact reconciliation policy (local design proposal)

Default: retain absent releases after every successful collection, including
`all`. Request deletion explicitly with `reconcile=true`; require an explicit
`page_limit=all`, all pages to EOF, successful normalization and full-scope commit.
Reject reconciliation with a finite limit before acquisition, even if that limit
might happen to reach EOF. After success, remove retained release IDs not present
in the fetched published release set; no tombstones or per-release deletion API
claims are introduced. Replace fetched records normally. Successful empty full
reconciliation produces `releases: {}`. Failure or any safety-budget stop commits
neither updates nor deletions. A future collection can reintroduce a removed ID.

The policy is deliberately opt-in: full pagination is not a transactional snapshot,
and absence can reflect upstream mutation or visibility changes. Reconciliation
means the catalog's retained set is aligned with this observed published set;
it does not certify upstream deletion. This distinction does not require extra
per-release API requests. Until an operator requests reconciliation, records
persist. There is no automatic age/count eviction hidden in collection.

This opt-in policy is the concrete local design proposal. No production behavior
is enabled by the proposal.

## Resource consequences and experiment scope

One-page input does not bound an accumulated catalog. Enforce catalog bytes,
line size, process memory and output-spool limits separately. If a merge exceeds
a catalog bound, fail without silently evicting old releases or advancing times.
Reconciliation may shrink the set but must not bypass acquisition or staging
budgets. Resource refusal can leave a repository stale until an explicit bounded
maintenance action succeeds.

The earlier 58/63-page tail observations remain useful for manual `all` and
reconciliation costs; they no longer establish a mandatory daily history cost.
The prepared inventory's 772 identities imply 772 default page attempts before
failures/other API calls, not the earlier roughly 976 full-history extrapolation.
Recount the configured inventory and actual workflow credential budget during
implementation. Earlier BusyBox RSS growth remains a reason to keep memory/file
bounds; old measurements do not benchmark the revised schema.

Offline transition fixtures cover subset selection, finite/all/early-EOF scope
success, record replacement/retention, per-page observation times, failures after
partial work, request/byte/time/catalog/line ceilings, explicit reconciliation,
and selection/freshness of an older stable release. Shared fixture budgets
also test aggregate request/byte/time exhaustion across sources, preserving
already successful sources and leaving unattempted sources unchanged with an
explicit report. This is a fixture-driven model, not a network collector, actual
transport/deadline enforcement, fair runner scheduler or production migration. No live measurement is required for this
revision, and none is authorized implicitly by these findings.

## Completed local experiment

Prototype source: `research/yaml-retained-observations` at
`4600ae0840b1ec516db9e77eda984e2fc53e6297`, directory
`tools/catalog-yaml-prototype/`. The worktree `/tmp/am-yaml-retained-observations`
is disposable; the branch is the durable source pointer. It descends from the
memory experiment and retains its limitations. No prototype code is merged into
main.

Run `python3 tools/catalog-yaml-prototype/retention_matrix.py` in that branch.
Sixteen unique test groups pass on each of mawk, GNU awk and BusyBox awk: nine
updated reader groups and seven retained-collection groups. `retention-results.json`
records the matrix. Shell syntax, shellcheck and whitespace checks pass; both
example documents validate. Normalized fixtures are also compared against an
independent YAML parser. No network requests, binaries, workflow actions or host
updates were performed.

The model has shared simulated request/byte/time budgets, plus per-source
request/response-byte/total-byte/time and merged-document/line limits. It does not
implement bounded transport, real wall-clock deadlines, fair scheduling or a
production normalizer. The former resource measurement files remain explicitly
historical; this revision does not establish new production memory/CPU bounds.
