# Sparse cadence is upstream of workflow execution

Ticket [39](../issues/39-diagnose-scheduled-cadence.md). Read-only diagnosis on
2026-10-28, captured after 09:46Z. No schedule/settings/source changes, extra
workflow dispatches, release requests or app operations.

## Finding

The available evidence localizes the symptom to GitHub schedule-event/run
creation, before our dispatcher executes. It does not establish GitHub's internal
reason for omitted/delayed events. Treat service-side delay/drop as the leading
explanation, not a confirmed incident/root cause.

The approved window starts 00:12:16Z and cron is `17 * * * *` (UTC). Ten nominal
slots elapsed from 00:17 through 09:17. Both the complete workflow-specific run
listing and a repository-wide event=schedule query return exactly one run:

| Boundary | Observed UTC time | Implication |
| --- | --- | --- |
| Schedule registered active | 00:12:02 | File was registered before first nominal slot |
| Schedule armed | 00:12:16 | Source/window valid before first nominal slot |
| Sole run created | 05:54:26 | Run creation itself is sparse/off-minute |
| Run started | 05:54:26 | No measured created-to-start runner queue |
| Dispatcher job began | 05:54:28 | Two seconds after run creation |
| Child created/started | 05:54:36 | Dispatch succeeded promptly |
| Dispatcher job completed | 05:54:39 | Controller completed in 11 seconds |
| Scheduled run updated/completed | 05:54:40 | No hour-scale controller execution |
| Child completed | 05:55:07 | Collection/publication worked |

There are no listed failed, skipped, cancelled, pending or queued schedule runs.
The sole event is 37m26s after the closest preceding nominal slot (05:17), but the
API does not expose which original slot generated it. Do not claim an exact
per-slot delivery delay or distinguish dropped from still-delayed events.
Deleted/unexposed run history cannot be independently ruled out by these public
listings; no evidence suggests deletion here.

## Hypotheses checked

| Hypothesis | Prediction | Evidence/result |
| --- | --- | --- |
| GitHub schedule delivery delay/drop | Missing run records despite valid active cron | Fits both independent list queries; leading explanation |
| Our revision/window/job guards | Skipped jobs or failed controller runs | No such runs; actual source equals pin and window still valid |
| Runner capacity or workflow concurrency | Queued runs or long run/job start delay | None listed; existing run/job starts in 0/2 seconds and succeeds |
| Wrong branch/cron or disabled configuration | Drift in remote file/default/state/history | Remote default main-marek, correct hourly cron, active workflow, sole installation commit |

Current remote source equals approved 466e1facc; local unpushed commits cannot
change GitHub's job guard. Window remains 00:12:16Z October 28 to exclusive
00:12:16Z October 29. Repository Actions enabled, repository unarchived. Workflow
created/updated once at activation and cron history has one installation commit.
The six unrelated workflows remain disabled; only dispatcher and collector active.
Recent registration and successful actor-triggered schedule run make the 60-day
inactivity and permanently unavailable actor explanations inconsistent with the
observed initial pilot. Later actor-state changes cannot be proved absent solely
from these API records.

## Reproducible signal and verification limit

[Captured cadence check](scheduled-cadence-check.json) records exact expected slots
and run timestamps. The archived `replay.py` is deterministic against captured
files and was run twice:

```text
python3 /tmp/am-cadence-diagnosis/replay.py
Expected 10 hourly slots; observed 1 scheduled workflow run(s).
AssertionError: Sparse schedule event creation (allowing one recent pending slot).
```

This replays the observed symptom, allowing one most recent pending slot; it does
not reproduce or control GitHub's scheduler. Minimization to scheduled-run history
alone rules out downstream collector state as a necessary element of the symptom.
There is no repository seam that can unit-test/fix GitHub event delivery. No fake
passing regression test, speculative cron change, schedule repin or new dispatch
was added. The diagnostic intentionally stays red for this retained history.
The earlier capture command had a trailing-slash repository API 404, corrected
in the diagnostic script; production controller already uses the correct route.

## Primary sources and recommendation

[GitHub troubleshooting](https://docs.github.com/en/actions/how-tos/troubleshoot-workflows)
explicitly documents delayed schedule events and dropped queued jobs under load.
[Schedule semantics](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
confirm UTC/default-branch behavior and inactivity rules. Minute 17 is already
away from the documented top-of-hour load peak. Changing its minute again, or
removing the extra dispatcher job, cannot be justified as a fix for absent runs.

[GitHub status API](https://www.githubstatus.com/api/v2/status.json) reported all
systems operational (page updated 09:21Z). Returned
[incident history](https://www.githubstatus.com/api/v2/incidents.json) did not show
an overlapping Actions scheduling incident; this does not rule out a GitHub-side
issue affecting this repository. No internal scheduler/audit telemetry is available
here to prove load, a platform defect or exact drop reasons. GitHub Support can use
repository/workflow/run IDs and timestamps from this record to investigate.

For strict hourly collection, use a reliable external timer that submits the
same guarded manual workflow, with explicit scoped credentials, monitoring and
an approved request budget. This is a future design choice, not implemented or
authorized by this read-only analysis. For best-effort Actions-only operation,
keep freshness refusal and separately monitor last successful observation age;
cron configuration by itself is not proof that refreshes happened. Leave current
pilot limits/expiry unchanged and assess actual interval distribution at shutdown.

[Exact evidence archive](scheduled-cadence-diagnosis-evidence.tar.gz), SHA256
`1937db4eaba5f359625edf1137f2be47657d4481e08fe1d5ad3cc5e3bfa3d28c`,
contains raw read-only API metadata, configuration, run/job timing, both query
results, capture/replay scripts, source notes and replay result. No credentials
are recorded. No production implementation change or whole-suite rerun needed.
