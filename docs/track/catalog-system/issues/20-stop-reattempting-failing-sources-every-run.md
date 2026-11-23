# Stop re-attempting permanently failing sources in every run

Type: task
Label: implementation:task
Status: resolved
Blocked by: none

## Outcome

A source that keeps failing is attempted at a bounded rate instead of in every
run, and the two refusal classes that are the fork's own choice (same-tag
conflicts, the 16 MiB response bound) each have a recorded decision.

## Why

Batch selection sorts sources by the `attempted_at` of their retained document
(`host_catalog.collect`). A failed attempt writes no document, so a source that
never succeeded sorts first forever, and one that starts failing keeps its last
successful time and drifts to the front. Measured on the status branch for
runs 43771598884, 43794093773 and 43857712579 (November 15 to 16, 2026): the
same 26 sources failed in all three, 26 of each run's 500 attempts.

| Sources | Cause | Note |
| --- | --- | --- |
| 14 | `same_tag_conflict`: GitHub returns two releases with one tag | Refused by the collector's own rule |
| 2 | Response over the 16 MiB bound (`VSCodium/vscodium`, `wekan/wekan`) | Refused by the collector's own bound |
| 10 | HTTP 404 | 8 are in the first upstream merge's `sources_to_retire`; `Odrannnn/MetroidPrimePort` and `xxx-holic/wishtoken-desktop` are not |

Twenty of the 26 never had a successful collection
([final audit](../github-coverage-final-audit-16.json)); six succeeded once and
have failed since. The set only grows as repositories disappear.

## Scope

- Record the time of a failed attempt where selection can see it, so a failing
  source rotates with the rest or backs off. Failure must still leave the
  retained facts and their times untouched.
- Decide the same-tag rule with Marek: keep refusing the whole source, or keep
  both releases under their own release ids (the format already keys releases
  by id) and let client selection choose.
- Decide the two oversized sources with Marek: raise the bound for named
  sources, collect fewer pages for them, or leave them out.

Pushing, the schedule pin and any change of the published format need Marek's
authorization.

## Comments

November 16, 2026: opened from the ticket 16 review.

November 22, 2026: Marek decided. Failed attempts rotate: a failure's time
counts for selection like a success, so a failing source is retried once per
full cycle (no backoff, no auto-retire). Same-tag conflicts keep the newest
release per tag (latest published time, ties to the higher id), no format
change. The two oversized sources get smaller pages (fewer releases per
request, named sources only); the 16 MiB bound stays.

November 23, 2026: the same-tag line above is withdrawn. "Keep newest" would
have contradicted ADR 0002, and Marek then chose a facts-only catalog instead:
the same-tag question moved to the simplification map's
[Record same-tag and removed releases as facts](../../catalog-simplification/issues/07-same-tag-and-removed-releases-as-facts.md).
Rotation and smaller pages for the two oversized sources stand.

November 23, 2026: the rotation's storage is revised (simplification ticket
[04](../../catalog-simplification/issues/04-choose-catalog-directory-layout.md)).
Instead of a `failed_attempts` map in `status.yaml`, each repository file gets
optional `failed_at` and `failed_with` (a cause code from a schema enum, the
list settled in simplification ticket 11), present only while the latest
attempt failed and removed on the next success. Selection sorts by the newer of
`collected_at` and `failed_at`. Build it now, on `release-catalog-v3`, as a
repository-format change (`ship --repin-schemas`); the later move into
`main-marek` carries it.

November 23, 2026: implemented, not yet shipped. Repository documents get
optional `failed_at`/`failed_with` (`not_found`, `same_tag_conflict`,
`too_large`, `invalid_response`, `transport`); a never-collected source gets a
document of identity, failure and `releases: {}` (Marek, same day), which host
selection refuses as `no_matching_asset`. Run-wide stops (budgets, quota,
authentication) record nothing. Selection sorts by the newer of `collected_at`
and `failed_at` (`incremental.decode`). `VSCodium/vscodium` and `wekan/wekan`
request 30 releases per page (`host_catalog.PAGE_SIZES`): a 10-release page
measured about 3 MB for each (about 300 KB per release), so 100 is about 30 MB,
30 about 9 MB. Both readers (awk, page) enforce the field pairs; the page shows
"Never collected" and the failed attempt. Tests: `test_failed_attempts.py` and
the page's navigation e2e. Ships with `--repin-schemas`.

November 23, 2026: shipped at `6dbb33736` (Long tests 45268579816, Fast run
45274936247 and catalog run 45274946865 green, both pins moved). The first
catalog under it (`a8922b396`) records 27 failing sources: 13 `not_found`,
14 `same_tag_conflict` (16 of them new never-collected documents, 8,288 files).
`VSCodium/vscodium` and `wekan/wekan` collected successfully with `page_size: 30`.
