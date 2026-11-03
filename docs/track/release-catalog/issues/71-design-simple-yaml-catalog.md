# Design a simple YAML catalog of release facts

Type: research
Status: open
Triage: ready-for-agent

Interview Marek to settle normalized catalog facts, a strict readable YAML subset, client selection responsibilities, and collection coverage. Implementation requires confirmation of shared understanding at the end of the grilling interview.

## Decisions and evidence

See [ongoing design interview](../research/yaml-format-design.md) and [facts/selection ADR](../../../adr/0001-catalog-facts-and-client-selection.md).

Q21 authorizes a bounded read-only measurement of release-history request cost, response bytes, provisional normalized YAML size, and duration. No workflow dispatch, production publication, repin, or push is authorized by this experiment. The separate natural daily run acceptance remains outstanding.

## Remaining

- Bounded history measurement completed; full published release history chosen, subject to explicit ceilings. Finalize ceilings using broader evidence.
- Policy interview decisions settled; see [consolidated review](../research/yaml-catalog-design-review.md). Exact grammar and budgets are the next experiments after confirmation.
- Shared understanding confirmed; schema/reader experiment completed in ticket 72.
- Unicode escape extension accepted; settle production resource strategy and collection ceilings before integration.

## Comments — completed experiment

Marek confirmed the design and authorized the local experiment. [72 resolved](72-prove-yaml-reader-feasibility.md) records its result. Consumer structure validation is feasible without a YAML dependency. The proposed three additional Unicode escapes require a design answer; no production changes or publication occurred.

## Comments — escape extension accepted

Marek accepted \N, \L and \P. The schema draft and findings now record acceptance. The interview no longer awaits that decision; remaining work concerns measured collection ceilings and reader memory strategy before production integration.
