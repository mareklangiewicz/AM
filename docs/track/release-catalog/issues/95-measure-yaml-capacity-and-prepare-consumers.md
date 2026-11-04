# Measure offline YAML capacity and prepare consumer migration

Type: task
Status: resolved
Triage: ready-for-agent

Continue ticket 94. Measure the maintained adapter/staging path with the reviewed
49-source/100-release shape, clearly synthetic and distinguished from saved real
response replay. Measure retained growth and current 2 MiB refusal boundary with
full rollback. Map existing consumer selections and prepare an offline format-2
selection/freshness candidate without changing live modules or recipes.

No live upstream collection, workflow activation, catalog publication, repin,
installed changes or yadm pointer operations. Source pushes remain authorized.
Measurements are evidence, not accepted operating budgets or runner guarantees.

## Answer

Source candidate `a295d7a2d` on `prep/yaml-offline-publication`.
[Findings](../research/yaml-capacity-and-consumers.md) record synthetic all-source
staging, dense-source refusal, atomic retained-growth refusal and hash-checked
saved-response replay. A static 475-path consumer inventory and explicit pinned
selection/freshness reference prepare migration without changing active modules.
Seven selection plus five workflow checks pass; compilation/whitespace pass.
The 2 MiB cap is not accepted: dense and growth scenarios demonstrate refusal.
Live full-default capacity, policy acceptance and actual portable-shell consumer
migration remain separate. No live or operational change.
