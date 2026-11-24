# Simplify the YAML encodings

Type: grilling
Label: wayfinder:grilling
Status: resolved
Blocked by: 01, 08

## Question

Which format-3 and status-1 encodings survive once ticket 08 has removed the
derivable data: media type aliases and `=` escapes, omitted defaults, `state`/
`value` wrappers on counts and metrics, numeric-id map keys, reason codes
(`source_validation` hides a same-tag conflict)? Target: a YAML file a person can
read without the spec.

## Answer — November 25, 2026

Marek's answers, one grilling round. Rows E1–E13 are ticket 01's inventory
(catalog `a8ee4e2fe9`); media-type aliases and `=` escapes (E2–E4) went with
`media_type` in ticket 08, the omitted `observed_at` default (E5) is ticket 06's.

- **URL exceptions (E1)**: a URL that differs from the one derived from
  repository, tag and name is stored whole as `url:`; the field's presence is
  the exception. `download_base` and `url_suffix` go.
- **Status numbers (E6)**: plain integers, omitted when unknown; no
  `state`/`value` wrappers. Which numbers remain is ticket 11's.
- **Git maps (E8)**: keyed by the quoted ref name or path instead of its
  SHA-256; the inner `name` and `path` fields go (5 Git-scope sources).
- **Provenance (E10)**: an architecture without a recipe is not listed;
  `availability` goes (23,872 of 33,796 bindings were absent rows).
- **Constants (E12, E13)**: `retention`, `scope.page_size` and
  `scope.pages_fetched` go; `history_complete` stays (the page reads it; it is
  ticket 18's removal proof). This settles the retention rename ticket 18
  deferred.
- **Release and asset IDs (E7)**: stay quoted decimal keys, ordered numerically.
- **Grammar (E9)**: unchanged (mappings only, fixed order, two-space indent,
  quoted dynamic keys, `{}`, exact decimals, the closed escape set, no
  comments), plus ticket 10's `$schema` first key. It is the short grammar doc
  ticket 10 kept; status reason codes and `details` values stay with ticket 11.

Implementation: all format changes join
[ticket 14](14-write-slimmer-release-facts.md) (the format changes once); the
grammar doc is [ticket 20](20-author-catalog-schema-in-yaml.md)'s.
