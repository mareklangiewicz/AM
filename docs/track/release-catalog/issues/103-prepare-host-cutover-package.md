# Inventory installed clients and consolidate an exact cutover package

Type: task
Status: resolved
Triage: ready-for-agent

Continue 102 after Marek's go-ahead. Read-only inventory of this host's AM
manager, configured AppMan roots, installed updaters/recipes and runtime hashes;
no updater/manager execution, host mutation or network acquisition. Consolidate
main's authoritative records and all inherited YAML candidates in one isolated
branch. Build an exact-source, hash-checked local review package with source
files, installed-client inventory, deterministic bound replacement recipes,
module/manager delivery evidence and explicit eligibility/refusal reasons.
Test reproducibility, tamper/drift refusal and disposable-root binding behavior.
Use code-review's separate standards/spec axes against the consolidated base.

Source coverage is not installed-client coverage. Do not treat 475 enrolled
paths as every shared source recipe. Preserve existing format-1 client support;
record a separate format-2 publication ref as a cutover proposal if inventory
makes an immediate single-ref switch unsafe. Wire that fixed candidate namespace
through YAML prior/publication/client resolution and test isolation from format 1;
keep the proposed workflow inactive. This is local preparation, not ref creation. Do not invent publication pins,
selected records, capacity/policy acceptance or host-wide client completeness.

No push, source/catalog publication, workflow activation/dispatch, installed
changes, repin, main runtime promotion or yadm changes. Commit local work and
record a concrete remaining cutover sequence and blockers.

## Answer

Isolated prep/yaml-cutover-package consolidates main records and all inherited
YAML source candidates at ee89ef3bd42aed9d5613650b15c976823f73f281.
[Host inventory, exact package, tests and next sequence](../research/yaml-host-cutover-package.md).
Frozen source bbfc63fad0c59a7cfb4098abe8cb5ece1a35107e builds/verifies a private
69-payload-file local package with exact runtime/source, before-images and bound
replacements for obsidian/nvim/nvim-nightly. Read-only /opt/account inventory
finds four managed catalog clients (Sunshine is not enrolled) and 17 legacy
updaters. Source coverage is 475 format-2 and 987 remaining format-1 shared paths.
Separate fixed release-catalog-yaml-v2 client/prior/CAS wiring is prepared locally;
format-1 ref/default and all active workflows remain unchanged.

59 distinct scoped tests pass, plus final targeted shared-constructor validation.
One Standards duplication finding and two Spec drift/collision findings were
fixed and confirmed; both axes have zero remaining findings. Package manifest
SHA-256 and full pins are recorded in the findings. No publication/selected pin
was invented; apply_ready=false. Installed migration, capacity/policy acceptance,
Sunshine/legacy expansion and live cutover remain separate. No host mutation,
push, live acquisition/publication, workflow activation, repin or yadm changes.
