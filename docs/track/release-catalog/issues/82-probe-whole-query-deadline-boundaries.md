# Probe whole-query deadline boundaries

Type: prototype
Status: resolved
Triage: ready-for-agent

Follow up 71/81 with offline fault injection around the complete reader shell:
input size preparation, parser, final copy and blocked output. Reuse the trusted
POSIX worker supervisor to distinguish whole-worker termination from parser-only
timeouts. Check private-result quarantine, process and temporary-file cleanup,
and document what streaming output cannot guarantee. No new consumer dependency,
operating budget, production integration, network access or publication is adopted.

## Answer

[Findings](../research/yaml-whole-query-deadlines.md): prototype `84849179b`
on `research/yaml-whole-query-deadlines` passes six focused cases: byte-identical
success, preparation/parser/final-copy stalls, partial private copy and real
BusyBox cat pipe backpressure. Five stalls refuse near the one-second trial
limit with no candidate, stopped recorded targets and parent arena cleanup.
Python compilation and whitespace checks pass. Initial uutils cat pipe behavior
is recorded without a diagnosis. Parent snapshotting, platform support and
consumer budgets remain open; streaming delivery cannot retract a received prefix.
No production integration, live requests, remote mutations or accepted dependency.
