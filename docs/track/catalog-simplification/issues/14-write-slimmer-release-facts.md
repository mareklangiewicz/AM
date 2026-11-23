# Write the slimmer release and asset facts

Type: task
Label: implementation:task
Status: open
Triage: needs-triage
Blocked by: 04, 09

## Outcome

The collector writes release and asset facts as decided in
[Choose what to catalog per release and asset](08-choose-what-to-catalog-per-release.md)
(derived URLs with exceptions, no `media_type` or `updated_at`, conditional
`created_at` and `title`, `sha256pre`, retention of 8 newest plus newest stable
plus newest with a Linux download), in the layout and encodings tickets 04 and
09 choose; the host modules, the browser and their tests read it.

## Comments

November 23, 2026, from ticket 04: the layout keeps today's per-repository
split, so this ticket writes on the existing `release-catalog-v3` branch; the
move into `main-marek` is ticket 16, after this one and ticket 15.
