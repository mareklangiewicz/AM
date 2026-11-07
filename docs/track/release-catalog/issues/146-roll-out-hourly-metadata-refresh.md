# Roll out bounded hourly metadata refresh

Type: task
Status: resolved
Triage: ready-for-agent

Marek said “go on” after the completed 224-source publication and 500/hour
assessment. Continue the profile through implementation, validation and rollout.
Keep metadata independent of recipe migration and installed applications.

Implement 500 attempts/hour, 512 MiB transfer, 900-second cooperative acquisition,
30-minute job, safe quota diagnostics and a 100-request primary reserve. Validate
a bounded 256 MiB local history allowance against the measured published history
and 500-source fixture. Preserve exact-parent publication, observation semantics,
2 MiB documents, the 1,024-file reader and actual 224-source enrollment. The
measured enrollment ceiling may rise to 500; new identities still require explicit
verification and cohort preflight. This is
not qualification for thousands or permission to invent new source identities.

Report actual requests, bytes, durations, success/coverage and explicit stop
reasons, including rate/auth and local budgets. Validate the whole enrolled scope
and verify the actual workflow's published pin before recording completion.


## Answer

Source `09ae7fe81355a06eabe1c2afc141f22e2d3de675` is pushed. All 159 full
collector regressions pass, plus final focused/main/enrollment checks.
[Run 42366263140](https://github.com/mareklangiewicz/AM/actions/runs/42366263140)
succeeds: 224 GETs / 224 successes, zero failures/unattempted, 179,326,726 bytes,
205.27-second command. Exact pin `59b3f3f398bc1013c7b5caf0f37b19a4f3fc9821`
and its actual parent pass canonical reader, identity and retained-observation
preservation. No new identities are enrolled; the ceiling is 500, actual scope 224.

[Rollout report](../research/hourly-refresh-rollout.md) and portable receipts
record the 256 MiB history qualification, safe quota diagnostics/reserve, actual
5,000 core header allowance and reset change. Official ordinary Actions baseline
remains 1,000/hour for planning; observed allowance's cause is unresolved.
The workflow is active with hourly cron; its first natural hourly trigger is
unobserved. Installed files, recipes, app binaries, website and yadm are unchanged.
Broader attribution/storage remains with 138.
