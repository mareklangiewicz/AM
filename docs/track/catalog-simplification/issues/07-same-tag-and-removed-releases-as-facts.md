# Record same-tag and removed releases as facts

Type: grilling
Label: wayfinder:grilling
Status: resolved
Blocked by: 01, 02

## Question

With the facts-only principle: how does the catalog record several release ids
under one tag (in one fetch, or across runs), an asset whose digest changed, and
a release no longer returned upstream, without invalidating, replacing or
reconciling? Which first/last-seen facts does a client need to warn or to treat
a rolling tag as expected, and how does retention bound the history kept? Revises
ADR 0002; takes over the same-tag part of catalog-system ticket 20.

## Answer — November 24, 2026

Marek's answers to three grilling rounds. The catalog lists what GitHub lists;
nothing is invalidated, replaced or reconciled by tag.

Evidence (catalog `3fd57907b`, GitHub API on November 24), from
[scripts/07/](../scripts/07/): `twins.py 3fd57907b` and `gone.py 3fd57907b`, run
at main-marek `09079186b`:

- All 14 `same_tag_conflict` sources are "twins": two release IDs, consecutive
  or nearly so, published within the same second under one tag, assets split
  between them (typically Linux builds on one, the rest on the other); a CI
  race. In 13 of 14 the twin is not the newest tag, yet it blocks the whole
  repository; none of the 14 was ever collected.
- All 612 per-release `observed_at` overrides (101 sources, 2–17 days old) are
  releases GitHub deleted: their fetch reached the end of the history or
  returned an older release. None is a release kept on purpose. (On
  `a8922b396`, a day earlier: 582 in 96 sources.)
- The host already selects by release ID (`published_at`, release ID, asset
  name); only its "duplicate exact tag" check (`catalog-contract-parser.am`)
  refuses twins.

Decisions:

- **Twins are two facts.** Every returned release is recorded under its own ID,
  even when tags repeat. `same_tag_conflict` leaves the collector, the host
  parser and the `failed_with` enum.
- **No exact-tag replacement.** A tag that gets a new release ID across runs
  (a recreated `nightly`) is one more release; the old one goes only by the
  next rule.
- **Proven-gone releases are removed.** A fetch proves a release gone when it
  reached the end of the history or returned an older release (GitHub lists
  newest first). Git history keeps the old record. A release the fetch merely
  did not reach stays, with its last-seen `observed_at`. This also bounds
  rolling tags, without a tag rule.
- **Assets are the latest fetch's list.** A re-uploaded file is a new asset ID;
  no asset history or digest-change marker in the file. A client notices a
  change by asset ID or `sha256pre`.
- **No first-seen time.** A new release ID with its own `published_at` is what a
  client needs.
- **Retention counts tags.** Ticket 08's 8 newest, newest stable and newest with
  Linux count tags and keep every release ID under a kept tag, so twins are never
  split.

Page text, replacing ticket 06's second "How it works" sentence: "Each repository
lists the releases GitHub shows for it now; a release deleted on GitHub is
removed (the catalog's history keeps it). An older release kept on purpose — the
newest stable one, or the newest with a Linux download — shows when it was last
seen. Two releases can share one tag; both are listed." Twins are two entries
with the same tag, unlabelled.

Implementation: [Record twins and drop proven-gone releases](18-record-twins-and-drop-gone-releases.md)
(today's format, unblocked); tag-counted retention joins
[ticket 14](14-write-slimmer-release-facts.md). The installer side is
[How AM's updater reads release facts](19-how-am-updater-reads-release-facts.md).
ADR 0002 has a dated note; glossary "Reconciliation" is redefined.

## Comments

November 24, 2026, from ticket 06: a release keeps its own `observed_at` ("last
seen") only when a later read didn't return it; first-seen was left to this
ticket, to add only if a client needs it.
