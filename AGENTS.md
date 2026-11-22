## Agent skills

### Issue tracker

Track work in Git-versioned Markdown under `docs/track/`. Read `docs/agents/issue-tracker.md` before creating, claiming, or resolving work.

### Triage labels

Use the default five triage roles recorded in `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: `GLOSSARY.md` and `docs/adr/`. Read `docs/agents/domain.md` before exploring domain behavior or changing terminology.

### Releases

`tools/release/release.py` ships `main-marek` (see `tools/catalog-collector/README.md`, "Focused verification and maintenance"). Pushing a `ci/<name>` test branch, and deleting it after `ship`, need no approval. Pushing `main-marek` and running `release.py ship` always ask Marek first, with `release.py plan` pasted. Run `ship` without `--watch`, then `release.py watch RUN_ID ...` with the printed ids in the background: a bounded caller that kills `ship --watch` loses the ship's output with it.

### Tests

While iterating, run only the affected module or test from its suite directory, e.g. `cd tools/catalog-collector && python3 -B -m unittest test_contracts.Contracts.test_retired_compatibility_publication_is_refused_in_summaries`. Once per finished change, before you commit, run `tools/fast-tests.sh`: lint and every Fast tier suite, the same command both workflows run (about 9 minutes). The whole-tree tier and container e2e run as Long tests on a `ci/<name>` branch. A change under `programs/`, to `modules/appimage.am` or to a `*-policies.json` also runs the whole-tree tier locally first (`cd tools/catalog-collector && python3 -B -m unittest discover -p 'tree_*.py'`, about 15 minutes; `python3 -B -m unittest tree_generated_policy` alone takes seconds and catches a policy left unregenerated): those are what it catches, and a Long tests round trip costs more. Fast tier tests never read the live recipe tree (ticket 28; the `without-upstream-recipes` job deletes it), so a check that does stays a `tree_*.py`.
