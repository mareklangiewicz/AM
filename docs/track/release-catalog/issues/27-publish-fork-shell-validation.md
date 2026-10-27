# Publish and publicly read the prepared fork shell candidate

> **2026-10-28 ownership correction:** [Ticket 29](29-respect-configured-catalog-repository.md) supersedes
> this record's fixed-upstream ownership assumption. This fork's catalog follows
> AMREPO and must not fall back to upstream AM. Upstream acceptance/publication
> is not a prerequisite for this fork. Results and archived bytes below retain
> their historical source/revision meaning; they do not define current policy.

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
At that revision, production ownership was still incorrectly fixed to ivan-hc/AM
(corrected by ticket 29). No workflow, new source collection, binary
download, app execution, migration, schedule or source branch push.
