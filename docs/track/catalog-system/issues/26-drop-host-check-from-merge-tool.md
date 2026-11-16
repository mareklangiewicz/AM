# Drop the host check from the upstream merge tool

Type: task
Label: implementation:task
Status: resolved
Blocked by: none

## Outcome

`tools/upstream-merge/merge.py` no longer reads `/opt/*/remove`; the receipt
has no `installed_here_deleted` or `installed_here_fell_back`; README and tests
follow.

## Why

The merge is about the repo. The check covered only the machine running the
plan, and it is what gave three installed recipes their own handling in the
first merge. A fallen-back recipe still installs and updates as an original, so
nothing replaces the check for now. Decided in
[ticket 24](24-simplify-and-unify-catalog-process.md#answer--november-16-2026).

## Comments

## Answer — November 16, 2026

`merge.py` no longer has `installed()`, the `apps_directory` and `host_arch`
parameters of `prepare`, or the two `installed_here_*` attention keys; the
README entry is gone. `unittest discover -s tools/upstream-merge` passes (15
tests); no test referenced the check. The committed receipt of the first merge
keeps its two keys as history. `plan` was not re-run against a new upstream
revision.
