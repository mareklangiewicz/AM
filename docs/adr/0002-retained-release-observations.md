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
succeeds, merge fetched releases and apply the explicit age/count retention
policy before candidate validation and publication. This permits removing
unfetched records under that policy, while partial-fetch absence still never
establishes upstream deletion. Failed and unattempted sources stay unchanged;
retained records keep their effective observation times. Keep releases within
730 days, at least the five newest dated releases, the newest dated non-prerelease,
and all undated releases. The exact inclusive cutoff, ordering and application
rules live in the
[accepted retention policy](../track/catalog-system/issues/05-choose-scalable-snapshot-and-history-storage.md#accepted-pruning-timing-and-current-retention-policy--november-7-2026).
This amends unconditional retention, not collection scope or freshness semantics.
Existing Git history stays intact; no runtime change or history rewrite is authorized.
