# Hard offline worker limits — November 4, 2026

Status: isolated prototype evidence for [78](../issues/78-enforce-offline-worker-limits.md),
not production integration or accepted operational ceilings. Branch
`research/yaml-worker-limits` at `22bf39a20` extends shared-default commit `b3e8b4e70` in
`tools/catalog-yaml-prototype/`. No network, installed files, remote controls,
publication, push, dispatch, daily pin or yadm pointers were changed.

## Mechanism

`collect_supervised` forks trusted local collection/normalization/merge work.
The child starts a session, disables core dumps and sets RLIMIT_AS and
RLIMIT_FSIZE before running the existing adapter. It serializes one result to a
private file. The parent returns that result only after exit 0 and complete JSON
decoding; partial files and failed workers never become candidates. Stdout/stderr
are discarded. Deadline enforcement is outside the worker, so stalled work need
not reach a cooperative check. At expiry the parent sends SIGKILL, kills the
worker's process group, reaps its direct child and removes the private directory.
Polling is 10 ms; OS scheduling and kernel completion latency still apply.
Remaining group members are killed after successful leader exit as well.

Worker refusal constructs `collection_limit` metadata in the parent using the
existing failed-refresh path. Prior releases, shared observation default,
individual overrides and last-success metadata survive. Arbitrary faults are
conservatively mapped to that refusal; an exit status is not an OOM diagnosis.
Supervisor setup/I/O errors propagate without exposing a candidate.

Trial inputs default to 120 seconds, 384 MiB virtual address space and 32 MiB per
regular file. None is an accepted production budget. Fork requires a
single-threaded parent. This Unix/Linux experiment is not a portable consumer
requirement or a hostile-code sandbox; trusted descendants must stay in the
worker session. Existing input/parent allocations and parent result decoding
remain outside the child memory limit. RLIMIT_AS does not measure or cap aggregate
RSS; RLIMIT_FSIZE is per file, not aggregate temporary storage.

## Acceptance

Reproduce from the prototype repository root:

```sh
python3 tools/catalog-yaml-prototype/worker_matrix.py
python3 -m py_compile tools/catalog-yaml-prototype/worker.py tools/catalog-yaml-prototype/worker_experiment.py tools/catalog-yaml-prototype/worker_matrix.py
```

Six new groups plus nine inherited strict-reader groups pass independently on
mawk, GNU awk and BusyBox awk (45 test executions). Accepted collector outputs
are independently parsed with PyYAML and checked by the selected shell reader.
The matrix records `worker-results.json` on the prototype branch.

- Actual file-backed normalization succeeds; a one-byte output allowance refuses
  and preserves prior facts/times. Previous input remains unchanged.
- A sleeping worker ignoring SIGTERM is killed under a 0.15-second deadline;
  the probe checks completion within three seconds and private-directory cleanup.
- A 256 MiB allocation under 96 MiB address space refuses and preserves retention.
- Partial serialization, unsupported JSON objects and a child mutating its private
  previous state before throwing expose no candidate and preserve parent state.
- Six-byte JSON serialization succeeds exactly at the file bound and refuses at
  five bytes; nonfinite/nonpositive time and malformed integer limits reject.
- Descendants left by both a timed-out and a successful leader cannot perform a
  delayed marker write; process-group cleanup is exercised in both paths.

These tests establish the refusal mechanism for sampled trusted workloads. They
do not establish a worst-case scheduling delay, aggregate storage/memory ceiling,
reader performance improvement or actual configured-run capacity. The existing
29-group matrices and historical measurements are unchanged; this wrapper is an
additional opt-in experiment, not a replacement of their execution paths.

## Next gates

Bound aggregate temporary storage and parent/input/result staging independently.
Choose and measure a reader strategy/budget for shared-default documents, keeping
the previous BusyBox large-file refusal visible. Measure actual default-run
capacity only under separate live-collection authorization. Ticket 71 remains
open; no production integration is authorized by this experiment.
