# Prepare an offline format-2 writer/publication candidate

Type: prototype
Status: resolved
Triage: ready-for-agent

Reuse the retained-merge model, canonical YAML emitter and existing local Git
publication helpers to assemble apps.yaml plus repositories/ID.yaml. Validate the
complete candidate before advancing a local ref, test pinned old/new reads and
preserved observations on failed scopes. Keep the implementation small and offline;
no workflow, installed consumer, live transport, remote publication or daily pin.
Trial size caps remain explicit experimental inputs, not accepted production limits.

## Answer

[Findings](../research/yaml-offline-publication.md): `b85f56fec` on
`prep/yaml-offline-publication` extracts the existing emitter, validates a complete
format-2 tree and reuses the existing Git helper for remote-free local publication.
Three-tool trials pass six snapshots, nine pinned consumer reads and fifteen
candidate refusals; retained-merge (48) and reader/budget (45) matrices pass.
Compilation/whitespace checks pass. Trial caps stay unaccepted. No operational
format switch, live transport, workflow, installed AM or daily pin change.
