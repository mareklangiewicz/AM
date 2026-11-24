# Decide which commit pins are needed

Type: grilling
Label: wayfinder:grilling
Status: open
Blocked by: 01, 04

## Question

Which commit hashes in the catalog and status (schema URLs, `inputs`, recipe,
rules and module bindings in provenance, input/output catalog per source) have
a clear benefit once the catalog is a directory of `main-marek`, and how is each
remaining one inherited down the structure instead of repeated?

## Comments

November 23, 2026, from ticket 04: catalog and code share one `main-marek`
commit, but `catalog.yaml`'s `inputs` record the code commit the collector ran
at, an ancestor of the catalog commit, not the same one. Decide whether that
pin is still needed.

November 24, 2026, from ticket 10: the schema URL pin is decided there (a
relative `$schema:` path, no hash, once the catalog is in `main-marek`). Left
for this ticket: whether `inputs.schemas` and `CATALOG_SCHEMA_REVISION` are
still needed, given that a catalog commit's `schemas/` can be newer than the
contract the collector validated against.
