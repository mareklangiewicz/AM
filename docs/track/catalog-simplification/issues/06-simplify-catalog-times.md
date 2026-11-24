# Simplify the catalog's times

Type: grilling
Label: wayfinder:grilling
Status: resolved
Blocked by: 01

## Question

Today: collection time, a shared observation time, per-release observation
times and publication time. Measured: the shared `observed_at` equals
`collected_at` in 8,270 of 8,272 sources; 719 releases carry their own older
time. Which times remain (proposal: one "checked" time per source, a release's
"last seen" only when older, plus first-seen if ticket 07 needs it), and how is
each said on the page?

## Answer — November 24, 2026

Marek's answers to two grilling rounds. One time per repository; everything
without its own time inherits it.

- **One source time, `observed_at`**: when the release page was received.
  `collected_at` is dropped. It equalled the shared `observed_at` in 8,270 of
  8,272 sources, and the 2 others (with Git scope) are 1 s later. The page receipt
  is the earlier time, so inheriting it can only understate freshness. Batch
  order, ticket 20's rotation (newer of `observed_at` and `failed_at`), the
  statistics freshness buckets and the page's source header read `observed_at`.
- **Releases: unchanged rule.** A release carries its own `observed_at` (when it
  was last seen) only when older than the source's; otherwise it inherits it. Not
  renamed: `observed_at` already means "last seen". The host's 7-day freshness
  rule is unchanged (client's decision).
- **Git refs and files: no own time.** Each collection refetches them in full
  (`git_observations.collect`), seconds after the release page, so they inherit
  the source's `observed_at`. The rules that a file time cannot precede its
  branch's or follow `collected_at` go.
- **Release dates: only `published_at`.** `created_at` is dropped. That
  supersedes ticket 08's "`created_at` only when there is no `published_at`",
  which never happens: drafts are skipped and every other release has
  `published_at` (`bounded.py`). The missing-timestamp rule becomes "drafts are
  skipped". Retention, host and page all order by `published_at`, then release ID.
- **Provenance `evaluated_at`: dropped.** Classification depends only on the
  pinned inputs the evidence already records, and nothing reads the time.
- **Scope**: the status channel's times (`reported_at`, source `attempted_at`/
  `completed_at`, `details` values, statistics `evaluated_at`) belong to
  [ticket 11](11-show-failures-and-staleness.md). First-seen, if needed, belongs to
  [ticket 07](07-same-tag-and-removed-releases-as-facts.md).

Page text:

- Source header: "Last seen 3 h ago" (its releases were last read from GitHub
  then), plus "· last attempt failed 1 h ago" when a later attempt failed.
  Replaces "Collected N ago".
- A release with its own older time: "Last seen 5 d ago". Others show no separate
  time. Replaces the per-release "Observed N ago".
- How it works: "Each repository shows when its releases were last read from
  GitHub. A release that a later read didn't return keeps the time it was last
  seen."

Implementation: added to
[Write the slimmer release and asset facts](14-write-slimmer-release-facts.md), so
the published format changes once. Glossary: "Collection time" superseded,
"Shared observation time" becomes "Repository observation time". ADR 0002 has a
dated note.
