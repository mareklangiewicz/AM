# Execute one bounded manual freshness refresh

Type: task
Status: open
Triage: ready-for-human

## Scope

Execute exactly the [ticket-33 plan](../research/manual-freshness-run-plan.md)
after explicit approval: recheck isolation and exact remote pins, dispatch once,
retain/validate artifact and parent/child evidence, then at most two pinned
public helper GETs. No schedule, retry/recollection or host app operation.

## Authorization

Preparation is complete. Await approval of the concrete six-request collection,
one conditional publication and two public catalog-read budget. Generic
continuation is not treated as authorization to dispatch the experiment.
