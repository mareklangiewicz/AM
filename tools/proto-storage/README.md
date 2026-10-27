# Throwaway offline storage prototype

Primary source for release-catalog ticket 08, branch `proto/offline-storage-v1`.
No HTTP libraries, remote operations, collector integration or app policy.

Run from the AM checkout:

```sh
python tools/proto-storage/offline.py
```

Python 3 standard library and Git only. It reads named regular archive members
without extracting paths, replays both complete rounds, runs 64 acceptance
scenarios, and prints a fresh `PROTOTYPE-storage-*` temporary directory containing
`report.json`, a manifest, candidate tree and a disposable local Git repository.
Use `--output /tmp/PROTOTYPE-my-run` to choose a new directory (must not exist).
The local repository has no remote. Cleanup: remove only the printed directory.

Open `demo.html` directly for the in-memory transition walkthrough. Its small JS
reducer illustrates availability/freshness; Python is the authoritative byte,
provenance and Git experiment. They are explicitly separate demonstrations.

`apply` has no filesystem/network/Git side effects. `publish` validates the closed
byte tree and uses Git objects and an atomic expected-old-value ref update. Only
fixed `100644` modes enter its Git tree. Disk import refuses symlinks, executable
files and unexpected paths. `lookup` requires a full commit, explicit availability,
and matching digest/length; freshness expiry/acceptance is deliberately deferred.

This is bounded experimental code, not a hardened publication service or a complete
GitHub schema validator. Public enrollment is an explicit fixture review assertion,
not a proof obtained from authenticated responses. The six sources are those in
the approved saved-evidence sample. The old WezTerm alias comes from the separate
redirect investigation. Saved per-response completion times are absent: the replay
uses explicitly labelled round-completion upper bounds. Do not promote those
synthetic freshness values to a production catalog.

The index embeds its reviewed manifest so offline validation can verify provenance
and active/retired membership. `timing_basis` describes the original receipt;
a later 304 cannot change that historical timing basis. Real collector timing is
still required. All schema choices remain revisable.
