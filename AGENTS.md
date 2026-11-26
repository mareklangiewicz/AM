## Agent skills

### Issue tracker

Track work in Git-versioned Markdown under `docs/track/`. Read `docs/agents/issue-tracker.md` before creating, claiming, or resolving work.

### Triage labels

Use the default five triage roles recorded in `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: `GLOSSARY.md` and `docs/adr/`. Read `docs/agents/domain.md` before exploring domain behavior or changing terminology.

### Releases

`tools/release/release.py` ships `main-marek` (see `tools/catalog-collector/README.md`, "Tests and shipping"). Pushing a `ci/<name>` test branch, and deleting it after `ship`, need no approval. Pushing `main-marek` and running `release.py ship` always ask Marek first, with `release.py plan` pasted. Ship finished tickets in batches: one Long tests round and one ship (one question to Marek) for several tickets, not one per ticket. Run `ship` without `--watch`, then `release.py watch RUN_ID ...` with the printed ids in the background: a bounded caller that kills `ship --watch` loses the ship's output with it.

### History

The collector commits `catalog/` to `main-marek` every hour (ticket 24), so most commits there are data. `git log -- . ':!catalog'` shows only the code history; `git log -- catalog` only the collector's.

### Tests

Before a commit, run only what the change touches: the affected tests or suites from their directory (e.g. `cd tools/catalog-collector && python3 -B -m unittest test_documents`), lint (`uvx ruff@0.17.4 check tools test`, seconds), and `python3 -B -m unittest tree_generated_policy` (seconds) when `programs/` or a policy compiler changed. Don't run the whole `tools/fast-tests.sh` or the whole-tree tier locally by default: Long tests on a `ci/<name>` branch run both, plus the container e2e. Push one `ci/<name>` per batch of finished changes, not per commit. Fast tier tests never read the live recipe tree (ticket 28; the `without-upstream-recipes` job deletes it), so a check that does stays a `tree_*.py`.
