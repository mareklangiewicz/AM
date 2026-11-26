# Enroll from apps.yaml, retire source-names.json

Type: task
Label: implementation:task
Status: open
Triage: ready-for-agent
Blocked by: 27

## Outcome

As decided in [Derive the collector's inputs](25-collector-inputs-from-catalog-and-recipes.md) (items 1, 2 and 9): the
collector's enrollment is the app set in `catalog/apps.yaml`; each app's
`repository_id` and `repository` come from the repository file it points
to; file names come from the pointers. The collector's rewrite of `apps.yaml`
refreshes labels only and never adds or drops an app. The 25 retired names move
to `tools/catalog-collector/retired-names.yaml` (catalog grammar, each name
mapped to `true`, with a schema `$defs` entry), and a pointer to a retired
name is refused. `collection-apps.json` and `source-names.json` go;
`tools/upstream-merge` and `collection-recipes.txt` handling follow (an
installable recipe's `apps.yaml` entry must exist). Enrolling a new app is an
`apps.yaml` entry plus a never-read repository file (ticket 27);
`tools/catalog-collector/README.md` and `docs/catalog-operating-policy.md`
say so. A test shows a hand-added entry collected on the next run, and a
removed entry's file listed for removal.
