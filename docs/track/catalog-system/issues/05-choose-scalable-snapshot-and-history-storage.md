# Choose scalable snapshot and history storage

Type: grilling
Label: wayfinder:grilling
Status: open
Blocked by: 01, 03, 04

## Question

Which simple storage/read/write approach supports bounded reruns and coverage beyond
500 sources while bounding full-snapshot work, individual documents, readers,
retained releases and remote history growth?

Compare the smallest credible alternatives using measured baseline constraints.
Distinguish current tree size, local Git guard, transferred Git history and durable
remote retention. Removing a current-tree file does not purge Git history.
Honor retained-release semantics; any pruning, reconciliation, depth or freshness
trade-off must be explicit and agreed, not an incidental optimization.

Define local temporary-evidence cleanup, public snapshot addressing, lazy
consumer reads, unchanged-source reuse and exact-parent conflict implications.
Choose what bounded experiment is required before accepting capacity and record
its decision threshold; do not qualify thousands from a synthetic count alone.
Preserve shell consumers or define an explicit compatible migration path.
No cap increase or storage implementation is authorized by resolving this question.

## Comments

### Accepted simpler recovery scope — November 7, 2026

Marek accepted redoing unfinished work after runner loss and final-summary-only
public health, with no public start record. Preserve the last published catalog;
no separate checkpoint store or runner-loss survival/replay guarantee is required. The older
durable-store, lease and publication-gate inputs below are superseded context.
Keep this storage decision focused on simple public snapshots, bounded reads/
writes/history and optional local temporary evidence. Recovery scheduling/retry
policy is now resolved in the owning ticket. Failed summary publication may leave
the previous timestamped “last reported run”; no durable report-delivery queue.

### Separate-store proposal withdrawn — November 7, 2026

During this ticket's discussion the agent proposed a private S3 checkpoint store.
Marek rejected that complexity and asked to prioritize simple implementation,
relax recovery guarantees where useful, and ask simple questions before deciding.
No store was provisioned, implementation written, or storage decision resolved.
The recovery ticket is reopened; this ticket returns to blocked/unclaimed until
the simpler recovery scope is agreed. Its earlier durable-store/gate inputs below
are historical and under reconsideration, not fixed constraints.

### Historical superseded inputs from the progress decision — November 7, 2026

[Durable progress and fair scheduling](../progress-and-scheduling-decision.md)
requires acknowledged evidence surviving runner loss, bounded raw/normalized
checkpoint staging and complete-scope replay, durable run registration/order and
ownership fences. Choose backend/lease/cleanup mechanisms and a measurable
runner-loss durability experiment. Lease expiry alone cannot transfer remote
publication authority: coordinate the serialized publication gate and ambiguous
write reconciliation with the interface decision. Fail closed if a prior publisher
or write cannot be reconciled. These are requirements, not proof that Git, a cache
or end-of-job artifacts already satisfy them.

### Read-only repetition measurement — November 7, 2026

The side conversation inspected the saved published snapshot at
`cbda9fb78ce4a6f29bdabd63d57f3c0085e8744f` in the preserved local
`/home/marek/Documents/Codex/am-500-publication-20261107/live-catalog.git`.
This is historical snapshot analysis, not a fresh remote-head or transfer check.
Reading its blobs with `git ls-tree` and `git cat-file --batch` measured
63,690,470 YAML bytes, 16,027 releases and 175,073 assets.

- Asset URL lines: 19,896,191 bytes, including indentation/key/framing.
- Asset content-type lines: 7,925,271 bytes, including indentation/key/framing.
  `application/octet-stream` occurs 55,460 times; `application/zip` 40,206 times.
- Indentation across documents: 8,476,854 bytes. This overlaps the line totals;
  do not add these categories as independent savings.
- Grouping asset URL prefixes (everything through the final slash) within each
  release gives 10,888,367 repeated prefix bytes beyond keeping each distinct
  prefix once. This is a gross opportunity, before replacement fields/encoding;
  it is not a measured migrated-format saving.
- Concatenating the YAML in memory and applying gzip level 6 gives 9,762,495
  bytes. This is compression potential, not per-file HTTP transfer, browser
  compatibility, Git pack/history size, or a deployed compression capability.

Most digest bytes are distinct useful information; a large field is not necessarily
redundant. Full asset coverage serves browsing across platforms. Whether to retain
every accumulated old release is a separate product/retention decision, not a
license to drop records during compaction.

[Choose public YAML contracts and revision consistency](03-choose-public-yaml-contracts-and-revision-consistency.md)
owns Marek's URL-prefix requirement, proposed media-type default/aliases and
editor-schema requirements. This storage decision should measure those alternatives
alongside incremental processing and retained/remote-history policy. Compact
encoding alone does not fix full-snapshot processing or durable progress.
No files in the preserved catalog or current publication were changed by this analysis.
