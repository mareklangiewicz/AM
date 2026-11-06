# Inspect the two candidate AppImage payloads before conversion

Type: task
Status: resolved
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

## Answer

[Static inspection and conversion proposal](../research/two-candidate-conversion-proposal.md)
verifies the exact recorded 520,789,917 payload bytes against saved sizes and
published SHA-256 values. System unsquashfs reads both files without executing
application code. Full listings, extracted desktop/icon/AppRun evidence,
symlink targets, tool versions and transformed desktop copies are retained in a
manifest-checked compact archive linked by the report and JSON receipt.

20x has one regular root desktop; 2fac has one logical desktop through a root
symlink. Both icon chains resolve internally. No hidden/additional desktop
entries were found. Current shared transformation retains 20x's `--no-sandbox`,
while the original recipe strips it: unchanged shared conversion of the pair is
not recommended without an explicit launcher decision. The report gives exact
IDs, patterns and proposed policy settings, plus ownership/removal and existing
installation gates. 2fac may be scoped independently in a subsequent conversion.

Validation: prior archive/response hashes, full payload digests, fresh evidence
archive/manifest hashes, complete desktop inventory, desktop text transformations,
original recipe hashes and whitespace checks pass. No runtime suite or real app
launch is claimed. No conversion, enrollment, installed inspection/mutation,
deployment, publication, workflow, push or yadm change occurred. The inspection
and proposal are complete; policy acceptance and conversion require separate scope.
