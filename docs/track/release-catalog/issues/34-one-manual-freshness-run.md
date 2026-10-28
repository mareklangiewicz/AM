# Execute one bounded manual freshness refresh

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Execute exactly the [ticket-33 plan](../research/manual-freshness-run-plan.md)
after explicit approval: recheck isolation and exact remote pins, dispatch once,
retain/validate artifact and parent/child evidence, then at most two pinned
public helper GETs. No schedule, retry/recollection or host app operation.

## Authorization

Preparation is complete. Await approval of the concrete six-request collection,
one conditional publication and two public catalog-read budget. Generic
continuation is not treated as authorization to dispatch the experiment.

Marek explicitly approved the concrete run with “ok”; executing once.

## Answer

[Run findings and persistent evidence](../research/manual-freshness-run-findings.md):
exact approved source/prior and isolation checks passed. One dispatch, attempt 1,
run 40606441534 succeeded with six 200 responses and matching prior conditions.
Published e8e5cf96295369d90402d7584853eb1d3436463d atop exact a0fdd1255 parent.
Artifacts/digests, independent recomputation, public tree and permission logs
pass. Two pinned shell GETs returned 200 and exact bytes, exit 0, empty stderr,
normal freshness, unchanged filter URL. Obsidian fresh through inclusive
2026-10-29T00:05:15.676301Z. No schedule, retry, app execution or binary download.
