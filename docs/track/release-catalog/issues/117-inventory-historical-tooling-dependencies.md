# Inventory historical collector and staging dependencies

Type: research
Status: resolved
Triage: ready-for-agent

Continue the handoff after 116 with a source-only dependency inventory. Identify
current workflow and maintenance roots, their local Python import closure, and
references tying tests to historical collector/staging tools. Propose one bounded
follow-up only when supported by this evidence. Static reachability is not proof
that an unreferenced command is safe to delete. Preserve legacy recipe behavior,
recovery evidence and deployment state. No deletion or conversion in this ticket.

## Answer

[Inventory](../research/historical-tooling-dependencies.md) records current workflow
and maintenance roots, conservative local import closures, direct staging/package
test callers, and prototype callers outside the collector directory. Current YAML
publication still reuses historical publication/fetch helpers; no module deletion
is justified by workflow retirement alone. Propose isolating those shared helpers
in a separately scoped task; preserve their isolation/bounds/parent checks and
historical callers. No implementation, deployment, push or test-suite claim.
