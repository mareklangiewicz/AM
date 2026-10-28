# Daily catalog refresh and 48-hour freshness

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Marek accepted daily final scheduling with a 48-hour freshness limit, retaining
failure ages and exact stale consent. Implement local code/tests/docs now; finish
the current hourly pilot before switching remote scheduling. Daily cadence is
03:17 UTC, same six sources, no external timer. Keep source/ref/manifest guards,
serial collection, no retries and separate publisher. Remove hourly-pilot-only
window/count controls from the final daily controller. No host app operation.
Remote activation after the pilot's planned shutdown is authorized by this
acceptance; do not ask again for this same change. Do not repin mid-pilot.

## Implementation notes

Daily cron is 17 3 * * * UTC. Final controller removes the 24-hour activation
window and observed-24-run pilot cap; it retains exact repository/event/cron/
source revision, current remote source, workflow isolation, no active collector,
full prior pin, rerun refusal and no dispatch retry. Existing collector/publisher
are unchanged. Daily scheduling is ongoing after separately recorded activation,
with nominal six upstream requests/day and existing transfer/job bounds.

Shell and Python readers use inclusive 172,800-second measured freshness. Both
still refuse future/unavailable/corrupt data and bind stale consent to exact
publication/request/body. No timestamp is rewritten. Tests exercise 36-hour
acceptance, exact 48-hour acceptance, one-microsecond-late refusal, post-transfer
expiry and stale tuple binding across two actual temporary Git publications.
The latter now derives its stale clock from the newest observation instead of
a hardcoded date, so both generations are truly stale under the new policy.

[41](41-activate-daily-refresh.md) records the already authorized remote switch and
user-run installed-helper delivery after ticket 37 closes the existing pilot.
No remote schedule/variable/source, installed helper or app changed in this work.

## Answer

Implemented and verified locally. **118 tests pass** in 53.194s. Shell syntax,
reader ShellCheck, workflow YAML validation and diff checks pass. Remote activation
remains ticket 41 after the approved hourly pilot closes; no repeat permission
needed. Installed users retain the old limit until the helper is delivered.
