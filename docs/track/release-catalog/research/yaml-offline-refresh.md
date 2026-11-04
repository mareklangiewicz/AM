# Closed offline YAML refresh loop — November 4, 2026

[86](../issues/86-close-offline-yaml-refresh-loop.md), prototype `1719bd8aa` on
`prep/yaml-offline-publication`, extending `b85f56fec`.

`load_local` reconstructs apps/repositories from an exact local Git commit. It
uses the existing bounded blob helper, checks the format-2 file layout and checks
original YAML bytes with the strict shell reader before PyYAML decoding. Duplicate
keys therefore cannot disappear silently into a Python mapping. Reference/identity
checks are shared with candidate creation rather than implemented twice.

`refresh_local` combines that loader, existing `bounded.collect_files` normalization
and retained merging, and the existing format-2 local publisher. Only explicitly
selected saved-page sources are collected. The complete prior app map/source set
is carried forward; unselected source files remain byte-identical when the schema
reference is unchanged. Failed sources update attempt metadata while preserving
releases, last-success metadata and effective observations. The original full
commit is also the expected parent for the final ref update.

No network, cache, daemon, consumer dependency or watchdog was added. Trial file
caps remain explicit and unaccepted. Source pushes do not publish catalogs.
Bootstrap/configuration changes remain caller responsibilities; this does not
provide source enrollment or a production workflow adapter. There is no aggregate
snapshot/time/RSS guarantee. These remain trusted local fixture experiments.

`refresh_experiment.py` passes on mawk, GNU awk and BusyBox awk. Each trial writes
four snapshots: initial state, partial success plus invalid-response failure,
successful retry, and failure after a successful first page. The latter first page
contains a new release 458, which must not survive the later failure. A fixed
advancing clock makes preserved observations distinguishable from reobservation.
Three sources exercise selected success, selected failure/retry and unselected
preservation. Saved JSON includes Unicode/escaped line breaks and real normalized
asset fields. Pinned old state remains readable after later ref changes.

Across three tools: twelve valid snapshots, twelve shell-consumer reads and twelve
rejected operations (stale parent, unknown selected source, unpinned read, duplicate
YAML key) pass. Unselected bytes and failed-source state preservation pass.
The prior publication experiment was rerun after shared validation refactoring:
six snapshots, nine pinned reads and fifteen candidate refusals pass. Python
compilation and whitespace checks pass. The strengthened new-release rollback
case was rerun after its addition. Other matrices retain their earlier revisions.
Results live in `refresh-results.json` and `publication-results.json` on the branch.

Reproduce from `tools/catalog-yaml-prototype/` with `refresh_experiment.py` and
`publication_experiment.py`. The next useful validation is a realistic saved-response
replay before preparing the production adapter diff; further speculative consumer
supervision remains outside the critical path. Installed AM, production format,
workflow/schedule configuration, catalog ref and daily pin were not changed.
