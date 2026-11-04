# Prepare exact-pin YAML acquisition and manager integration

Type: task
Status: resolved
Triage: ready-for-agent

Continue 97 in an isolated source branch: configured AMREPO, bounded raw-file
acquisition without Git/Python/jq on clients, distributed shared reader/policy
modules, five cohort recipe bindings and real manager install/update/batch seams.
Use saved local Git fixtures and stubbed transports only. Preserve command pin
reuse, per-selection freshness/waiver, REFRESH_ALWAYS, repair and pre-mutation
refusal. Distinguish proposed format-2 stale UI from legacy format-1 consent.
No merge to main, workflow activation/dispatch, live API/catalog publication,
installed change, repin or yadm pointer operation. Policy acceptance and complete
format-1 transition/rollback remain separate.

## Answer

Candidate `7946f2167` on prep/yaml-consumer-integration supplies bounded exact-pin
raw-file acquisition, ordinary shared-module distribution and actual five-recipe
install/update/batch bindings. [Findings](../research/yaml-manager-integration.md).
161 scoped checks pass with final diagnostic coverage targeted afterward. Runtime
source changes are isolated from main; source promotion, 470 remaining recipe
policies and a complete installed-consumer/format transition remain separate.
No live or operational changes. This resolves source preparation, not activation.
