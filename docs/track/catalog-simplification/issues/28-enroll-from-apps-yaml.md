# Enroll from apps.yaml, retire source-names.json

Type: task
Label: implementation:task
Status: resolved
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

## Answer

Enrollment is `host_catalog.enrollment(root)`: every app in
`catalog/apps.yaml`, with `repository_id` and `repository` read from the head
of the repository file its entry points to (`documents.read_top`), and that
file's name as its source's name. `configuration()` keeps its signature for
its other callers. It refuses with a named reason: a pointer to a retired
name, a missing file, a malformed pointer, two file names for one repository
id, an enrolled recipe whose app has no entry, an enrolled recipe whose
identity disagrees with its file, an empty `apps.yaml` (it would empty
`catalog/`), and the source cap.
`collection-recipes.txt` stays and marks readiness to install.
`collection-apps.json` and `source-names.json` are deleted.

- `tools/catalog-collector/retired-names.yaml` holds the 25 names in a new
  `retired_names` schema kind (name → `true`), as filed. Marek confirmed this
  over ticket 25's later "no new catalog-grammar files for collector inputs".
  `build.py` now writes a boolean const as `true` (before, it wrote Python's
  `True`); no earlier kind had one.
- Publish has a race guard. Hand edits to `apps.yaml` now share `catalog/` with
  the collector. If the tip's app → file map differs from the one collect
  read, publish keeps the tip's `apps.yaml` and removes nothing, and the next
  run catches up. Without the guard, an entry added during a run was
  overwritten, and the run after that deleted its file.
- `tools/upstream-merge/merge.py`: `derive` only drops a no-longer-declared
  recipe from `collection-recipes.txt`, since the app's entry stays in
  `apps.yaml`. `stage` checks the merged recipes with `enrollment()` against
  `catalog/` at the fork revision. Its plan against `upstream/main`
  (`ec0fe70e9`) ran clean.
- `pinned_recipes.COMMIT` is `125dd7632`, the commit that adds
  `retired-names.yaml`, and its snapshot now includes `catalog/apps.yaml` and
  `catalog/repositories/` (about 0.6 s to unpack).

Live tree, before the switch: the derived enrollment equals the old one
exactly (8,466 apps, 8,288 sources, every identity and file name the same).
Enrollment costs about 4 s, 3 s of it `recipe_rows` as before.

Tests:
- `test_enrollment` covers the configuration seam and each refusal.
- `test_catalog_run.Enrollment`: a hand-added entry is collected on the next
  run; a removed entry's file leaves `catalog/`; an entry added during a run is
  kept and collected next (red before the guard); a pointer to a retired name
  refuses the run.
- `test_examples` adds the retired-names examples.

Still blocked: no never-read file may be committed to `catalog/` until
myxps, mylenovo and mypi have run `am -s` with ticket 27's parser. The code
only writes such files in test fixtures.

Not done: `release.py` validates a catalog-only commit with the readers, not
with `enrollment()`. A hand enrollment with a broken pointer passes `ship` and
fails the next hourly run.
