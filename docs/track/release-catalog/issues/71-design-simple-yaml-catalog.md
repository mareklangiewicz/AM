# Design a simple YAML catalog of release facts

Type: research
Status: claimed
Triage: ready-for-agent

Interview Marek to settle normalized catalog facts, a strict readable YAML subset, client selection responsibilities, and collection coverage. Implementation requires confirmation of shared understanding at the end of the grilling interview.

## Decisions and evidence

See [ongoing design interview](../research/yaml-format-design.md) and [facts/selection ADR](../../../adr/0001-catalog-facts-and-client-selection.md).

Q21 authorizes a bounded read-only measurement of release-history request cost, response bytes, provisional normalized YAML size, and duration. No workflow dispatch, production publication, repin, or push is authorized by this experiment. The separate natural daily run acceptance remains outstanding.

## Remaining

- Bounded history measurement completed; full published release history chosen, subject to explicit ceilings. Finalize ceilings using broader evidence.
- Settle failure handling, optional values, schema details, reader interface, and remaining design branches.
- Confirm shared understanding before implementation or reader prototype.
