# Choose compatibility transition and recovery

Type: grilling
Label: wayfinder:grilling
Status: open
Blocked by: 03, 05, 06, 07, 08

## Question

How can the selected contracts, storage and pipeline replace the present system
without silently breaking existing shell/browser consumers or losing last-good data?

Specify producer/reader compatibility, ordered rollout, old pinned snapshot access,
checkpoint migration/invalidation, recipe/policy revision handling, concurrent
publication and rollback/recovery boundaries. Address public operational summaries
when collection/validation/publication fail independently.
Include the transition from the separately deployed prototype branch to the
accepted main-marek website-code home without losing preview/recovery capability.
Preserve AM app identities, numeric source identities, retained release IDs and
effective release observations. Avoid promising binary rollback from catalog rollback.

Include the accepted app-map transition from numeric values and source filenames
to explicit readable YAML paths, as recorded in
[Choose public YAML contracts and revision consistency](03-choose-public-yaml-contracts-and-revision-consistency.md#accepted-app-to-file-references--november-7-2026).
Cover source/app renames, old numeric-path consumers and old pinned snapshots;
do not silently require existing installed readers to understand the new map.

Compare a small reversible end-to-end summary/browser slice with alternatives.
Identify old code and operational procedures that can actually retire, evidence
that must remain, and unknowns needing a bounded rehearsal. Agree migration gates
and recovery ownership with Marek. This is a plan, not deployment authorization.
