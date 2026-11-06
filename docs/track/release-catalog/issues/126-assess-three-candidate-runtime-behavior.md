# Assess runtime behavior for three template migration candidates

Type: task
Status: open
Triage: ready-for-agent

Follow [125](125-recognize-default-appimage-selector.md) with an independent,
offline assessment of 20x, 2fac and 4nier-patrimonio before any conversion.
Recognition is syntactic accounting; it does not establish runtime equivalence.

## Scope

Use the exact source/template identities and hashes recorded in
[124's report](../research/selector-review-groups.md). Read the current fork
recipes and shared runtime before choosing a proposed declaration. Preserve
original source/template provenance in the assessment and any inert candidates.
Do not replace tracked recipes as part of this ticket.

Compare the pinned upstream selector with proposed catalog selection using local
release/asset fixtures: ordering, multiple matches, architecture alternatives,
prereleases, no matches, missing assets and retained releases outside the first
response page. Record intentional policy differences and unresolved decisions;
do not silently treat first matching URL as newest stable/publication.

Use disposable directories and inert local assets to assess direct AppImage and
archive staging, replacement/backups, failures, desktop/icon/remover output,
standalone updater behavior, and direct download versus appimageupdatetool.
Stub network and external installation commands. Do not run originals against
installed paths or launch downloaded binaries.

## Completion evidence

Produce a per-candidate behavior comparison with reproducible focused checks,
source/template hashes, proposed policy and remaining conversion gates. Record
repository numeric identity only if supported by available primary evidence;
otherwise leave it explicitly unverified. Distinguish differences that need a
policy decision from implementation defects. Recommend a bounded conversion
batch only if the evidence supports it; otherwise record concrete blockers.

No collection expansion, recipe conversion, live installation/deployment,
publication, network acquisition, push or yadm operation is part of this ticket.
Claim before implementation. Conversion/enrollment requires a separate scope.
