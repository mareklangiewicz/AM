# Whole-query supervision and output boundary — November 4, 2026

Local evidence for [82](../issues/82-probe-whole-query-deadline-boundaries.md).
Prototype `84849179b` on `research/yaml-whole-query-deadlines`, extending
`5a9e2043d`; files are under `tools/catalog-yaml-prototype/`. No production code,
network access, push, publication, dispatch, repin or installed files changed.
No consumer dependency or numerical operating budget is accepted.

## Source boundary

At prototype parent `5a9e2043d`, `reader.sh` guards only its trusted awk parser;
`wc`, spool setup and final `cat` are outside that timer. `reader_budget.py` already
runs the entire reader shell inside `worker.py:run_worker`, copying stdout into a
private regular file. It accepts that path only after complete success. Parent
input snapshotting precedes that worker timer. `staging.py` bounds source lengths
but not storage-I/O elapsed time. Stage reservation state belongs to the parent;
moving its mutations into a fork would not update parent accounting.

`worker.py` creates a session, polls elapsed time and kills the worker process
group on refusal, also cleaning remaining same-group descendants on success.
This covers trusted work remaining in its session, not arbitrary escaped trees.
Address-space/per-file limits are not aggregate RSS or filesystem quotas.
SIGKILL remains subject to scheduling and uninterruptible kernel I/O latency.

## Focused experiment

`whole_query_experiment.py` reuses that unchanged supervisor around `/bin/dash`
executing the complete reader. It uses one second for deliberate stalls and five
seconds for the small successful query. Injected `wc`, `awk` and final `cat` shims
record entry/PID, ignore TERM and exec sleep. A fourth shim writes an 18-byte
prefix before stalling. A separate final-copy shim execs local BusyBox cat against
a prefilled pipe with an open, unread receiving end. The parent retains that end
until supervision completes. Marker assertions establish phase entry; PID checks
exclude running targets (zombies do not count as running).

All six cases pass in `whole-query-results.json`: success matches the direct
reader's four output bytes by SHA-256; five stalled cases refuse at 1.008–1.011 s,
expose no accepted candidate, leave no running recorded target and remove their
private arena. The partial-copy case leaves 18 private bytes before parent cleanup.
SIGKILL bypasses reader shell traps; surviving parent ownership of cleanup matters.
The blocked-pipe case uses BusyBox 1.37.0 cat; it is not a timer/shell/awk matrix
or a new large-input performance measurement. No parent snapshot stall was tested.

An initial full-pipe attempt using local uutils 0.10.0 cat completed successfully
instead of stalling. Its cause was not investigated; no utility defect is claimed.
The retained deterministic backpressure case explicitly uses BusyBox cat and
records a deadline refusal. This does not establish equivalent uutils behavior.

Reproduce on this Linux host with dash and BusyBox installed:

```sh
python3 tools/catalog-yaml-prototype/whole_query_experiment.py
python3 -m py_compile tools/catalog-yaml-prototype/whole_query_experiment.py
git diff --check
```

Those checks pass. Earlier matrices were not rerun and retain their recorded
revisions. The harness uses the existing polling supervisor; its timing assertions
are local trial checks, not hard real-time guarantees.

## Consequence and next gates

Private-file acceptance can discard partially copied output after timeout. Direct
stdout delivery cannot promise the same: once a downstream consumer receives a
prefix, killing the writer cannot retract it. This is a consequence of the direct
copy in `reader.sh`, not a newly adopted output contract. Callers must reject
partial streams after nonzero status or consume an accepted private file. A later
copy of that file still needs its own delivery contract and deadline.

Next useful offline work is supervised input snapshot acquisition with parent-owned
reservations and bounded receipts, or evaluation of a consumer strategy against
explicitly chosen platform/performance requirements. Neither parent setup/result
acceptance nor arbitrary final destinations become bounded merely by supervising
the reader shell. Portable consumer dependencies, accepted memory/time ceilings,
real transport/publication staging and separately authorized live capacity remain
open under 71.
