# Concrete catalog update adoption proposal

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Continue after ticket 21 by inspecting actual AM update/distribution behavior and
recording a bounded proposal for one opt-in Obsidian update path. No installed
updater migration, selected asset download, workflow change or automatic schedule.

## Answer

[Concrete proposal](../design/obsidian-update-adoption.md) follows actual update,
module-sync and installer source. Recommends a coherent seven-module consumer
runtime, foreground single-app preflight, exact stale consent and an explicitly
reviewed catalog-capable Obsidian adapter. Identifies suppressed diagnostics,
ungated success reporting, early mutation and appimageupdatetool bypass as adoption
constraints. Next bounded implementation is local runtime packaging/verification;
ordinary update activation and installed migration are not implemented or accepted.
Documentation/source inspection only; no network, installer or installed state
operation. No tests needed for this proposal; git diff --check passes.

## Comments

2026-10-27 — Superseded recommendation: Marek subsequently accepted shell-only
consumer adoption with no new Python runtime, small simplifying recipe/updater
diffs and fewer independent trust sources. Do not start the Python zipapp/runtime
packaging suggested above. [23](23-shell-consumer-and-small-recipe-migration.md) is
the next-session implementation frontier. This ticket remains resolved as a
historical proposal/source investigation; its actual update-path findings remain
inputs, while its runtime distribution recommendation is no longer the plan.
