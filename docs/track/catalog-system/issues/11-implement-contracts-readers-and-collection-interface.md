# Implement contracts, readers and the collection interface

Type: task
Label: implementation:task
Status: resolved
Assignee: codex
Blocked by: 10

## Outcome

One maintained collect/validate/publish command and explicit format-3/status-1
contracts, schemas and readers, using the accepted document boundaries and domain
meanings. Implement collection and credential-free validation first; ticket 12
completes explicit publication/finalization. Keep format 2 operational.

## Accepted inputs

[Public contract](../public-contract-decision.md), decisions
[05 storage](05-choose-scalable-snapshot-and-history-storage.md),
[06 provenance](06-choose-evidence-bound-recipe-classification-and-provenance.md),
[07 interface](07-choose-one-reusable-collection-interface-and-permissions.md),
[08 health](08-choose-truthful-health-summaries-and-bounded-statistics.md), and
[final targets](10-agree-system-acceptance-and-implementation-roadmap.md#answer--november-8-2026).

## Work and acceptance

- Write executable document kinds/field order, closed schemas and supported
  mapping-only grammar fixtures. Maintain exact decimal IDs, URL/MIME round trips,
  numeric/source-name/app identity checks and explicit absent/unknown semantics.
- Reuse maintained acquisition/normalization/retention/writer/reader modules.
  Live and saved-response collection share the same pipeline; saved replay has no
  credentials/network and preserves original receipt times. Collection emits a
  candidate/report without remote writes or ref advancement.
- Apply successful-source exact-tag replacement and 32-plus-stable retention,
  timestamp fallback, conflict rejection and exceptional overflow preservation.
  Keep format-2 output on its own exact-parent merge/retention rules, from the same
  normalized acquisition input rather than v3's pruned projection.
- Implement four-label provenance predicates on exact architecture/recipe/rule/
  dependency inputs, including unknown and catalogue-only-with-existing-recipe.
  Metadata processing executes no recipes or payloads. Review links use recipe pins.
- Deliver strict shell/awk and browser validation/query support for v3 while v2
  remains unchanged. Lua consumers receive explicit YAML/schema contracts without
  a required new runtime/library. No general plugin framework.
- Run focused shared positive/negative fixtures against writer, shell reader,
  browser validator and editor schemas. Cover rule/version refusal, identities,
  observations, retention, same-tag reuse and every compact encoding boundary.
  Record intentional schema-only checking limits and selection differences.

## Evidence and boundary

Commit source/fixtures locally with exact test commands/results and references to
reused evidence. No broad historical per-app lifecycle suite without affected
behavior. This ticket description is not execution authorization; use the accepted
local implementation scope when separately started. No push, live acquisition,
workflow dispatch, enrollment, installed-host change, Pages or remote publication.

## Answer — November 8, 2026

Implemented locally: closed format-3/status-1 contracts and generated editor schemas,
strict shell/browser readers and fact queries, exact decimal/URL/MIME encodings,
32-plus-stable/exact-tag merging, stable source labels, pinned recipe predicates,
and explicit candidate collection/offline validation. Shared acquisition feeds
independent v2/v3 parent merges; format 2 and the deployed legacy workflow remain
operational. Publication is explicitly reserved for ticket 12 and refuses here.

[Implementation and acceptance](../implementation-11.md) records 9 focused new
checks including 33 shared fixtures across shell/browser/schema boundaries and
mawk/gawk/BusyBox, 71 affected legacy test invocations, shellcheck/whitespace and
an unmocked committed-CLI synthetic replay with zero HTTP/ref advancement.
It documents schema-only limits and intentional retention/selection differences.
No capacity, real-cohort, browser-delivery or deployment qualification is inferred.
No push, live acquisition, dispatch, enrollment, installed-host/Pages change,
remote publication or yadm pointer update occurred.
