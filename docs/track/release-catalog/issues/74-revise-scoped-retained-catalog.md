# Revise scoped collection and retained release observations

Type: prototype
Status: resolved
Triage: ready-for-agent

Apply Marek's explicit November 3 design revision to schema, ADR/glossary,
consolidated design, chronology and resource strategy. Update the isolated reader
and offline merge experiment for source subset, page size 1–100, positive page
limit or all, default one-page collection, per-release observed_at and atomic
failure retention. Specify exact full-history reconciliation semantics.

No deployment, workflow dispatch, push, source repin or installed-host mutation.

## Answer

Schema, glossary, ADR 0002, consolidated review, chronology, spec/map and resource
strategy now separate requested scope, retained releases and release observation
time. Scheduled defaults are all sources / 100 releases per page / one page.
Fetched records replace old facts, unfetched records and timestamps survive,
and scope failure commits no staged observations. Selected-release observed_at
controls installation freshness. Retained-size/memory bounds remain unresolved.

The exact local reconciliation proposal defaults to retention, even after all;
explicit reconciliation requires successful all scope and removes only absent
IDs, atomically with that refresh. Partial absence cannot delete. Both attempt
and last-success metadata record the reconciliation flag.

[Findings and reproducible matrix](../research/yaml-retention-revision.md).
Prototype branch: research/yaml-retained-observations at
4600ae0840b1ec516db9e77eda984e2fc53e6297, under tools/catalog-yaml-prototype/.
Sixteen unique groups pass on mawk/GNU awk/BusyBox; syntax, lint, examples and
whitespace checks pass. No production integration, network collection, workflow
dispatch, push, repin or installed-host mutation. Ticket 71 stays open for resource
bounds and implementation.
