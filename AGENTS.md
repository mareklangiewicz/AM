## Agent skills

### Issue tracker

Track work in Git-versioned Markdown under `docs/track/`. Read `docs/agents/issue-tracker.md` before creating, claiming, or resolving work.

### Triage labels

Use the default five triage roles recorded in `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: `GLOSSARY.md` and `docs/adr/`. Read `docs/agents/domain.md` before exploring domain behavior or changing terminology.

### Releases

`tools/release/release.py` ships `main-marek` (see `tools/catalog-collector/README.md`, "Focused verification and maintenance"). Pushing a `ci/<name>` test branch, and deleting it after `ship`, need no approval. Pushing `main-marek` and running `release.py ship` always ask Marek first, with `release.py plan` pasted.
