# Move the Git sources into their recipes

Type: task
Label: implementation:task
Status: open
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
