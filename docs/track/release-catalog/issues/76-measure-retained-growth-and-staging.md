# Measure retained growth and staging

Type: prototype
Status: resolved
Triage: ready-for-agent

Continue 75 offline: repeated one-page retained merges, exact merged-byte refusal,
near-16-MiB staging and revised-reader resource measurements on three awk tools.
Use serial, process-limited children and bounded synthetic files. Verify selected
release freshness and no partial reader output on a malformed suffix. Measurements
are evidence for trial limits, not approved operational ceilings or live capacity.

## Answer

[Findings](../research/yaml-retained-growth.md) and prototype `ccd0273e4` record
thirty daily merges, exact merged-size rollback, near-16-MiB staging, twenty reader
cases and a smaller completed pilot. Selected-release freshness, line boundaries,
malformed-suffix refusal and forced spool-write failures are verified. BusyBox
hits the 55-second CPU cap at 16.67 MB; mawk/GNU awk complete at about 8 MiB RSS.
The 16 MiB retained-byte candidate remains provisional. Hard collector/staging
limits, portable reader budgets and live run capacity remain open under 71.
No production changes, push, dispatch or repin.
