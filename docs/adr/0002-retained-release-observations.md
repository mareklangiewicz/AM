# Merge scoped collections into retained release observations

Collect a configurable source subset, page size (1–100) and positive page limit or all, defaulting scheduled collection to all sources and one page of 100 releases. Merge fetched releases into retained records only after the requested scope succeeds within explicit safety budgets; retain unfetched records, and preserve the previous observation on failure. This supersedes mandatory full-history collection and replacement-only release windows, allowing clients to select older stable records from the current catalog while judging freshness by each release's response-inclusion time (`observed_at`), independently of repository collection and publication times.

Full-history reconciliation requires a separately explicit deletion policy; partial absence never removes releases. Retention growth still needs catalog-size and reader-memory bounds. This decision authorizes local design and experiments only, with no deployment, dispatch, push or repin.

November 4 representation revision, agreed by Marek: a repository-level shared
observation timestamp supplies the default. Omit release `observed_at` when equal
to that default; include an override otherwise. Before changing the default,
materialize the old effective timestamp for previously implicit releases left
untouched. Preserve the shared default and all release observations on failure.
Keep distinct page-receipt times through overrides. This reduces repeated
timestamp churn without changing any release's effective freshness; measure Git
history as well as snapshot size. Implementation and evidence are in ticket 77.

November 7 retention amendment, agreed by Marek: after a source's requested scope
succeeds, merge fetched releases and apply the explicit count-based retention
policy before candidate validation and publication. This permits removing
unfetched records under that policy, while partial-fetch absence still never
establishes upstream deletion. Failed and unattempted sources stay unchanged;
retained records keep their effective observation times. Keep the 32 newest
observed releases and, if none is non-prerelease, the newest observed non-prerelease
when available (at most 33), including all their assets. Publication time orders
records, falling back to creation time, then numeric release ID, descending.
This supersedes the earlier age window and unlimited undated exception. A release
missing both timestamps invalidates that source's collection; preserve its previous
published data and report the validation failure, without inventing a timestamp or
ordering. See the
[accepted missing-timestamps rule](../track/catalog-system/issues/05-choose-scalable-snapshot-and-history-storage.md#accepted-missing-timestamps-rule--november-7-2026)
and the
[accepted count policy](../track/catalog-system/issues/05-choose-scalable-snapshot-and-history-storage.md#accepted-32-plus-stable-retention--november-7-2026-side-conversation).

Marek also accepted one current record per exact tag within each numeric source:
a newly observed release replaces an older retained incarnation of that tag,
even if the numeric release ID changed. Keep the observed ID as evidence; apply
tag replacement before count retention. Distinct tags remain distinct. Different
release IDs for the same exact tag within one collection invalidate that source's
collection; preserve its previous published data and report the conflict rather
than choosing an ID. See the
[accepted conflict rule](../track/catalog-system/issues/05-choose-scalable-snapshot-and-history-storage.md#accepted-conflicting-same-tag-evidence-rule--november-7-2026).
See the [accepted exact-tag replacement rule](../track/catalog-system/issues/05-choose-scalable-snapshot-and-history-storage.md#accepted-exact-tag-replacement--november-7-2026-side-conversation).
Earlier catalog commits preserve metadata, without guaranteeing historical binary
availability. This amends retention/supersession, not collection scope or freshness.
Existing Git history stays intact; no runtime change or history rewrite is authorized.
