# Choose scalable snapshot and history storage

Type: grilling
Label: wayfinder:grilling
Status: claimed
Assignee: codex-storage
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

### Accepted newest-release ordering — November 7, 2026

Marek answered “yes” to using upstream publication time to define “newest” for
the five-release minimum and newest non-prerelease protection, with numeric
release ID breaking ties. Order publication times descending, then numeric IDs
descending. Editing an old release does not move it ahead of newer publications.
Missing publication-time behavior, the two-year boundary and pruning timing
remain open. This records a planning decision only.

### Accepted cadence and release retention — November 7, 2026 side conversation

Marek explicitly answered “Yes” to this proposed policy:

- Two scheduled collection runs daily, with additional manual workflow dispatch
  available whenever wanted. This supersedes hourly scheduling as the target;
  it does not change the deployed workflow or promise that every trigger runs.
- Keep every release published within the last two years.
- Also keep at least the five newest releases per source, even when some or all
  are older than two years.
- Also protect the newest non-prerelease release regardless of age, so recent
  prereleases do not evict the last stable release.

This explicitly permits age/count-based removal from the current retained release
set, amending the previous retain-unfetched-records policy in ADR 0002 for that
purpose. It does not authorize deletion inferred from absence in a partial fetch,
or changing retained observations' effective freshness. Ordering for “newest” is
settled by the subsequent ordering comment above; time-boundary rules, missing
publication-time behavior, and safe pruning timing remain open. No exact cron
times were chosen.
Translate these choices into the baseline/spec/ADR and implementation roadmap in
the main planning session; the ticket remains claimed and unresolved because its
broader storage/read/write and capacity-experiment questions remain open.

Marek subsequently agreed to leave existing Git history intact for now after
asking whether a one-time history prune was warranted. Reconsider only if measured
history growth makes it worthwhile. No history reset/rewrite or force push is
authorized. Removing current release records does not erase their Git history.

#### Size evidence and estimates discussed

Read-only local inspection in this side conversation found:

- The preserved catalog-only repository at
  `/home/marek/Documents/Codex/am-500-publication-20261107/live-catalog.git`
  is not shallow; its `refs/heads/fetched` at
  `cbda9fb78ce4a6f29bdabd63d57f3c0085e8744f` has 39 reachable commits.
  `git count-objects -vH` reports one pack, 59.28 MiB, and no loose objects.
- The main AM clone's shared object database reports 359.94 MiB packed plus
  58.24 MiB loose (approximately 418 MiB), including locally held branches.
  Neither figure is a fresh measurement of GitHub's server-side storage.
- The saved 500-source snapshot's 63,690,470 YAML bytes / 16,027 releases give
  approximately 3,974 bytes per release including assets. At unchanged density,
  1,000 / 5,000 / 10,000 sources extrapolate to 127 MB / 637 MB / 1.27 GB of
  current uncompressed YAML. These are not measured capacity qualifications.
- Illustrative no-pruning growth at that density: one new release per source per
  week adds about 103 MB/year for 500 sources or 1.03 GB/year for 5,000; one daily
  adds about 725 MB/year or 7.25 GB/year respectively. Actual arrival rates were
  not measured, and these estimates exclude Git revision overhead/churn.
- Two daily runs create 12 times fewer scheduled publication opportunities than
  hourly runs; this is not a measured 12-fold reduction in storage growth.
  Compressed Git-history growth still needs representative measurement.

GitHub's checked documentation distinguishes recommendations (ideally <1 GB,
strongly <5 GB; a separate structure guide recommends compressed `.git` <=10 GB)
from enforced single-file and push limits. Ordinary Git does not use the metered
Git LFS storage allowance. A history rewrite also cannot guarantee immediate
server-side reclamation or continued availability of old catalog pins.
Sources: [large-file guidance](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github),
[repository limits](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits),
[Git LFS billing](https://docs.github.com/en/billing/concepts/product-billing/git-lfs),
[history-rewrite caveats](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

This side conversation changes planning records only. No workflow, runtime,
catalog content, Git history, remote ref, installed host or yadm pointer changed.

### Planning continuation — November 7, 2026

Claimed after the public-contract and simplified-recovery prerequisites resolved.
Implementation simplicity remains the priority; no storage backend or retention
change is accepted. Begin with the product choice of whether automatic removal
of older retained releases is acceptable. This concerns release records in the
current catalog, separately from retaining past catalog snapshots in Git history.
Any removal policy would explicitly amend the retained-release decision; its
age/count rules and protection for useful older releases remain undecided.
Await Marek's answer before choosing that policy or downstream storage machinery.

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
