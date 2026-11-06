# Investigate shared selector parameter-review groups

Type: research
Status: resolved
Triage: ready-for-agent

Continue ticket 123 preparation: rank parameter-review groups at the pinned
upstream revision, inspect the largest ordinary selector variants, and identify
a bounded candidate family with exact provenance and explicit runtime gates.
Record reproducible evidence. No recipe conversion, enrollment, push or live
change in this investigation.

## Answer

[Investigation](../research/selector-review-groups.md) ranks exact selector groups
at the pinned source. The largest is 4,437 archive-layout recipes explained by
upstream's AIA/default-keyword generator path. Three bounded preparation
candidates have exact template/source provenance. Seven recipes have differing
installer/updater FUNCTION values; the archive-layout consistency gate needs
extension before broadening recognition. Current classifications are unchanged.

Verified recorded JSONL hash, regenerated full inventory summary, reproduced
ranking, and checked hashes/byte-exact expansion for the three candidates plus
pyuploadtool. No runtime equivalence, conversion, enrollment or live operation
is claimed. Next implementation scope: recognize the exact generator-derived
variant with repeated site/FUNCTION consistency and adversarial refusal tests,
then assess the three-candidate runtime behavior independently.
