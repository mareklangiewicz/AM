# Retry transient `gh` failures in release.py

Type: task
Label: implementation:task
Status: claimed
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

## Implementation

`retrying(run)` in `tools/release/release.py` wraps the runner `main()` hands
to `plan`, `ship` and `watch`: a failing `gh` call is tried up to `ATTEMPTS`
(3) times, `RETRY_SECONDS` (10) apart, then raises `failed (CODE) after 3
attempts: COMMAND`. Two calls are tried once. One is `git`, whose exit codes are
answers (`merge-base --is-ancestor`). The other is `gh workflow run`: a failed
reply can hide a run that already started, and a second try would dispatch
another catalog run. Tests in `test_release.Retrying`: one failure then
success, three failures raising with the command named, the two single-try
calls, and `main(['watch', ID])` surviving a failed `gh run view` (the
November 24 failure).

Resolve once a real `plan`, `ship` or `watch` is seen recovering from a
transient failure, or after a few ships with none seen.
