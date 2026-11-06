# Review armhf eligibility in generic recipe declarations

Type: task
Status: resolved
Triage: ready-for-agent

[126's offline assessment](../research/three-candidate-runtime-assessment.md)
shows that the maintained x86_64 declaration guard admits App-armhf.AppImage
under a broad AppImage suffix pattern, while the inspected upstream selector
rejects armhf. This is a synthetic eligibility gap, not an observed wrong download
for a real candidate. Decide and document the generic architecture eligibility
contract before adjusting the shared guard; inspect all supported architectures
and existing declarations rather than patching an application-specific pattern.

Use actual maintained awk selection with independent fixtures for armhf, armv7,
arm64/aarch64, x86 variants and unlabelled names across supported architectures.
Keep intentionally accepted unlabelled-name behavior explicit. Cover selection
and no-match refusal and verify existing declared recipes' focused checks. Update
126's assessment oracle if the accepted contract changes its documented gap.

Record source change and verification, with no live deployment, recipe conversion,
collection expansion, network acquisition, publication or push. Resolving this
gap alone does not verify candidate repository IDs, real asset names/desktops,
or authorize conversion of 20x/2fac or addition of 4nier-patrimonio.

## Decision before implementation

Treat armhf as a 32-bit ARM hard-float label, not proof of ARMv7. Reject that
label on x86_64, aarch64 and i686, even when another matching architecture label
also appears. For armv7l, continue requiring an explicit armv7 label; a combined
armv7/armhf name may match. Preserve x86_64's existing acceptance of unlabelled
names, and the positive-label requirements on other supported architectures.
Matching stays case-insensitive for architecture labels over asset names;
trusted asset patterns, channel and OS rules still apply. This is a filename
eligibility contract, not verification of payload architecture or URL parity.

## Answer

Implemented the contract above in the maintained declaration selector only;
transitional named policies and generated registry data remain unchanged. The
[tools README](../../../../tools/catalog-collector/README.md) documents the full
name-filter contract. Updated 126's current oracle and appended a historical-
evidence follow-up without rewriting its old source comparison.

A new 24-name by four-architecture matrix exercises actual compiled declarations
on mawk, gawk and BusyBox awk: 288 selection/refusal checks, including mixed and
uppercase armhf labels, explicit armv7/armhf names and unlabelled names. All
11 declaration/compiler/selection tests pass (5.711 s), all 33 reconstruction/
assessment tests pass (7.688 s), and all 16 existing host lifecycle/cutover groups
pass (86.502 s): 60 focused tests total. No full catalog/container run or independent
review is claimed. No recipe, enrollment, installed runtime or live file changed.

Read-only primary evidence preparation for the existing pair continues in
[128](128-verify-two-candidate-upstream-evidence.md). Fixing the name guard alone
does not establish binary architecture, URL/name equivalence or conversion readiness.
