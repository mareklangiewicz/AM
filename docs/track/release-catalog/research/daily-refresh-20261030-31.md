# Natural daily refresh observation — October 30–31, 2026

Read-only verification on October 31 at 17:46 UTC closes ticket 64's remaining
observation. No dispatch, source push, repin, enrollment or host operation was
performed. The six-source operational scope is unchanged.

## Observed runs

| Date | Scheduled controller | Collector/publisher child | Controller created (UTC) | Publication |
| --- | --- | --- | --- | --- |
| October 30 | [41038460711](https://github.com/mareklangiewicz/AM/actions/runs/41038460711) | [41038483568](https://github.com/mareklangiewicz/AM/actions/runs/41038483568) | 10:07:49 | `d8d985e969989e9703e4b55d44572444394cb1fe` |
| October 31 | [41189888365](https://github.com/mareklangiewicz/AM/actions/runs/41189888365) | [41189898522](https://github.com/mareklangiewicz/AM/actions/runs/41189898522) | 09:44:06 | `067f236b205d8fe01c6f4e79744887e4979437fc` |

All four runs completed successfully at source revision
`1d3253c5f2a82c74319d8188b02d5361457beb7b`. Controller metadata records
`event=schedule`; logs record `17 3 * * *`, the matching approved source revision,
and `dispatch_submitted` immediately before each child. The children themselves
correctly use `workflow_dispatch`. Controller creation lagged the nominal 03:17
UTC schedule by about 6 hours 51 minutes and 6 hours 27 minutes respectively.
These observations establish working daily execution, not punctual scheduling.

Both runs attempted and completed exactly six requests with prior ETag conditions;
the two latest-release requests also carried Last-Modified conditions. All twelve
responses were HTTP 200, with no 304 responses or retained-failure observations.
The second run's observation validation times span
`2026-10-31T09:44:29.120365+00:00` through
`2026-10-31T09:44:32.974674+00:00`. At verification, its oldest observation was
28,923.53 seconds (about 8 hours 2 minutes) old, within the inclusive 48-hour policy.
The first run's observations were also still fresh, about 31 hours 38 minutes old.

## Publication verification and retained evidence

The first publication's parent is
`3cb2bada61744479531b7093d6cf3167c463cf36`; the second publication's parent is
the first publication. Both match the controllers' recorded previous publication
and the collection reports. The current `release-catalog` ref was observed at the
second publication.

Downloaded collection/publication artifacts for both children and read their
public Git commit/tree objects. For each publication:

- Validated the complete candidate with `storage.validate` and recomputed
  `lookup.tsv` with `shell_lookup.render`.
- Compared publication index SHA256 and total tree bytes with the candidate.
- Checked the collection ZIP SHA256 against the publisher's recorded artifact
  digest, and fetched the exact tree object named by the published commit.
- Checked the exact single parent and all eight published blob paths, sizes and
  Git blob SHA1 values against the candidate bytes; the recursive tree was complete.

[Retained evidence](daily-refresh-20261030-31-evidence.tar.gz) contains both original
collection/publication ZIP pairs, public commit/tree API responses and
`verification.json` with per-request conditions, outcomes, timestamps, hashes,
publication relationships, sanitized dispatcher results and verification ages.
Raw dispatcher logs were inspected locally; only their public result fields are
retained. No credentials are included. Freshness above is a timestamped observation,
not a continuing availability guarantee.
