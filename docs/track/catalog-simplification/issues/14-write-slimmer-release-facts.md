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
plus newest with a Linux download, all counted as tags per
[ticket 07](07-same-tag-and-removed-releases-as-facts.md)), in the layout and encodings tickets 04 and
09 choose, with the times decided in
[Simplify the catalog's times](06-simplify-catalog-times.md) (one repository
`observed_at`, no `collected_at`, no Git ref/file times, no `created_at`, no
provenance `evaluated_at`) and its page text; the host modules, the browser and
their tests read it.

## Comments

November 23, 2026, from ticket 04: the layout keeps today's per-repository
split, so this ticket writes on the existing `release-catalog-v3` branch; the
move into `main-marek` is ticket 16, after this one and ticket 15.

November 24, 2026, from ticket 06: the times above, and 06's page sentences for
"Last seen". `created_at` is now dropped outright, superseding 08's conditional
`created_at`.

November 24, 2026, from ticket 07: retention counts tags, keeping every release
ID under a kept tag (twins stay together). Twins, no tag replacement and
proven-gone removal ship earlier, in ticket 18, on today's format.

November 24, 2026, from ticket 18: also drop `same_tag_conflict` from the
`failed_with` enum (read-only since 18; check that no live document still holds
it) and rename the `retention` constant to `32-plus-stable-v2` (or whatever the
tag-counted retention is named).

November 25, 2026, from ticket 09 (now unblocked): also whole-`url:`
exceptions instead of `download_base`/`url_suffix`, plain status integers
without `state`/`value`, Git maps keyed by quoted name/path, no absent
provenance rows or `availability`, and no `retention`, `page_size` or
`pages_fetched` (which settles ticket 18's deferred rename: the constant goes).
