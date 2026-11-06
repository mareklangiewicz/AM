# Reduce repeated full-snapshot processing before further enrollment

Type: task
Status: resolved
Triage: ready-for-agent
Assignee: codex
Blocked by: 140

Continue 138 after the successful 128-source publication. Remove redundant
snapshot decoding and avoid rewriting unchanged Git blobs/index entries, while
preserving distributed-reader validation, canonical bytes, cross-file identity
checks, exact-parent publication and all existing resource bounds. Use the safe
LibYAML loader when available, with the existing safe loader as fallback.

Measure the maintained whole command against the published 128-source pin and
saved responses. This is a bounded scaling step, not qualification for thousands
or permission to raise source/history/file limits without measurements. Extend
source attribution and prepare the next cohort only within measured capacity.

## Answer

Implemented bounded single-pass snapshot decoding, safe C-loader preference with
safe Python fallback, and exact-parent Git index/blob reuse. Same-evidence replay
improves from the recorded 311.45 seconds to 94.51 seconds / 167,784 KiB RSS under
1 GiB, with identical source receipts and snapshot bytes apart from schema revision.
[Report and timing receipt](../research/snapshot-processing.md) record checks and
limitations. No reader laziness, raised resource bounds or thousands-source claim.
Full regression results and the targeted mixed-revision rerun are recorded in 143.
Source-only; publication is separately proposed in 144.
