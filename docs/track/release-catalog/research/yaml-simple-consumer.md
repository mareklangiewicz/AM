# Simple consumer path — November 4, 2026

[83](../issues/83-simplify-consumer-reader.md), prototype `7e8210a56` on
`research/yaml-simple-consumer`. Marek explicitly prioritizes simplicity over
increasingly defensive supervision. This revises the recommended direction:
whole-query/snapshot watchdog work is optional research, not a prerequisite for
the simple consumer. No production integration or remote changes occurred.

## Candidate and recommendation

Use the existing shell/awk reader with complete schema validation, byte caps and
private output spooling. Remove the opt-in parser watchdog and its timeout
dependency; the prototype does so. Keep explicit external awk lookup because the
BusyBox tool-selection issue was actually observed, rather than hypothetical.
Keep the existing exclusive private-spool hook for offline harnesses. Python
supervisors, aggregate staging reservations, process-group cleanup and snapshot
watchdogs stay outside the consumer path. Prior branches preserve their evidence.

Use one `rows` query for multiple fields instead of reparsing for each scalar.
Callers check exit status. Do not promise hard elapsed limits or atomic delivery
to arbitrary stdout destinations. These boundaries need documentation, not more
consumer machinery in the absence of a concrete operational need.

Proposed starting policy: a 2 MiB per-source input cap and 2 MiB query-output cap,
prefer mawk or GNU awk for larger retained catalogs, retain BusyBox compatibility
when its slower execution is acceptable. Aim for ordinary snapshots around or
below 1 MiB. These are practical starting proposals, not worst-case guarantees
or a newly accepted production budget. No automatic deletion/truncation follows
from a cap: retained merging and failure preservation remain unchanged. A source
that exceeds the chosen cap needs an explicit size/reader decision, not silent
loss of history. Existing prototype defaults remain unchanged pending that choice;
the measurement supplies 2 MiB caps explicitly.

## Direct measurements

`simple_measure.py` runs `/bin/dash reader.sh rows ...` without the Python worker,
staging or parser timer. Fixtures have eight embedded assets per release, short
titles and shared observations with one older override in ten. They represent
ordinary synthetic shapes, not measured live distributions. An independent hash
oracle comes from fixture objects via `reader_budget_measure.expected_hash`.
All nine complete hashes and row counts match.

| Releases | Input bytes | Output bytes | mawk seconds | GNU awk seconds | BusyBox seconds |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 163,383 | 8,992 | 0.124 | 0.233 | 0.540 |
| 500 | 815,383 | 45,392 | 0.562 | 1.189 | 3.111 |
| 1,000 | 1,630,384 | 90,893 | 0.987 | 2.095 | 5.387 |

Single runs on the same local Linux host/tools as ticket 80; normal host load
applies. These are total direct-command wall times, not portable bounds.
`/usr/bin/time` reports largest-process RSS of 7,796–7,964 KiB across these cases;
this is not isolated awk or summed process-tree RSS, and does not prove constant
memory or an improvement over the earlier fork-supervised measurements. GNU time
and Python are benchmark dependencies only. Complete values and hashes are in
`simple-measurements.json` on the prototype branch. The 2 MiB exact boundary,
large scalar/asset outliers and arbitrary documents below it were not benchmarked
here; earlier shape measurements retain their source revisions.

## Checks and next action

Nine benchmark cases pass. `reader_budget_matrix.py` passes six budget groups plus
nine inherited reader groups on all three awk tools (45 executions). Shell syntax,
shellcheck, Python compilation and whitespace checks pass. Watchdog-specific
harnesses belong to historical branches and are explicitly identified as such in
the candidate README; they are not checks for the removed feature.

Proceed toward a small integration candidate using this consumer path and an
explicit source-size policy. Resolve concrete collection/publication requirements
as that work needs them. Do not make further speculative watchdog experiments a
gate. Actual live acquisition, production integration and publication retain their
separate authorization boundaries; ticket 71 remains open.
