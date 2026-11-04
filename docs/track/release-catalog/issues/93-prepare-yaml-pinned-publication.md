# Prepare remote format-2 prior and publication CAS candidate

Type: task
Status: resolved
Triage: ready-for-agent

Continue ticket 92. Reuse isolated authenticated fixed-ref Git acquisition,
require the caller's exact prior pin or proven absence, and reject format 1 rather
than converting implicitly. Validate bounded canonical YAML prior snapshots.
Connect authenticated artifact verification to YAML-only commit construction and
an exact expected-parent publication lease. Exercise local bare repositories and
races; no live catalog writes, workflow activation, repin or installed changes.

## Answer

Prepared source candidate `3bf90b411` on `prep/yaml-offline-publication`.
[Findings](../research/yaml-pinned-publication.md) record exact-pin/proven-absence
acquisition, bounded canonical format-2 prior loading and direct-child YAML-only
publication with an explicit expected-parent lease. Nine new local-Git/API-fixture
tests and 55 regressions pass (64 total), plus compilation and whitespace.
No live catalog publication or workflow activation. Operational source promotion,
capacity/policy acceptance, migration and activation remain separate.
