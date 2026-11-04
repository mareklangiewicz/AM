# Replay real saved release pages and prepare the attempt adapter

Type: prototype
Status: resolved
Triage: ready-for-agent

Replay the 44 previously acquired AppImage release-list response bodies through
format-2 normalization, local publication, pinned loading and the simple consumer.
Prepare an adapter from existing collector attempt records, retaining recorded
receipt times rather than assigning replay time. Keep transport/workflows unchanged;
no new network acquisition, installed changes, remote catalog publication or pin.

## Answer

[Findings](../research/yaml-real-response-replay.md): `125a2ff9d` replays 41 saved
list responses (914 releases/14,242 assets), explicitly excluding three latest-only
bodies. Complete local snapshots reload and remerge with original receipt times;
all saved fact comparisons pass. Largest 1.25 MB source returns matching rows on
three awk tools. Six adapter tests and the existing closed-loop refresh checks
pass; compilation/whitespace checks pass. A small existing-attempt adapter and
production seam review are prepared. Unconditional list bodies avoid adding
conditional-page membership machinery; no operational changes occurred.
