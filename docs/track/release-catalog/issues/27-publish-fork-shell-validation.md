# Publish and publicly read the prepared fork shell candidate

Type: task
Status: resolved
Triage: ready-for-agent

## Scope and authorization

Marek approved the ticket-26 concrete publication and pinned two-GET public read
with “yes”. Publish only candidate a0fdd125558c4629a07c7edd0d7f6f7f96b1dcc1 atop
exact parent d612ff34b492b337fe51128f769ec9d262d0ee86 to the fork release-catalog
ref. Use the archived fork-only reader, real clock and explicit commit. Preserve
the production upstream owner. No workflow dispatch, source collection, binary
download, installer, migration, ref smoke test or source branch push.

## Answer

Approved exact candidate published with a normal fast-forward push after the
remote parent matched. Server ref confirmed at the candidate. Exactly two real
public HTTP 200 GETs through the fork-only shell reader returned 450,991 exact
body bytes, exit 0, empty stderr, normal freshness and the identical retained
Obsidian filter URL. Lookup/body hashes and bytes match the candidate.

[Findings and persistent evidence](../research/fork-shell-public-read-findings.md).
Production owner remains ivan-hc/AM. No workflow, new source collection, binary
download, app execution, migration, schedule or source branch push.
