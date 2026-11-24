# Record twins and drop proven-gone releases

Type: task
Label: implementation:task
Status: claimed
Triage: needs-triage
Blocked by: none

## Outcome

On today's format, as decided in
[Record same-tag and removed releases as facts](07-same-tag-and-removed-releases-as-facts.md):

- The collector records every returned release under its own ID even when tags
  repeat; `retention_v3.merge` no longer raises `same_tag_conflict` nor replaces
  an older release ID with the same tag.
- A retained release missing from a fetch that reached the end of the history
  is removed; otherwise it keeps its `observed_at` (corrected, see Comments).
- The host parser drops its "duplicate exact tag" check; the page lists twins as
  separate entries.
- `same_tag_conflict` leaves the `failed_with` enum (schemas, host tables);
  ships with `release.py ship --ci NAME --repin-schemas`.
- Tests show the 14 twin sources' shape (two IDs, one tag, split assets)
  collecting, a recreated tag keeping both IDs while upstream lists both, and a
  deleted release removed only on proof.

The 14 stuck repositories should collect on their next turn; confirm in the
first catalog run after shipping.

## Comments

November 24, 2026, during implementation: two parts of the Outcome are deferred
to [ticket 14](14-write-slimmer-release-facts.md), which already changes the
format once. Dropping `same_tag_conflict` from the `failed_with` enum, and
renaming the `retention` constant `32-plus-stable-exact-tag-v1` (agreed:
`32-plus-stable-v2`), both narrow the contract. `release.py ship
--repin-schemas` validates the live catalog under HEAD's contract first, and the
live catalog fails both: `catalog.yaml` carries the old constant, and 14
repository files carry `same_tag_conflict` until they are recollected, about 17
runs away. So this ticket ships widening only: collection never writes
`same_tag_conflict` (`build.py` marks it read-only), and the generated schemas
and tables are unchanged, so no repin is needed.

November 24, 2026, Marek's choice during implementation: removal needs a
complete history only. GitHub's list is not strictly newest-first, so the
"returned an older release" proof from ticket 07 was unsound (ticket 07's
Comments have the numbers).

November 24, 2026: shipped at `78e290935` (`release.py ship --ci twins-18
--repin-schemas`; Long tests 45404830517, Fast run 45433403536, catalog run
45433417508 and page deploy 45439666753 green). The page deploy was dispatched by
hand: `release.py` compares only the deployed definitions
([catalog-system ticket 47](../../catalog-system/issues/47-release-compares-every-deployed-browser-file.md)).
The live `reader.mjs` now equals HEAD.

First catalog under it, `3f309f260` (`scripts/18/removed.py 3fd57907b
3f309f260`): of 500 collected repositories, every missing release is accounted
for: 136 dropped by the 32-release cap, 105 removed by a complete history, none
without proof. Per-release `observed_at` overrides fell from 612 to 522. The
first twin is a recreated tag, `xLightsSequencer/xLights` `nightly`: new ID
456350789 seen now, old ID 453465231 kept with its last-seen time. None of the
14 twin repositories was in this batch (they failed on November 23, so rotation
reaches them later); this ticket stays claimed until they collect.
