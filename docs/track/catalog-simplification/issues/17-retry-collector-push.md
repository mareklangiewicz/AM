# Retry the collector's push after a rejection

Type: task
Label: implementation:task
Status: open
Triage: needs-triage
Blocked by: none

## Outcome

When the collector's push to `main-marek` is rejected because the branch moved,
it fetches, rebases its `catalog/`-only commit and pushes again, a bounded number
of times, then fails visibly; a test shows a rejected push racing a code commit
ending with both. Decided in
[Choose the catalog directory layout in main-marek](04-choose-catalog-directory-layout.md).
