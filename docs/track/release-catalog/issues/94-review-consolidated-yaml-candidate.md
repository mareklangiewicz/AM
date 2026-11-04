# Review consolidated YAML source and prepare complete inactive workflow

Type: task
Status: resolved
Triage: ready-for-agent

Review the complete prep candidate at 3bf90b411 against main dab1efd67 using
standards and current authoritative schema/ADR axes. Address concrete findings,
separate reusable runtime modules from experiments, and prepare an inactive
collection/artifact/publication workflow with distinct permissions. Keep existing
operational workflows and refs untouched. Validate offline, record remaining
capacity/policy/migration/activation decisions. Source pushes remain authorized.

## Answer

Consolidated candidate `ff2dc1499` on `prep/yaml-offline-publication` (implementation
`deba0518e`, followed by whitespace cleanup). [Findings](../research/yaml-consolidated-review.md)
record independent standards/spec review, all addressed findings, maintained-module
relocation and complete inactive manual collection/publication workflow. 83
collector/storage/workflow/delivery tests and 62 reader/retention/adapter tests
pass, plus publication trials on three awk implementations. Compilation, shell
syntax, legacy imports, runtime dependency separation and whitespace pass.
No active workflow, live collection/catalog publication, repin or installed change.
Capacity/policy acceptance, maintainer source promotion, consumer migration,
transition/rollback and explicit operational activation remain separate.
