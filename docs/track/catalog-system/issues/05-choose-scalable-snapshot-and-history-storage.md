# Choose scalable snapshot and history storage

Type: grilling
Label: wayfinder:grilling
Status: open
Blocked by: 01, 03, 04

## Question

Which storage/read/write approach supports durable checkpoints and coverage beyond
500 sources while bounding full-snapshot work, individual documents, readers,
retained releases and remote history growth?

Compare the smallest credible alternatives using measured baseline constraints.
Distinguish current tree size, local Git guard, transferred Git history and durable
remote retention. Removing a current-tree file does not purge Git history.
Honor retained-release semantics; any pruning, reconciliation, depth or freshness
trade-off must be explicit and agreed, not an incidental optimization.

Define checkpoint survival/recovery/cleanup, public snapshot addressing, lazy
consumer reads, unchanged-source reuse and exact-parent conflict implications.
Choose what bounded experiment is required before accepting capacity and record
its decision threshold; do not qualify thousands from a synthetic count alone.
Preserve shell consumers or define an explicit compatible migration path.
No cap increase or storage implementation is authorized by resolving this question.
