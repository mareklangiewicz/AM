# Issue tracker: local Markdown

Issues, research, and specs live in `docs/track/`, intentionally tracked by Git.

- One effort per directory: `docs/track/<effort>/`.
- Spec: `docs/track/<effort>/spec.md`.
- Map: `docs/track/<effort>/map.md`, with Notes, Decisions-so-far, and Fog.
- One ticket per file: `docs/track/<effort>/issues/NN-<slug>.md`, numbered from 01.
- Each ticket records `Type: research|prototype|grilling|task`, `Status: open|claimed|resolved`, and any `Blocked by: NN, NN` dependencies.
- Keep triage separate from execution status: `Triage: <role>` uses docs/agents/triage-labels.md.
- The frontier consists of open, unblocked tickets; take the lowest number first.
- Claim by setting Status to claimed before work. Resolve by appending an Answer, setting Status to resolved, and adding a result and relative link to the map.
- Append discussion under Comments; preserve earlier evidence and identify superseded assumptions.

When a skill says publish to the issue tracker, create or update a file here. When it says fetch a ticket, read its referenced file. Use docs/track/ wherever a skill assumes .scratch/. GitHub Issues and PRs remain external references unless explicitly requested.
