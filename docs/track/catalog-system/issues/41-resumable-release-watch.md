# `release.py watch` can resume

Type: task
Label: implementation:task
Status: resolved
Blocked by: none

## Outcome

`tools/release/release.py watch [RUN_ID ...] [--minutes N]` watches runs
that `ship` started (or the runs on `origin/main-marek`'s HEAD when no id is
given) and exits 0 only when they all succeeded. A `ship --watch` that ran
out of time can be continued instead of being judged by hand with `gh run
view`.

## Why

Retro of the ticket 22/38 session, third item. `ship --watch 9` exited 1 on
a run that later passed: the deadline, not the run, decided the exit code,
and nothing could pick up where it stopped. Long watches now run in the
background with `--watch 30`.

## Scope

- Reuse the existing `watch` function; `ship --watch` calls the same code.
- A deadline exit says that the runs are still in progress and prints the
  `watch` command that continues it, so the message differs from a failed
  run.
- Tests in `tools/release/test_release.py` against scripted `gh` replies.

## Comments

## Answer — November 19, 2026

`tools/release/release.py watch [RUN_ID ...] [--minutes N]` (default 30).
Without ids it watches the newest run of each workflow on the commit
`origin/main-marek` points at. `watch` (and `ship --watch`) exits 0 when all
runs are green, 1 when one failed (also when another is still running at the
deadline), and 3 when the deadline came first with nothing failed; its last
line is then the `watch` command for the runs still going.

Tests: `tools/release/test_release.py` `Watch` and `Resume`, on scripted `gh`
replies. Mutants that report a failure as still running, list finished runs
in the continue command, or pick an older run of the same workflow each fail
them (the last one survived at first; a test with two Fast tests runs on one
commit was added). Run for real: `watch --minutes 1` found Fast tests
44512967029 on `5a4ee43ec` (green, exit 0), and so did `watch 44512967029`.

November 19, 2026: shipped with Marek's approval as part of `6ff1c94fa` (Long tests 44514966125 on `ci/release-watch`, Fast tests 44516166447 green; no repin). `release.py plan` and `watch` were used for real in that ship.
