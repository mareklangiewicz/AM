# Repair extracted installer test after encoder refactor

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Full post-refactor validation found the metacharacter module-location test failing
with an empty sourced path. Its extracted installer block calls the new shared
encoder but its harness omits that definition. Preserve the real production
helper in the harness and reject unexpected stderr; rerun the focused case and
full catalog suite. Production encoder already passes the round-trip spec and
all 38 installed-container scenarios pass.

## Answer

Harness now includes the actual encoder definition and rejects unexpected stderr.
Focused red reproduced twice before repair, then passed; full suite 198 tests passes
(142.904 seconds), plus 10 e2e support specs. No production change. Container matrix
passed all 38 scenarios before this test-only correction. Diff checks pass.
