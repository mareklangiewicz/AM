# Aggregate managed staging — November 4, 2026

Status: isolated prototype evidence for [79](../issues/79-bound-offline-aggregate-staging.md).
Source: `research/yaml-staging-limits` at `a710841e8`, extending worker prototype
`22bf39a20`. Files live under `tools/catalog-yaml-prototype/` on that branch.
No live collection, production integration, push, dispatch, repin, publication,
remote-control inspection or installed-host changes. Limits remain trial inputs.

## Mechanism and exact bound

A `Stage` arena reserves aggregate logical bytes and file count before any managed
write. `collect_staged` first reserves result headroom, then snapshots the prior
JSON file and selected local response files. Each snapshot reserves its opened
regular file's size, copies at most 64 KiB at a time and refuses growth or shrink
relative to that size. Nonregular inputs are rejected, with nonblocking opens
allowing FIFO rejection without waiting for a writer. Finite scope does not consume
extra pages; explicit page/source byte ceilings independently restrict inputs.

The child reads/decodes the staged previous JSON and responses under RLIMIT_AS,
normalizes/merges them, then serializes its result under RLIMIT_FSIZE. The worker
now accepts an optional private result path and returns that file without decoding
it in the parent. Only exit 0 and size within the reserved result allowance expose
a candidate. Snapshot reservations are released after completion; candidate
capacity remains charged until explicit release or arena exit. Reuse one arena
across sequential sources so candidates retained from earlier sources continue to
consume its capacity. Arbitrary multiple arenas do not share a global limit.

For this trusted path, at every write the sum of managed file lengths is at most
the sum of live reservations, which is at most `Stage.total_bytes`. File count is
independently bounded. Unused result headroom is conservatively charged. Refusal
releases partial files/reservations and leaves the original previous file intact.
A killed worker or staging refusal raises without a candidate; unlike the earlier
object-returning helper it does not construct failed-attempt metadata in the parent.
Callers must preserve their previous artifact and report refusal separately.

Trial defaults: 128 MiB arena, 128 files, 32 MiB previous JSON, 16 MiB one response,
96 MiB source responses, 64 pages and 32 MiB result headroom. These JSON/file
allowances are distinct from the existing 16 MiB trial normalized-YAML allowance.
Worker defaults remain 120 seconds and 384 MiB address space. No values have been
promoted to accepted production ceilings.

## Acceptance and reproduction

```sh
python3 tools/catalog-yaml-prototype/staging_matrix.py
python3 tools/catalog-yaml-prototype/worker_matrix.py
python3 -m py_compile tools/catalog-yaml-prototype/staging.py tools/catalog-yaml-prototype/staging_experiment.py tools/catalog-yaml-prototype/staging_matrix.py tools/catalog-yaml-prototype/worker.py
```

Seven new staging groups plus nine inherited reader groups pass on mawk, GNU awk
and BusyBox awk: 48 executions. The existing six-worker-plus-nine-reader matrix
also passes all 45 executions after the optional file-result extension. Syntax
and whitespace checks pass. Results are in `staging-results.json` and unchanged
`worker-results.json` on the prototype branch. Accepted fixtures are independently
parsed with PyYAML and validated by each selected shell reader.

- Exact sum of input lengths plus reserved result capacity succeeds; one byte less
  refuses, removes partial snapshots and restores zero reservations. A retained
  candidate prevents a second source exceeding capacity; releasing it permits
  collection again. Recorded reservation peak equals the exact allowance.
- Empty snapshots, exact file boundaries and an independent file-count guard work;
  oversized input refuses before copying.
- Growth/shrink probes alter the initial stat length while reading real data;
  both refuse and clean up. A real FIFO is rejected without blocking.
- Output truncation and a deadline refusal leave no candidate/snapshots and preserve
  the original previous file byte for byte.
- Finite scope never asks an iterator for the next page; source byte exhaustion
  and a full-history request exceeding the page safety capacity refuse.
- Guards confirm the parent never calls JSON decoding for inputs or results.
  Closing the arena removes candidates and rejects subsequent reservations.
- Forced output-open failure and invalid arguments leave no reservations.

The first no-parent-decoding probe patched the shared JSON module in both parent
and child and accidentally prohibited legitimate child decoding. The probe was
corrected to distinguish process IDs; the completed matrix above passed.

## Limits and remaining gates

This is an aggregate bound on managed **logical file lengths**, not a filesystem
quota. Allocation blocks, directory metadata, fixture originals, unrelated files,
publication copies and arbitrary worker writes are outside it. Trusted children
must obey the managed-path contract and stay in their worker session. No general
hostile-code confinement or aggregate RSS ceiling is claimed. Parent copies have
bounded chunk sizes but no external elapsed deadline; regular-file I/O can stall.
Snapshots are private after copying, but external same-size in-place source edits
are not a transactional upstream snapshot. These remain trusted fixture inputs.

The file interface removes parent whole-document JSON decoding; it does not prove
all parent RSS constant (caller inputs, page descriptors and existing interpreter
memory still exist). Child address-space refusal still protects normalization/
merge amplification. No near-cap CPU/RSS benchmark was rerun; earlier shared-default
and explicit-encoding results retain their original scopes.

Remaining 71 gates: choose and measure the shared-default reader's runtime/output
budgets or another strategy; integrate bounded transport and publication staging
only under their own authorization; measure actual default-run capacity only under
separately authorized live collection. No production or publication permission
follows from this offline result.
