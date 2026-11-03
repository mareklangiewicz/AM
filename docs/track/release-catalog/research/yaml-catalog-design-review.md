# YAML catalog design — current shared understanding

Status: user-revised November 3, 2026. [Retention revision](yaml-retention-revision.md)
supersedes mandatory full-history collection and replacement-only release windows.
Production remains format 1; this is local design and experiment authorization.

## Facts and format

Publish normalized release facts as `repositories/ID.yaml` and a small YAML app
map, without raw responses or a distributed JSON/TSV compatibility layer. Clients
choose releases/assets and define latest; collection makes no separate latest
request. Keep source archive URLs and embedded uploaded-asset facts as returned,
without claiming independently audited asset completeness or transactional pages.

Use the strict mapping-only YAML subset and ordered fields in the
[schema draft](../../../catalog-format-v2.md): quoted dynamic keys/strings,
canonical integers/booleans, `{}` for empty maps, fixed indentation, immutable
schema reference and shared structural validation. The accepted escape set
includes `\N`, `\L`, `\P` along with quote/backslash/newline/carriage-return/tab.
Missing optional fields differ from actual empty strings. Unsupported input fails
normalization rather than being silently changed.

## Scope, merge and freshness

Parameters: configured source subset (default all), page size 1–100 (default 100),
and a positive page count or `all` (default 1). Scheduled runs default to all
configured sources and one page of 100 releases. Manual runs can request other
scopes. Request/byte/time budgets remain mandatory even with `all`.

Completing the requested limited scope succeeds; exhausting a budget before its
completion fails. Stage a per-source merge: replace fetched release facts and
assets, retain unfetched releases exactly, and commit only on success. Failure
preserves all previous release observations and last-success scope/time metadata.
Unselected sources remain unchanged. `collection` records the latest attempt;
`last_success` records the last completed scope, actual page count and whether
pagination reached EOF. None implies every retained release was revisited.

Every release has `observed_at`: last successful committed response inclusion,
using that response's receipt time. Unchanged included records are reobserved;
untouched records, failed staged updates, cached copies and publication do not
advance it. Clients can choose an older stable release from the current catalog.
Installation freshness uses that release's observation time under the existing
48-hour rule and explicit stale override. A repository's recent collection time
cannot rescue a stale selected release.

Partial absence never deletes retained releases. The [exact local reconciliation
proposal](yaml-retention-revision.md#exact-reconciliation-policy-local-design-proposal)
retains by default, including on full history, and permits explicit deletion only
with a successful `all` reconciliation request. Full-history absence is not proof
of upstream deletion. Retained size can grow beyond one fetched page; independent
catalog-size, reader-memory and output-spool bounds still need measurement.

## Migration and evidence

The chronology remains in [interview decisions](yaml-format-design.md); newer
answers supersede older mandatory-history/check-time statements. [ADR 0001](../../../adr/0001-catalog-facts-and-client-selection.md)
keeps client selection separate, and [ADR 0002](../../../adr/0002-retained-release-observations.md)
records scoped retained observations. [Reader feasibility](yaml-reader-experiment.md)
and [memory measurements](yaml-reader-memory-experiment.md) are evidence for their
recorded schema revisions, not current worst-case bounds. [Resource strategy](yaml-resource-strategy.md)
is revised for incremental retention; candidate numbers remain trial proposals.

The local retained-observation experiment updates the reader and demonstrates
merge/failure/freshness behavior without network calls. Production normalization,
consumer selection migration, operational resource budgets and reviews remain
before deployment. No workflow dispatch, push, source repin or host delivery is
authorized by this revision. Natural-run acceptance remains separate.
