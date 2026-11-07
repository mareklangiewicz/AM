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

Compare simple Git-based read/write approaches using measured baseline constraints.
Git is a firm project constraint; alternative storage backends are out of scope.
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

### Accepted temporary-evidence cleanup — November 7, 2026

Marek answered “yes” to keeping temporary collection files in the run's temporary
directory, removing them on normal exit, and relying on runner disposal after
interruption. Save local replay evidence only when explicitly requested. This is
temporary working data, separate from published Git snapshots and final public
summaries; it introduces no cross-run recovery store or automatic evidence archive.
Runner disposal applies to disposable workflow runners; interruption of a local
run does not itself guarantee deletion of its temporary directory. Planning only.

### Accepted validation for unchanged-blob reuse — November 7, 2026

Marek answered “yes” to trusting unchanged files only from an exact, previously
validated catalog commit under the same validation rules. Validate changed files
each run and preserve applicable root/cross-document identity checks. Changes to
format, schema or validation policy require a full snapshot check before reuse
under the new rules. This settles the validation direction left open in the
incremental-processing comment below; the evidence/mechanism establishing prior
validation and rule identity must be specified in implementation work. An exact
commit pin alone is not evidence of prior validation. Planning only.

### Accepted document-size overflow rule — November 7, 2026

Marek answered “yes” to preserving a source's previous published data and reporting
the refresh failure if its candidate document exceeds the document-size limit
after retention. Do not drop additional releases or assets to make it fit, and do
not raise the limit implicitly. The existing 2 MiB/document limit remains in place.
This settles the overflow question left open below; it does not establish capacity
or authorize an implementation or limit increase. Planning only.

### Accepted missing-timestamps rule — November 7, 2026

Marek answered “yes” to treating a source's collection as invalid if a release
has neither publication time nor creation time. Preserve that source's previous
published data and report the validation failure; do not invent a timestamp or
ordering, or apply replacement/pruning from that invalid collection. Publication
time still falls back to creation time when available. This settles the missing-
both-timestamps question left open below without adding an unbounded exception
to the 32-plus-stable policy. Planning only; no runtime change.

### Accepted conflicting same-tag evidence rule — November 7, 2026

Marek answered “yes” to treating a source's collection as invalid when that
collection returns different numeric release IDs for the same exact tag.
Preserve that source's previous published data and report the conflict; do not
choose a winning ID or apply replacement/pruning from that invalid collection.
This concerns conflicting newly collected evidence, not a new observation
replacing a previously retained incarnation under the accepted exact-tag rule.
This settles the same-tag validation question left open below. Planning only.

### Accepted exact-tag replacement — November 7, 2026 side conversation

After discussing Git tags, GitHub release identities and rolling nightlies,
Marek explicitly accepted the proposed rule and requested this tracker update:
keep one current release record per exact tag name within each numeric source.

- On successful source-scope collection, a newly observed release using the same
  exact tag as an older retained release replaces that older record in the current
  catalog, even when the numeric GitHub release ID changed. Keep the observed
  numeric release ID as evidence; a tag is not substituted for that identity.
- Updating the same release ID refreshes its record as before. Resolve tag reuse
  before applying the accepted 32-plus-stable retention rule, so old incarnations
  of a rolling tag do not consume retained-release slots or stable protection.
- Distinct tags such as `v1.2.3` and `v1.2.4` remain distinct releases, subject to
  the count limit. There is no special interpretation of names such as `nightly`,
  `stable`, `current` or `latest`; match exact names within the source only.
- Failed or unattempted source collection does not replace prior release data.
  Partial-fetch absence alone still does not prove deletion. A positively observed
  replacement under the same tag is the basis for this explicit supersession rule.
- Earlier catalog commits preserve previous observations, including older numeric
  release IDs and asset facts. This archives metadata, not upstream binaries;
  a reused tag/download URL does not guarantee access to historical asset bytes.

This deliberately replaces historical incarnations of a rolling tag in today's
catalog, including rolling non-prereleases. It does not discard a distinct
version-tagged release merely because a newer release becomes stable or “Latest”.
The main planning session must incorporate this rule alongside 32-plus-stable
retention in the spec/ADR and roadmap. The discussion of a possible 64-release
limit was measurement only; the accepted count remains 32 plus stable.
Ambiguous same-tag evidence within a collection still needs an explicit validation
rule; do not infer a winning numeric ID without specifying it. The ticket remains
claimed and unresolved. Planning only; no runtime, catalog or remote changes.

