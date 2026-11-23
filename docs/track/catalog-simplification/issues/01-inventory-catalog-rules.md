# Inventory the catalog's rules

Type: research
Label: wayfinder:research
Status: resolved
Blocked by: none

## Question

For each rule a user can meet (selection order, run limits, retention of 32 plus
newest stable, same-tag replacement and invalidation, the four kinds of time,
partial history and reconciliation, status reporting, recipe classification
labels, platform guesses) and each format-3/status-1 encoding (`download_base`/
`url_suffix`, media type aliases and `=` escapes, omitted defaults, `state`/
`value` wrappers, reason codes, commit pins): where it is implemented, which
ADR or ticket accepted it, what the webpage says about it today
(`web/catalog/app.mjs`), and what reads or depends on it (hosts' modules, the
browser, tests). One table row per rule, with file:line references.

## Answer — November 23, 2026

Research on the local branch `research/catalog-rules-inventory` (commit
`d1f2e146f`, never merged): `docs/track/catalog-simplification/research/01-rule-inventory.md`,
62 rows (32 rules, 13 encodings, 17 commit pins) with file:line references,
accepting ADR/ticket, current page text and readers; counts from its
`scripts/01/` on catalog `a8ee4e2fe9` and status `0cf9f40f9c`.

Findings later tickets depend on (spot-checked on main-marek where marked):

- Selection sorts by last success, not last attempt: `incremental.py:53` sets
  `attempted_at` from `collected_at` (checked). Catalog-system ticket 20's cause.
- Same-tag conflicts and oversized responses are both published as
  `source_validation`; a run's `stop_reason` is `source_validation` whenever any
  source fails (63 of 64 summaries).
- Three "newest" orders disagree at the edges: retention uses published time
  falling back to created time; the host has no fallback and its stable
  channel also excludes the tag `nightly`. No published release hits the edge.
- The page misstates retention ("32 newest observed"; it is by publication
  time) and never mentions tag replacement; it labels every source "Bounded /
  partial history" (`app.mjs:69`, checked), though 7,573 of 8,272 reached the
  end of pagination; its per-source refresh line reads only the last run's 500
  details, so most sources show unknown.
- Written but read by nothing: asset `digest` (1.22M assets; the host verifies
  downloads from upstream `.zsync`/`.sha*` files instead, `APP-MANAGER:2008-2024`,
  checked), `media_type` (page only), `output_catalog`, four always-unknown
  metrics, `page_size`/`pages_fetched` (always 100/1), the `retention` string,
  `recipe.blob`.
- Status counts carry little: `deferred` always equals `unattempted`, which is
  0 in all known summaries; `unknown` is always 0.
- Pins: the four non-schema inputs are always the run's main-marek HEAD,
  repeated in about 24,000 provenance entries; every one of 16,546 files repeats
  the schema URL; the host reads only `inputs.schemas`.
- Never produced: classification `custom` (the workflow passes no reviews) and
  availability `unknown`.
- Stale text: `docs/catalog-operating-policy.md` (ceiling 500 and branch
  `release-catalog`; 8,288 enrolled, code cap 9,000), `REQUEST_CAP=500` vs the
  workflow's 750, "maintainer's quota" (the workflow uses `github.token`,
  checked), glossary "Reconciliation" (no implementation).
- 16,546 published files approach the 20,000-file catalog bound.
