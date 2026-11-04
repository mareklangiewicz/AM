# Close the offline pinned-YAML refresh loop

Type: prototype
Status: resolved
Triage: ready-for-agent

Load the previous complete YAML tree by exact local Git commit, feed saved JSON
response fixtures through existing normalization and retained merge, and publish
the next local snapshot. Keep unselected sources unchanged and failed-source facts
retained. Reuse existing components; add no live transport or consumer machinery.
Validate original YAML before decoding so duplicate/invalid input is not silently
repaired by parsing. No workflow, installed AM, remote catalog or daily pin changes.

## Answer

[Findings](../research/yaml-offline-refresh.md): `1719bd8aa` closes the offline
loop with a pinned-tree loader and a thin existing-component refresh adapter.
Three-tool trials pass twelve snapshots, twelve consumer reads and twelve rejected
operations, including rollback of a new first-page release after second-page
failure. Prior publication checks pass after shared validation refactoring.
Compilation/whitespace checks pass. No live/installed/workflow/catalog/pin changes.
