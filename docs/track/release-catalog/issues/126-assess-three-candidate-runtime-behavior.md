# Assess runtime behavior for three template migration candidates

Type: task
Status: resolved
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

## Answer

[Assessment](../research/three-candidate-runtime-assessment.md) records exact
upstream/current-source provenance, a per-candidate readiness comparison and
executable offline evidence. 20x and 2fac remain byte-identical existing fork
recipes; 4nier-patrimonio is absent and would need a separate addition scope.
Numeric repository IDs and real asset/launcher facts remain unverified.

Five new assessment groups pass, including 42 selector comparisons across all
three candidates, stale/identity refusal, inert shared install/standalone update,
custom desktop/data/command preservation, removal, failed transfer/empty asset/
helper refusal, and explicit tar staging. A closed command directory stubs all
network acquisition; no original installer or real app binary executes. The
report records source-only versus executed evidence and untested capabilities.

The exploratory any-channel/name-suffix declaration differs from the legacy
first-URL selector in ordering, URL/name matching, OS rules, retained history and
freshness. It also admits armhf where upstream rejects it. No conversion batch
is approved by synthetic checks. Keep 20x/2fac as the bounded existing-recipe
preparation pair; keep 4nier as source-only comparison. Track the concrete
eligibility gap in [127](127-review-armhf-declaration-eligibility.md). Repository
identity, real asset/desktop evidence, accepted policy differences and an explicit
conversion/enrollment scope remain separate gates. No production source/runtime,
recipe, enrollment, live file, publication, push or yadm change in this ticket.

Final validation: all 33 recipe-reconstruction tests pass in 7.533 seconds,
including the five new assessment groups; changed documentation links and
whitespace checks pass. No final full catalog/container suite or independent
code review is claimed.

## Comments

2026-11-06: Assessment source `a2119bd9f` and prior tracker update `44fe43a1b`
were pushed with Marek's go-ahead. No live deployment. Ticket 127 resolves the
source armhf guard gap; 128 separately gathers real primary candidate evidence.
