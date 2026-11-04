# Prepare scoped YAML collection with shared transport budgets

Type: task
Status: resolved
Triage: ready-for-agent

Continue 88 with finite/all-page orchestration using existing collector and
transport, validated numeric pagination and atomic retained merges. Keep a shared
request/byte/elapsed budget across pages and sources. Test offline rollback,
finite scope, EOF, budget stops and transport-wide stops. No live requests,
workflow changes, catalog publication, repin or installed changes.

## Answer

Candidate `2f9292218` on `prep/yaml-offline-publication` implements finite/all
pagination with shared transport budgets and source-atomic retained merges.
[Findings](../research/yaml-scoped-transport-adapter.md) record 19 adapter,
21 supervised-transport, 17 collector and six attempt-adapter passing checks.
No operational integration or live action occurred.
