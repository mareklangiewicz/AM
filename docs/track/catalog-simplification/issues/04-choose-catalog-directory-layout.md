# Choose the catalog directory layout in main-marek

Type: grilling
Label: wayfinder:grilling
Status: resolved
Blocked by: 01

## Question

Where in `main-marek` do the catalog and the status live (paths, file split,
one directory or two), and what does a host or the webpage fetch to read a
consistent snapshot without orphan branches?

## Answer — November 23, 2026

Marek's decisions, grilled from the two branches as they stand (`release-catalog-v3`:
`catalog.yaml`, `apps.yaml`, 8,272 `repositories/` and 8,272 `provenance/` files,
460 MB; `catalog-status-v1`: `status.yaml`, `statistics.yaml`, `runs/`, 2 MB).

Layout: one top-level `catalog/` directory in `main-marek`. Facts keep today's
split (`catalog.yaml`, `apps.yaml`, one `repositories/<id>.yaml` per source;
whether `provenance/` merges into them is tickets 05/09's). Status lives in
`catalog/status/` (`status.yaml`, `statistics.yaml`, `runs/`), with today's
bounds unchanged: 64 summaries, per-source details for the 8 newest runs, 90 days
of statistics; older runs only in Git history.

Consistency: each collector run writes everything it changes (facts, status or
both) in one `main-marek` commit, so a commit is a consistent snapshot. Hosts and
the webpage resolve `heads/main-marek` to a commit and read everything under
`catalog/` at it, the same pin-then-read they do today, one ref instead of two;
code and catalog share that pin. The cross-channel confirmed-publication binding
and its labelled lag go (ADR 0003 dated note). A run that fails validation still
commits its status and leaves facts untouched, so failures stay visible while
the last good catalog stays usable.

Code and catalog side by side: the collector touches only `catalog/`. Commits
touching only `catalog/` skip `tests.yml` (`paths-ignore`) and count as needing
no tests in `release.py plan`. On a rejected push the collector fetches, rebases
(conflict-free, it touches only `catalog/`) and retries a bounded number of
times; Marek's rejected push needs `git pull --rebase`. Bot commits (about 3 a
day) stay in `main-marek`'s log; `git log -- . ':!catalog'` filters them, named
in `AGENTS.md`. A separate repository stays a later option.

Order: the move comes after the slimmer facts (ticket 14), confirmed by ticket
15's measurement, so the checkout grows about 80 MB once instead of 460 MB.
No host clones the repository (hosts fetch raw files), so this affects only
Marek's and CI checkouts.

Migration: the directory starts from one fresh commit; no branch history is
carried. After the switch the collector stops writing both branches; each tip
is kept as a local-only `archive/<name>` ref and the branches are deleted from
origin after a week of clean directory runs.

Failure records (revises catalog-system ticket 20's `failed_attempts` map, see
its comments): each repository file gets optional `failed_at` and `failed_with`,
present only while the latest attempt failed, removed on the next success.
Rotation sorts by the newer of `collected_at` and `failed_at`. `failed_with` is
a code from a schema enum (`not_found`, `rate_limited`, `too_large`,
`invalid_response`, `other`, ...); ticket 11 settles the list. A whole-run
validation failure writes no repository files and stays in the run summary.

Implementation: [Move the catalog into `catalog/` in main-marek](16-move-catalog-into-main-marek.md)
and [Retry the collector's push after a rejection](17-retry-collector-push.md);
the failure fields are built in catalog-system ticket 20, now, on the branch.
