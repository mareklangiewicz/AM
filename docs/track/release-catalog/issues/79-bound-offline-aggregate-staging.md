# Bound aggregate offline staging and parent transfers

Type: prototype
Status: resolved
Triage: ready-for-agent

Follow up 71/78 with a private staging arena that reserves an aggregate logical
byte budget before writes. Snapshot bounded regular input files and reserve
worker result capacity before execution. Add a file-oriented collector interface
so the parent copies bounded chunks and never decodes the candidate JSON.
Exercise aggregate exhaustion, exact bounds, source growth, cleanup and failures.

Limits apply to this trusted offline path's managed files, not arbitrary worker
writes, filesystem allocation overhead, external fixture originals or publication.
No filesystem quota or aggregate RSS guarantee is implied. No live collection,
production integration, push, dispatch, repin or installed-host changes.

## Answer

[Findings](../research/yaml-staging-limits.md): prototype `a710841e8` on
`research/yaml-staging-limits` reserves aggregate managed logical bytes before
input snapshots/result writes and keeps earlier candidates charged. The parent
copies bounded chunks and never decodes prior/result JSON. Seven new groups plus
nine inherited reader groups pass on three awk tools (48 executions); all 45
existing worker-matrix executions also pass. Syntax/whitespace checks pass.

No filesystem quota, arbitrary-write bound, parent elapsed deadline or aggregate
RSS guarantee is claimed. Refusal exposes no candidate and preserves the prior
file. Reader budgets, real transport/publication staging and actual live capacity
remain separate gates under 71. All work is local only.
