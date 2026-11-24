# Retry transient `gh` failures in release.py

Type: task
Label: implementation:task
Status: open
Triage: ready-for-agent
Blocked by: none

## Outcome

`tools/release/release.py` retries a failing `gh` call a bounded number of
times with a short pause before raising, so `plan`, `ship` and `watch` survive
a transient GitHub API error; a test shows one failure followed by success
completing, and repeated failures still raising with the command named.

## Why

November 24–25, 2026, three transient failures in one session: `gh variable
get CATALOG_SCHEDULE_REVISION` returned HTTP 401 "Bad credentials" with a valid
keyring login (the retry succeeded), `ship` failed looking up the run of a push
it had just made (the push had landed), and `watch` died on `gh run view` while
the run was still in progress. Each needed a manual check and rerun.
