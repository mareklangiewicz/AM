# Show failures and staleness to users

Type: grilling
Label: wayfinder:grilling
Status: resolved
Blocked by: 06

## Question

What does a user see for an app whose last check failed, that has never
succeeded, or whose data is old, and what does the webpage's health view keep
from today's run summaries and statistics?

## Answer — November 25, 2026

Marek's answers to two grilling rounds.

Evidence (`origin/catalog-status-v1` and catalog `dbeb79f8b`, November 24,
21:34 UTC): 4,000 of the status branch's 4,066 files are per-source details (8
runs × 500); the page reads a source's detail only from the last run, so most
show "Refresh unknown" (ticket 01, R26). The latest summary has `unknown`,
`unattempted` and `deferred` at 0, 4 of 11 metrics always unknown
(`received_bytes`, `packed_history_bytes`, `remote_storage_bytes`,
`peak_rss_bytes`) and `budgets` repeating code constants; `stop_reason` was
`source_validation` in 63 of 64 summaries (R23). Age buckets: 2,473 / 1,411 /
4,390 / 14 / 0. Oldest repository `observed_at` 2026-11-10; 7 repositories last
seen more than 7 days before the catalog commit (`git grep '^observed_at:'`).

- **Per-source state lives in the repository file** (`observed_at`, `failed_at`,
  `failed_with`). Per-source detail files, the status `details` map and its
  timestamps, and per-source `reason` codes go.
- **`failed_with` keeps four codes** (`same_tag_conflict` leaves in ticket 14):
  - `not_found`: "GitHub says this repository doesn't exist or isn't public."
  - `too_large`: "GitHub's answer was larger than the catalog accepts."
  - `invalid_response`: "GitHub's answer wasn't what the catalog expects."
  - `transport`: "GitHub couldn't be reached."
  Shown as "Last seen 3 h ago · last attempt failed 1 h ago: <sentence>".
- **Never collected**: "Never collected · last attempt failed 1 h ago:
  <sentence>", no releases (ticket 20's shape).
- **Old data: the host warns, never refuses** (Marek, changing catalog-system
  ticket 19's rule): when the selected release was last seen more than **14
  days** ago (its own `observed_at`, else the repository's), AM prints a warning
  and continues; `--accept-stale-release`, the stale tuple and the refusal of
  stale release/Git selections go. Page: "Last seen 15 days ago: AM warns before
  installing from data this old."
- **Run summaries**: one `status/runs.yaml` keyed by run, the last 64, each with
  `id`, `attempt`, `reported_at`, counts `enrolled`, `selected`, `succeeded`,
  `failed`, the 7 known metrics and `stop_reason` (`complete`, a budget,
  `quota`, `authentication`, `internal`: why the run stopped early, never
  `source_validation`). Stage outcomes, zero counts, unknown metrics and
  `budgets` go.
- **Statistics**: age buckets from `observed_at` only: under 24 h, 24–48 h,
  48 h–14 days, over 14 days, never collected. The `unknown` bucket and daily
  aggregates go.

Implementation: [Slim the status channel](22-slim-the-status-channel.md) and
[Warn instead of refusing old catalog data](23-warn-on-old-catalog-data.md), both
unblocked.

## Comments

November 23, 2026, from ticket 04: repository files get optional `failed_at`
and `failed_with` (present only while the latest attempt failed). This ticket
settles the `failed_with` code list (schema enum; `not_found`, `rate_limited`,
`too_large`, `invalid_response`, `other` are the starting guess) and what the
page says for each.

November 24, 2026, from ticket 06: the catalog's times are settled (one
repository `observed_at`, release `observed_at` only when older). This ticket
owns the status channel's times: `reported_at`, source `attempted_at`/
`completed_at`, the `details` values and statistics `evaluated_at`. The
freshness buckets now count from `observed_at`.
