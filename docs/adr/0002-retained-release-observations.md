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
