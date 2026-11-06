# Inspect the two candidate AppImage payloads before conversion

Type: task
Status: open
Triage: ready-for-agent

[128](128-verify-two-candidate-upstream-evidence.md) verifies numeric identities,
observed asset names and narrow selector winners for 20x/2fac. Metadata/header
checks do not establish desktop/icon output or full-file integrity. Statically
inspect the exact recorded assets, without launching them, before a conversion
proposal. Read [preparation](../research/two-candidate-upstream-preparation.md)
and the saved source/receipt hashes first.

Use bounded acquisition into a disposable evidence directory (recorded total
520,789,917 bytes; cap combined app payload bytes at 550 MiB). Check expected
size and published digest; fail on changed identities/sizes rather than silently
switching releases. Use static AppImage/squashfs tooling only. Record tool
versions, root/desktop/icon paths, main and hidden/multiple entries, Exec arguments
and symlinks. Inspect ownership and removal implications against the shared
installer. Do not run an AppImage, launcher or downloaded script. Avoid unrelated
installed/recovery paths. If resource/tool constraints prevent safe static
inspection, record concrete findings and leave the inspection requirement open.

Produce a concrete, reviewable two-recipe conversion proposal with provenance,
verified IDs, narrow patterns, and explicit decisions/remaining questions about
ordering, channels, acquisition and launcher behavior. Keep 4nier-patrimonio
outside scope. No conversion, collection enrollment, app execution, installation,
deployment, publication, workflow, push or yadm changes in this ticket.
