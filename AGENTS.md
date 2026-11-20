## Agent skills

### Issue tracker

Track work in Git-versioned Markdown under `docs/track/`. Read `docs/agents/issue-tracker.md` before creating, claiming, or resolving work.

### Triage labels

Use the default five triage roles recorded in `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: `GLOSSARY.md` and `docs/adr/`. Read `docs/agents/domain.md` before exploring domain behavior or changing terminology.

### Releases

`tools/release/release.py` ships `main-marek` (see `tools/catalog-collector/README.md`, "Focused verification and maintenance"). Pushing a `ci/<name>` test branch, and deleting it after `ship`, need no approval. Pushing `main-marek` and running `release.py ship` always ask Marek first, with `release.py plan` pasted.

### Tests

While iterating, run only the affected module or test from its suite directory, e.g. `cd tools/catalog-collector && python3 -B -m unittest test_contracts.Contracts.test_retiring_compatibility_publication_is_optional_in_summaries`. The collector's fast tier takes about 6 minutes, so run it, and the other suites that import changed code, once per finished change, before you commit. Then run `uvx ruff@0.17.4 check tools test`, with the same version and `ruff.toml` the workflows use. The whole-tree tier and container e2e run as Long tests on a `ci/<name>` branch.
