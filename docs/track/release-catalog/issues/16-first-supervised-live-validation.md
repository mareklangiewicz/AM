# First supervised adapter live validation

Type: task
Status: claimed
Triage: ready-for-agent

## Authorization and bounds

Marek explicitly approved pushing the enrolled manifest, installing/pushing the
prepared manual-only workflow and running it once. Enrollment commit e0d8e61a2
is included. Exactly six serial numeric release GET attempts at most; no redirects,
retries, pagination, endpoint fallback, schedule, publication or installer change.
The current manifest SHA256 is
`1c550b882e9855a7a652e44516d88db95046641da92f4b6e34fd65b9a6da87b9`.
Record the full resulting pushed source/workflow commit before dispatch.

## Pre-dispatch control-plane check

GitHub reports AM ID 1291019762, default main-marek, Actions enabled. Five unrelated
workflows remain disabled_manually. The historical Catalog quota probe is active,
manual-only; no run is pending in the recent list. Install the approved manual
collector, then disable the historical probe so only the current collector is active.
No upstream release endpoint was read by these control-plane checks.

## Acceptance

- Verify exact source, workflow and manifest revisions plus offline checks.
- Verify server-side isolation; dispatch exactly once with approved inputs.
- Retain bounded public evidence, inspect all attempted/not-attempted endpoints,
  route statuses, quota and timing; distinguish transfer from release validation.
- Record failure without automatically retrying; no further dispatch is authorized.
