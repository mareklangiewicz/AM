# Prepare explicit installed recipe migration transactions

Type: task
Status: claimed
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
