# Decide the client freshness rule against the real rotation

Type: grilling
Label: wayfinder:grilling
Status: open
Triage: ready-for-human
Blocked by: none

## Question

The client refuses a selection whose release was observed more than 48 hours
ago (`modules/catalog-yaml-policy.am`, `age>172800`). Collection takes almost
five days to go round all sources. Which of the two changes?

## Evidence — November 16, 2026

- Enrollment: 8,313 sources. Each run attempts 500; 26 of those are the same
  failing sources every run ([ticket 20](20-stop-reattempting-failing-sources-every-run.md)),
  leaving 474.
- Scheduled runs per day on the status branch (`statistics.yaml`): 3, 3, 4, 4,
  4 for November 11 to 15, although the workflow's cron is hourly
  (`17 * * * *`). GitHub starts only that many.
- That is about 1,700 sources a day, a full round in about 4.9 days. Keeping
  every source under 48 hours needs about 4,160 a day.
- `statistics.yaml` at catalog `9e653dd32` (11:45 UTC): 1,896 sources under 24
  hours, 1,904 from 24 to 48 hours, 4,493 at 48 hours or more, 20 never
  collected. So 54% of sources were past the client's limit.
- What the client does with that, measured by running it for every policy key:
  see the usable-selection result in [ticket 16](16-qualify-v3-coverage-expansion.md).
- A refused asset selection prints the exact
  `--commit … --accept-stale-release …` arguments that accept it. A release or
  Git selection (21 policies) has no such override and stays refused.

## Options

1. Raise the client limit to cover the round, for example 7 days. One constant
   in the policy module, plus delivering the module to each installed host.
2. Start runs from outside GitHub's scheduler (a timer on one of Marek's
   machines calling `gh workflow run`). Hourly runs would bring the round to
   about 18 hours. Needs an always-on machine and a token there.
3. Larger batches. The run's own bounds (750 requests, 512 MiB, a 30-minute
   job) cap a batch near 900 sources, a round of about 2.6 days at four runs a
   day: not enough alone.
4. Leave both. More than half of installs and updates then need the manual
   override at any moment.

Marek said on November 9 that freshness is not a target and that the 48-hour
rule may be adjusted. That points to option 1; option 2 can follow.

## Comments

November 16, 2026: opened from the ticket 16 review.
