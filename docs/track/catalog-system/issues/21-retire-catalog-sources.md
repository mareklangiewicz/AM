# Retire catalog sources no recipe selects from

Type: task
Label: implementation:task
Status: open
Blocked by: 18

## Outcome

A source can be taken out of collection enrollment. Its documents leave the
next published snapshot, earlier snapshots keep them, and its source name is
never reused. The sources the first upstream merge lists are retired this way.

## Why

[ADR 0005](../../../adr/0005-upstream-authoritative-converted-recipes-derived.md)
says a recipe upstream deletes takes its source out of collection enrollment.
Today that cannot be done: `host_catalog.collect` refuses a batch when the
published catalog retains a source the enrollment no longer has ("batch would
discard retained sources"), and nothing moves a name from `active` to `retired`
in `tools/catalog-collector/source-names.json`. The upstream merge therefore
leaves such sources enrolled and only names them, under `sources_to_retire` in
its receipt.

## Scope

- An explicit retirement step: remove the enrollment row, move the source name
  to `retired`, and let collection drop exactly those retained documents. A
  source missing from enrollment without that step still refuses.
- Retire the merge receipt's `sources_to_retire`, and the am-utils source
  (repository 1225768109) once no recipe uses it: upstream moved the am-utils
  recipes to "am-extras" (`0a221879c`), and the receipt cannot see that source
  because those recipes carry no policy rows.
- Remove the then-unused am-utils policy (`am_utils_recipe` in
  `modules/catalog-yaml-policy.am`) and its reference data.

Pushing, the schedule pin and delivering the changed policy module to an
installed host need Marek's authorization.

## Comments

November 16, 2026: opened from tickets 16 and 18.
