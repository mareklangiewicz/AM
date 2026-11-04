# Shared-default reader budgets — November 4, 2026

Status: local trial evidence for [80](../issues/80-bound-and-measure-shared-default-reader.md),
not approved production limits or a consumer dependency decision. Source branch
`research/yaml-reader-budgets` at `3a8087613`, directory `tools/catalog-yaml-prototype/`.
No network, production integration, remote controls, source push, workflow dispatch,
publication, daily repin or installed-host delivery.

## Bounded portable output and supervised execution

Every reader data write now uses one output-accounting function. Under LC_ALL=C,
check the encoded/decoded byte length before writing. `get` counts exact decoded
scalar bytes (no added newline); `rows` counts canonical tokens, IDs, tabs and
newlines; ID listings count their LF. The default output cap is 16 MiB, configurable
from zero through 32 MiB. Input remains independently configurable from one byte
through the previous 32 MiB maximum. The 64 KiB physical-line guard remains.
Zero output permits validation and empty scalar queries. Duplicate projection
fields refuse; only the ten release or five asset scalar fields can be projected.
The shell stops argument accumulation at ten fields.

The existing private spool still prevents malformed suffixes exposing earlier
rows. A trusted supervisor can supply an exclusive-create spool path; existing
files are preserved and refused. Direct POSIX shell/awk queries gain byte limits,
not hard elapsed or address-space limits. A downstream copy failure can still
produce partial stdout, so direct callers must check status.

The offline Python supervisor runs the shell query in the worker session. Reserve
input snapshot + full spool capacity + full copied-output capacity + diagnostic
capacity + a 4096-byte status receipt. Diagnostic capacity is max(output cap,4096),
matching the kernel per-file allowance. Only the first 512 diagnostic bytes enter
the bounded receipt. Parent decoding is restricted to that receipt; query data
remains a private file. Success exposes a stage-owned candidate; missing query,
parse/output refusal or killed worker exposes none and releases all reservations.
Accepted candidates stay charged until release. These are logical managed-file
bounds with the same trust/aggregate/RSS exclusions as ticket 79.

Measurement trial: 60-second external worker deadline, 128 MiB RLIMIT_AS, 128 MiB
arena, 32 MiB input and 16 MiB output. Parent snapshotting precedes the watchdog.
This demonstrates an offline mechanism, not a decision to add Python to consumers,
a portable shell watchdog or accepted operational ceilings.

## Acceptance and reproduction

```sh
python3 tools/catalog-yaml-prototype/reader_budget_matrix.py
python3 tools/catalog-yaml-prototype/default_matrix.py
python3 tools/catalog-yaml-prototype/retention_matrix.py
python3 tools/catalog-yaml-prototype/bounded_matrix.py
python3 tools/catalog-yaml-prototype/reader_budget_measure.py
sh -n tools/catalog-yaml-prototype/reader.sh
shellcheck tools/catalog-yaml-prototype/reader.sh
```

Six new budget groups plus nine inherited reader groups pass on mawk, GNU awk and
BusyBox awk (45 executions). Existing shared-default, retained-merge and adapter
matrices also pass on all three tools. New groups cover exact output and one-byte
short refusal for row/ID/scalar queries, app listings, empty scalars at zero cap,
duplicate fields/invalid budgets, exact aggregate reservations, private output
identity, malformed suffix/missing query/status preservation, watchdog kill of an
awk shim ignoring SIGTERM, input bounds and exclusive private-spool creation.
All refusals expose zero candidate files and clean reservations. Accepted fixtures
retain independent PyYAML reference checks through inherited reader groups.
Shell syntax, shellcheck, Python compilation and whitespace checks pass.

## Measurement method

The serial measurement generates release documents with a shared default. Nine
out of ten releases are implicit; every tenth retains an older explicit override.
Embedded assets and a maximum physical title line exercise different shapes.
An independent output oracle takes facts/effective observations from the fixture
objects, hashes expected encoded rows, and compares the complete output hash and
row count on success. It does not derive expected times from reader output.
Malformed-suffix and 4096-byte output-refusal cases check absence of candidates.

`reader-budget-measurements.json` records individual attempts and diagnostics.
Wall time includes bounded parent snapshotting and supervisor overhead. Child
elapsed/CPU and largest child RSS come from subprocess timing/getrusage. RSS can
include inherited fork/exec startup image and is not isolated awk memory or a
simultaneous process-tree/parent sum. No memory improvement over earlier awk-only
measurements should be inferred. Synthetic fixture construction and originals are
outside child limits. Single-host timing includes ordinary host load; these are
not portable worst-case bounds.

An initial measurement stopped when the valid large GNU awk query returned 2;
its diagnostic was discarded, so its cause is unknown. The direct and exact
supervised reproductions subsequently passed. The wrapper now captures bounded
diagnostics; the measurement records a generic reader refusal instead of assuming
resource exhaustion from a status. No interpreter bug or memory cause was proved,
and no fix for that unexplained attempt is claimed.


## Completed shared-default measurements

All 21 completed cases match their expectations: 15 full-hash successes and six
intentional refusals exposing no candidate. The initial uncaptured GNU awk refusal
above remains an additional unsuccessful attempt, not part of those 21 cases.
Wall times below include snapshot/supervisor overhead.

| Shape | Input bytes | Output bytes | mawk (s) | GNU awk (s) | BusyBox (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| 100 releases | 163,383 | 8,992 | 0.134 | 0.244 | 0.618 |
| 1,000 mixed observations | 1,630,384 | 90,893 | 1.374 | 2.643 | 6.927 |
| 10,000 retained releases | 16,309,385 | 918,894 | 10.521 | 21.740 | 56.359 |
| 60,000 embedded assets | 10,849,593 | 6,528,894 | 8.872 | 15.784 | 37.499 |
| 65,536-byte physical title line | 67,606 | 65,580 | 0.115 | 0.065 | 0.790 |

Largest reserved logical-byte peak is 66,645,129 bytes for the retained shape.
This includes full unused spool/output/diagnostic headroom and the status receipt;
it is not sampled filesystem occupancy or physical allocated blocks. Asset output
is 6,528,894 bytes, illustrating the distinct spool plus copied-output cost.
Largest-child RSS values are retained in the JSON but deliberately not presented
as isolated awk measurements: inherited fork/exec image dominates several cases.
Host: Linux 7.0.0-42-generic x86_64, Python 3.14.4, mawk 1.3.4 (20260129), GNU awk
5.3.2, BusyBox 1.37.0. Earlier measurements at other revisions remain historical.

## Budget conclusion

Keep the 16 MiB retained-YAML ceiling provisional. The 16,309,385-byte shared-default
retained fixture completes on all three tools, but BusyBox takes about 56 seconds
under a 60-second wall watchdog. That leaves little margin even for this one
synthetic shape. It does not establish that every document below that size fits
this runtime/address-space allowance. The previous explicit-encoding BusyBox
55-second CPU refusal is still valid historical evidence: encoding, fixture size,
output guards and runtime allowance changed, so this is not a controlled claim
that shared defaults fixed reader CPU or memory growth.

The output guard and supervised refusal mechanism are now exercised. Portable
consumer hard deadlines remain undecided; the dependency-free shell reader alone
does not supply them. Before production adoption, choose consumer enforcement and
acceptable performance bounds, test further worst-case shapes or an alternative
reader, and authorize integration explicitly. Bounded real transport/publication
staging and separately authorized default-run live capacity remain ticket 71 gates.
No numerical operational budget is accepted by this result.
