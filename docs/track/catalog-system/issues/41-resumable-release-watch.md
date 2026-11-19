# `release.py watch` can resume

Type: task
Label: implementation:task
Status: open
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