Reference facts: GitHub release publication requires a `tag_name`; release IDs
and uploaded assets are separate GitHub metadata. GitHub's “Latest” designation
is separate from a Git tag. Neovim's checked workflow deletes/recreates `nightly`,
illustrating why ID-only retention accumulates rolling-release incarnations.
Sources: [release API](https://docs.github.com/en/rest/releases/releases),
[Neovim release workflow](https://github.com/neovim/neovim/blob/master/.github/workflows/release.yml).
These references explain the decision; they are not capacity or binary-availability
guarantees, and the workflow link is mutable.

### Accepted 32-plus-stable retention — November 7, 2026 side conversation

Marek proposed keeping the 32 newest releases plus the newest observed
non-prerelease when all 32 are prereleases, then accepted the clarified policy
with “Great” and explicitly requested this tracker update.

- Keep the 32 newest observed releases per source, or all if fewer exist.
- If those contain no non-prerelease, also keep the newest observed
  non-prerelease, when available. This yields at most 33 releases per source;
  no additional historical acquisition is required to find an unobserved stable
  release.
- Order by publication time descending, falling back to creation time when
  publication time is absent, then numeric release ID descending to break ties.
  There is no unlimited undated-release exception. Handling records missing
  both timestamps still needs specification; it must preserve the count bound.
- Keep all assets belonging to retained releases.
- Apply pruning only after successful source-scope collection and merge, before
  candidate validation/publication. Failed and unattempted sources preserve their
  previous release data. Retained records keep their effective observation times.

This replaces the 730-day window, five-release minimum and unlimited undated
retention recorded below. Prior comments remain chronological history; the
pruning timing, Git foundation, unchanged-blob reuse, twice-daily target cadence
and decision to leave existing Git history intact still stand. The main planning
session must update the spec/ADR and roadmap to this replacement policy; their
earlier age/count text is superseded by this explicit acceptance.

The separate proposal to preserve prior data on document-size overflow has not
received a yes/no answer; accepting this retention policy does not resolve that
question or change the existing 2 MiB/document limit. The broader storage ticket
remains claimed and unresolved. Planning only; no runtime, catalog, workflow,
history, remote-ref or installed-host changes are authorized here.

#### Supporting read-only measurements

Measured from the preserved 500-source snapshot at
`cbda9fb78ce4a6f29bdabd63d57f3c0085e8744f`, not a fresh remote-head check:
source YAML totals 63,676,573 bytes, with median 53,353 bytes, 90th percentile
352,647, 95th percentile 521,023 and maximum 1,372,340. No source has more than
109 retained releases, so a hypothetical 200-release cap would remove none.
The largest source, `any-listen/any-listen-desktop`, contains 100 releases and
3,635 assets: 94 releases are marked prerelease and six non-prerelease.
Scaling its average bytes/release to 32 gives roughly 429 KiB, an extrapolation
only, not the measured size of the selected newest 32 or a capacity guarantee.
Release-count bounds do not guarantee a byte bound for asset-heavy releases.

### Accepted incremental source processing — November 7, 2026

Marek answered “yes” to processing only selected sources and reusing unchanged
Git blobs instead of loading and rewriting every source on each run. Build the
candidate from the exact prior catalog pin, preserving unselected source records
and their observations. Changed root documents still need their applicable
validation and cross-document identity checks; this direction does not waive
complete-snapshot integrity or the existing exact-parent publication contract.

The implementation roadmap must specify how previously validated unchanged blobs
are trusted/reused and when full validation is required, especially across format,
schema or policy transitions. These mechanics and their measurements are not yet
accepted. This is a processing direction, not proof of capacity or authorization
to implement or raise limits.

### Accepted Git foundation — November 7, 2026

Marek accepted keeping Git as the public snapshot store, reusing unchanged source
files and reading at exact commit pins. He explicitly strengthened the proposal:
“we will not consider any another backend.” Leveraging Git for transparency,
simplicity and trust is a main idea of the project, not a temporary choice pending
capacity measurements.

Capacity experiments must guide improvements and operating bounds within the
Git-based design; they are not a gate for switching to another storage backend.
Keep the selected separate catalog/status Git channels and exact-parent publication
contract. History-growth measurements still matter, with existing history left
intact as agreed. Processing strategy, bounds and the capacity experiment remain
open; no implementation or backend provisioning is authorized.

### Accepted pruning timing and current retention policy — November 7, 2026

The retention counts/window in this comment are superseded by the accepted
32-plus-stable policy above. Its successful-source pruning timing still applies.

Marek answered “yes” to pruning only after a source's requested collection scope
succeeds: merge fetched releases, apply retention, then validate before
publication. Failed and unattempted sources stay unchanged. The last good
publication remains intact if candidate validation or publication fails.

Together with the accepted answers below, the current policy is:

- Fix one UTC timestamp at collection start; retain dated releases published at
  or after that timestamp minus 730 days, inclusive.
- Also retain the five newest dated releases per source (or all if fewer exist),
  ordered by publication time descending, then numeric release ID descending.
- Also protect the newest dated non-prerelease release under that ordering.
- Keep every undated release outside the five dated-release slots. This also
  protects undated non-prereleases without inventing an ordering date.
- Apply these rules to the merged retained set after source-scope success, not
  just to fetched records. Absence from a partial fetch never proves deletion;
  removal under this explicit retention policy is independent of such absence.
- Preserve effective observation times for retained records. Pruning does not
  establish full upstream coverage or reobserve unfetched releases.
- Keep existing Git history intact for now; current-record pruning does not
  erase old snapshots. Reconsider history policy only from measured growth.

This settles the retention details previously left open below. Broader storage,
read/write and capacity-experiment decisions remain open; this ticket stays
claimed. The earlier comments are chronological discussion, superseded where
these accepted answers settle their pending questions. Planning only.

### Accepted retention time boundary — November 7, 2026

Marek answered “yes” to defining “within two years” as a rolling 730-day window,
measured from one fixed UTC timestamp at collection start. Retain a dated release
when its upstream publication time is at or after that timestamp minus 730 days;
the exact cutoff is inclusive. Use the same cutoff throughout that collection.
The five dated-release minimum, newest non-prerelease protection and undated
retention still apply outside the window. This settles the time-boundary question
left open below; safe pruning timing remains open. Planning only.

### Accepted undated-release retention — November 7, 2026

Marek answered “yes” to keeping releases with no publication date as undated,
outside the five dated releases. An unknown age is not grounds for pruning;
undated records do not consume the five dated-release slots. This settles the
missing publication-time retention question left open below. The two-year
boundary and safe pruning timing remain open. Planning only; no runtime change.

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
