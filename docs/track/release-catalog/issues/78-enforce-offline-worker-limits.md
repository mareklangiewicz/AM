# Enforce hard offline collector worker limits

Type: prototype
Status: resolved
Triage: ready-for-agent

Follow up 71 and 75–77 in the isolated YAML prototype: supervise offline
normalization/merge in a child with a hard elapsed deadline, address-space and
per-file output limits. Quarantine results until successful child completion;
worker refusal must preserve retained facts, effective observation times and
last-success metadata. Exercise noncooperative work and partial output failures.

Trial values are experiment inputs, not approved operational ceilings. No network,
production integration, publication, push, dispatch, repin or host delivery.
Aggregate temporary-storage enforcement and actual default-run capacity remain
separate gates; do not claim a per-file limit bounds arbitrary worker disk use.

## Answer

[Findings](../research/yaml-worker-limits.md): prototype `22bf39a20` on
`research/yaml-worker-limits` enforces an external worker deadline, child
address-space and per-file limits, with private-result quarantine and retained
state preservation on refusal. Six new groups plus nine inherited reader groups
pass on all three awk tools. Syntax and whitespace checks pass. Aggregate staging,
parent memory, portable reader budgets and live capacity remain open under 71.
No production changes or remote operations; both commits remain local.
