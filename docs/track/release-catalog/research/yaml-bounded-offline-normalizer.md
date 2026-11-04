# Bounded offline JSON normalization — November 4, 2026

Local experiment only. Prototype commit `b9d155973` on
`research/yaml-bounded-collector`, based on retained prototype `4600ae084`.
No network acquisition, workflow changes, publication, push, daily repin or host
installation occurred. Format 1 remains production. Candidate limits remain
unapproved trial inputs.

## Result

The new file-backed adapter consumes actual JSON bytes rather than pre-normalized
fixture records or caller-declared byte counts. It reads local regular fixture
files in chunks, counts failed opens as attempts, checks source request and byte
limits, and checks real monotonic elapsed time cooperatively. Overflow detection
can consume one byte beyond the available response/aggregate allowance; that byte
is counted. Exact-boundary bodies succeed if the requested scope completes.
Response receipt time is captured after acquisition, before normalization.

Normalization maps published release and embedded asset facts to the exact
prototype field order, discards draft records, sorts asset IDs numerically, omits
unavailable optional facts, and rejects duplicate JSON keys/IDs, invalid scalar
types/ranges, invalid timestamps, non-HTTPS URLs and unrepresentable strings.
Unused upstream fields are ignored. It feeds lazy responses into the existing
atomic retained-merge model. A finite scope never opens subsequent fixture files.
A failure on a later page rolls back all fetched facts and observation times.

Six new acceptance groups plus nine inherited reader groups pass with mawk,
GNU awk and BusyBox awk. Separately, all sixteen prior reader/retention groups
still pass on those interpreters. Results are in `bounded-results.json` and
`retention-results.json` on the prototype branch. Tests validate output through
both the shell reader and the independent YAML parser, including Unicode strings,
malformed later responses, request/byte/elapsed/catalog/line limits, draft handling
and the explicitly experimental reconciliation policy. Whitespace checks pass.

Reproduce in a worktree of that branch:

```sh
python3 tools/catalog-yaml-prototype/bounded_matrix.py
python3 tools/catalog-yaml-prototype/retention_matrix.py
```

## Limits and next gate

This is a local-file adapter, not a network collector. `has_next` is explicit
fixture metadata; HTTP status, Link-header validation, auth/rate handling, redirects,
retry policy and credential budgeting are not implemented. JSON parsing and the
merge still allocate whole bounded objects. Output validation is exercised by
tests, not integrated as a production staging/publication step. The fixture budget
can be reused, but this does not establish a fair multi-source runner contract.

Elapsed checks surround reads, normalization and the completed merge. They cannot
interrupt a blocked read, JSON parsing, serialization or copying in progress.
Therefore this experiment establishes cooperative elapsed refusal, not a hard
deadline or process-memory ceiling. It makes no runner-capacity guarantee.

Next measure repeated retained growth, near-limit merges/staging and revised
reader resources; add process isolation/deadline and memory enforcement before
calling the collector operationally bounded. Selected-release freshness continues
to use the preserved `observed_at` semantics tested in ticket 74. Live collection
cost measurement and approval of operational ceilings remain separate steps.
