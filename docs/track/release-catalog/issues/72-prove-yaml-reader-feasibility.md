# Prove YAML reader and structural validation feasibility

Type: prototype
Status: resolved
Triage: ready-for-agent

Marek explicitly approved proceeding after the consolidated design checkpoint.
Question: can a precise YAML subset support small POSIX shell/awk validation and fact queries?

## Answer

Yes, within measured bounds: 31 shell + 179 awk lines implement full-file structure validation, scalar lookup, ID listing and batch projection without a YAML runtime dependency. Eight experiment groups pass on mawk, GNU awk and BusyBox awk; 46 malformed variants, independent PyYAML comparisons, Unicode round trips and client release selection are exercised. Shell syntax, shellcheck and whitespace checks pass.

[Findings and limits](../research/yaml-reader-experiment.md), [schema draft](../../../catalog-format-v2.md).
Primary prototype source: research/yaml-reader-prototype at 8a3e5c623 (initial 623eb55de), directory tools/catalog-yaml-prototype/. Prototype code is not merged into main.

The independent parser revealed Unicode line-break folding; propose fixed YAML escapes \N, \L, \P. Ticket 71 remains open for that design answer and resource choices. The simple implementation stores whole-file paths/values; production must address linear memory growth. The 1.64 MB/1,000-release/8,000-asset fixture validates in 0.56–3.08 seconds across tested interpreters, with GNU awk peak RSS 33,336 KiB.

No production, network, installed-host, remote-ref, daily-pin or workflow mutation. No publication or push.
