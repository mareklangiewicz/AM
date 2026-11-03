# Design a simple YAML catalog of release facts

Type: research
Status: open
Triage: ready-for-agent

Interview Marek to settle normalized catalog facts, a strict readable YAML subset, client selection responsibilities, and collection coverage. Implementation requires confirmation of shared understanding at the end of the grilling interview.

## Decisions and evidence

See [ongoing design interview](../research/yaml-format-design.md) and [facts/selection ADR](../../../adr/0001-catalog-facts-and-client-selection.md).

Q21 authorizes a bounded read-only measurement of release-history request cost, response bytes, provisional normalized YAML size, and duration. No workflow dispatch, production publication, repin, or push is authorized by this experiment. The separate natural daily run acceptance remains outstanding.

## Remaining

- Collection revised to configurable scopes and retained merges; scheduled default is all sources, one page of 100. Finalize independent safety and retained-size budgets.
- Policy interview decisions settled; see [consolidated review](../research/yaml-catalog-design-review.md). Exact grammar and budgets are the next experiments after confirmation.
- Shared understanding confirmed; schema/reader experiment completed in ticket 72.
- Unicode escape extension accepted; settle production resource strategy and collection ceilings before integration.

## Comments — completed experiment

Marek confirmed the design and authorized the local experiment. [72 resolved](72-prove-yaml-reader-feasibility.md) records its result. Consumer structure validation is feasible without a YAML dependency. The proposed three additional Unicode escapes require a design answer; no production changes or publication occurred.

## Comments — escape extension accepted

Marek accepted \N, \L and \P. The schema draft and findings now record acceptance. The interview no longer awaits that decision; remaining work concerns measured collection ceilings and reader memory strategy before production integration.

## Comments — resource follow-up underway

[73 resolved](73-bound-yaml-reader-memory.md): record-scoped validation and private
output spooling preserve the contract, but portable constant RSS is not established. A [second random sample plus targeted histories](../research/yaml-history-outliers-20261103/findings.md)
found active sources advertising 58 and 63 release pages; they were not fully
acquired. A [concrete resource proposal](../research/yaml-resource-strategy.md)
records candidate ceilings and the remaining exact-format, runner and scheduling
gates. Candidate numbers are not accepted production budgets. No deployment,
remote mutation, natural-run acceptance or installed-host delivery is implied.

## Current design revision — retained observations

Marek's [explicit revision](../research/yaml-retention-revision.md) supersedes
mandatory full-history collection and replacement-only windows. Per-release
observed_at controls installation freshness; successful limited collections merge
fetched records without touching unfetched facts/times. Repository attempt and
last-success metadata record scope separately. [74 resolved](74-revise-scoped-retained-catalog.md)
updates the schema and offline experiments. The reconciliation policy is an
explicit all-only local proposal, defaulting to retention. Resource ceilings,
retained-growth tests and production integration remain open; no remote mutation.
