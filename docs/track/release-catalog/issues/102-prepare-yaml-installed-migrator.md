# Prepare explicit installed recipe migration transactions

Type: task
Status: resolved
Triage: ready-for-agent

Continue isolated candidate 0c157af59. Implement a maintainer-only, explicit
single-installation transaction tool: a reviewable exact-source plan; bound old
and replacement recipe hashes; manager/runtime/updater/binary/version guards;
selected-record preflight before mutation; durable backups, atomic replacement,
receipts, drift refusal and interrupted-rename recovery; guarded recipe rollback.
Exercise disposable roots only. Keep ordinary clients shell-only; this offline
maintainer tool may use the existing Python tooling. Never invoke an updater or
claim binary rollback. A reviewed fully bound replacement is an explicit input;
automatic source-to-installed binding remains outside this increment.

Use code-review's parallel standards/spec axes against 0c157af59. No live
acquisition, installed host inventory/change, push, publication/ref decision,
workflow, repin, main runtime promotion or yadm work. Operational acceptance and
an exact reviewed installation package remain separate.

## Answer

Isolated prep/yaml-installed-migration implements explicit maintainer-only
single-recipe plan/apply/rollback transactions, reviewed at 974cc963a.
Complete clean candidate: 5d410b1a5801a8bfbd75e69195c8a98977de7033.
[Findings and boundaries](../research/yaml-installed-migrator.md). Exact-source
manager/modules and installed hashes, selected-record preflight, durable backup
and intent, atomic metadata-preserving replacement, receipts, drift refusal and
interrupted apply/rollback recovery are implemented. All 11 final disposable
tests pass (119.742 s). Standards review found zero findings; spec found one
post-apply drift defect, fixed and confirmed, with zero remaining findings.

No automatic source-to-installed binding or binary rollback is claimed. A
reviewed exact package, exclusive installation access, manager/module delivery,
installed inventory, policy/stale UI/capacity acceptance and publication/ref
transition remain operational gates. Tooling is isolated/unmerged/unpushed;
normal clients remain shell-only. No live or installed host changes occurred.
