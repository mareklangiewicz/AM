# Simple offline app-to-release consumer — November 4, 2026

[84](../issues/84-exercise-simple-offline-consumer.md), prototype `f7650b660` on
`research/yaml-simple-consumer`, following the simplified reader `7e8210a56`.
The user authorized pushing the accumulated work and continuing. Main documentation
through `644f3136b` and all referenced YAML research ancestry were pushed to origin;
no workflow dispatch, catalog publication, daily pin or installed AM change occurred.

`tools/catalog-yaml-prototype/browse.sh SNAPSHOT_DIRECTORY APP` resolves the app
through `apps.yaml`, checks `repositories/ID.yaml` declares that identity, then
prints release ID, tag, effective observed_at, published_at, prerelease and title.
This is a small shell example over an already obtained single-commit snapshot.
It introduces no transport, cache, daemon, timeout or supervisor. Fields after ID
are canonical JSON scalar tokens in TSV, never executable shell. Version choice,
freshness decisions and installation remain caller responsibilities.

Three reader calls provide map lookup, identity check and release rows. The
repository is parsed twice, so ticket 83's single-query times are not end-to-end
browse timings. A caller already holding a validated identity can query rows
directly; no new combined query language or cache was added to optimize an example.

`browse_experiment.py` passes six cases on each of mawk, GNU awk and BusyBox awk:
two successful aliases with exact independent expected bytes, missing app (3),
repository identity mismatch (2), malformed repository suffix (2) and malformed
app-map suffix (2). Successful rows retain an older explicit observation and a
newer implicit shared observation. All failures expose no release rows. The
matrix records 18 passing cases in `browse-results.json`; syntax, shellcheck,
Python compilation and whitespace checks pass. Other historical matrices retain
their recorded revisions; this is not installed-command or live-source evidence.

Reproduce from the prototype branch:

```sh
python3 tools/catalog-yaml-prototype/browse_experiment.py
sh -n tools/catalog-yaml-prototype/browse.sh
shellcheck tools/catalog-yaml-prototype/browse.sh
```

The next substantive step is a format-2 writer/publication candidate using retained
merges, paired with this consumer path. Keep it offline first; reuse existing
collection/publication mechanisms rather than promote the full research harness.
The proposed 2 MiB cap is still unaccepted. No automatic truncation/deletion or
operational rollout is implied by pushing source branches.
