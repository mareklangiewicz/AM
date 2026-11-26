# Derive the Git sources from the recipes

Type: task
Label: implementation:task
Status: resolved
Triage: ready-for-agent
Blocked by: none

## Outcome

As decided in [Derive the collector's inputs](25-collector-inputs-from-catalog-and-recipes.md) (items 4 and 7): the five
`git-sources.json` entries become `CATALOG_GIT_*` assignments in their
`script`-form recipes (junest, translate-shell, mediaurl-js, anything-llm,
cursor-ai-downloads), for example `CATALOG_GIT_TAGS=true` and
`CATALOG_GIT_BRANCH_FILES='master:VERSION'` (exact names chosen here, stated in
`docs/`). The policy generator reads them; `git_observations.py` takes them
from the generated rows; `git-sources.json` goes. No install conversion. The
recorded run 45658789307 regression test in `test_catalog_run.py` keeps
passing with the scopes read from the recipes.

## Answer

Simpler than planned (Marek, November 26: check whether the Git sources are
needed at all). The Git data is needed: five recipes select their version
from Git.
- `x86_64/junest` reads `VERSION` on `master`.
- `x86_64/cursor` reads `version-history.json` on `main`.
- `x86_64/anything-llm`'s second selection reads `linux_installer.sh` on
  `desktop`.
- `x86_64/trans` and `x86_64/watched` pick the newest matching tag.

All five repository files were read between November 24 and 26 and carry
those refs. `mediaurl-js`, behind `watched`, has no releases at all.

But `git-sources.json` only repeated those recipes' selection lines (ticket
26), and deriving from them gave exactly its five entries. So
`git_observations.configuration` now derives each scope from the recipes'
selections: tags for `git-tag`, the branch for `git-branch`, and the branch
and file for `git-file`. It keeps the old limits. `git-sources.json` is
deleted, and the recipes get no new lines: Outcome's `CATALOG_GIT_*`
assignments would have been a third copy.

Tests (`test_git_observations`): the derivation over sample rows, a fifth
branch refused, and the pinned recipes giving exactly the old five scopes.
`test_catalog_run.Budget` reads the derived scopes.
