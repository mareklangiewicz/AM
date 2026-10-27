# Validate current configured-source helper with a pinned public read

Type: task
Status: resolved
Triage: ready-for-agent

## Scope and read budget

Marek authorized continuation of the handoff's suggested bounded verification.
Execute the unmodified modules/catalog.am at source 3a843e656 with explicit
AMREPO=https://raw.githubusercontent.com/mareklangiewicz/AM/main-marek and
publication a0fdd125558c4629a07c7edd0d7f6f7f96b1dcc1, Obsidian releases alias.
At most two GETs: pinned lookup.tsv (2,000,000-byte cap) and selected body
(450,991-byte cap), each at most 30 seconds. No ref lookup, redirect, retry,
source collection, publication, workflow, binary download or app execution.
Use real time and no stale consent. Fresh boundary is inclusive
2026-10-28T15:43:58.633795+00:00; stop on refusal. Record actual request outcomes
through a transparent curl wrapper and compare bytes/hash/filter with retained
publication evidence. Do not repeat failed network requests automatically.

## Answer

At 2026-10-27T23:47:22.159432+00:00 through 23:47:23.399754+00:00,
the unmodified current helper exited 0 with empty stderr and 450,991 stdout
bytes. Exactly two pinned fork catalog GETs returned HTTP 200. Real freshness
passed without stale consent. Lookup/body equal ticket 27's retained bytes;
the actual recipe filter selected the same Obsidian 1.14.5 AppImage URL.
[Findings and persistent evidence](../research/current-helper-public-read-findings.md).

Initial sandbox execution failed DNS (curl 6), emitted no body and recorded one
failed curl invocation; it did not establish an HTTP request. A network escalation
was explicitly approved, then one successful invocation ran. No automatic HTTP
retry, ref lookup, source collection, publication, workflow or app operation.
Only evidence/tracker files changed; targeted byte/hash/filter checks passed.
The historical 107-test implementation suite was not rerun for this evidence task.
