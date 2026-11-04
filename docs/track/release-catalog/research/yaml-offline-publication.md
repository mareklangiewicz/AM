# Offline format-2 publication candidate — November 4, 2026

[85](../issues/85-prepare-offline-yaml-publication.md), prototype `b85f56fec` on
`prep/yaml-offline-publication`, extending the simple consumer `f7650b660`.
No installed AM, workflow, live transport, catalog publication or daily pin changed.

The candidate extracts the existing canonical emitter into `writer.py` rather than
invent another serializer. `yaml_publication.py` assembles `apps.yaml` and
`repositories/ID.yaml`, verifies map references and file identities, checks YAML
round trips with PyYAML and validates each document with the simple shell reader.
PyYAML remains publisher-side; shell consumers gain no dependency. Callers supply
an immutable schema URL and an explicit trial per-file allowance (2 MiB in tests).
That cap remains proposed, not accepted production policy.

Local publication reuses `tools/catalog-collector/publication.py:git` for isolated
Git execution. Format-1 `publish_local` cannot be reused because its validator
requires the old JSON tree; format-1 code is unchanged. The small format-2 adapter
writes a complete validated tree using a temporary Git index and advances the
local ref with an expected-parent compare-and-swap. It refuses repositories with
remotes. It has no remote publisher, daemon, raw-body archive, derived index,
watchdog or new staging framework. Basic identity/reference checks prevent a valid
file from being placed under the wrong identity; they are format correctness.

The caller supplies the whole retained source set and app map. Unchanged sources
must be included; this function is not a partial-tree merge or collection runner.
The experiment uses the existing `retention.refresh` transition before publishing.
Reconstruction of prior state from YAML, actual response acquisition, scheduling,
publication workflow provenance and production cap selection remain integration
work. No one-shot migration or actual format switch is claimed.

`publication_experiment.py` passes on mawk, GNU awk and BusyBox awk. Each trial
creates two local snapshots for two repositories and three aliases. Old/new/old
pinned reads produce exact expected release rows, including unfetched retained
releases and their older observations. A second source's failed attempt preserves
facts/shared observations while updating attempt metadata. Trees contain only
`apps.yaml` and two repository YAML files. Five rejected candidates per trial
(stale parent, mismatched identity, file cap, unsupported string, missing app
reference) leave the accepted ref unchanged. Thus six snapshots, nine pinned
consumer reads and fifteen candidate refusals pass across the three tools.

The emitter extraction also passes the retained-merge matrix (16 groups × three
tools = 48) and reader/budget matrix (15 × three = 45). Python compilation and
whitespace checks pass. Raw results are `publication-results.json` on the prototype
branch. Reproduce with `publication_experiment.py`, `retention_matrix.py` and
`reader_budget_matrix.py` from `tools/catalog-yaml-prototype/`.

Next: exercise loading the previous pinned YAML tree into the retained model and
feed saved response fixtures through normalization, merge and this publisher.
That would close the offline loop without adding live transport or consumer
machinery. Source pushes remain distinct from catalog publication and deployment.
