# Review armhf eligibility in generic recipe declarations

Type: task
Status: open
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
