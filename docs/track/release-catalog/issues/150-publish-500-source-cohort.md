# Publish the verified cohort at the 500-source ceiling

Type: task
Status: resolved
Triage: ready-for-agent
Blocked by: 149

After 149's real-cohort density/capacity and preservation checks pass, present the
concrete source commit and ask Marek for the push/publication call. Proposed scope
is 509 apps / 500 numeric sources, adding 184 catalog-only app identities / 180
sources to the published 325-app / 320-source baseline. Keep existing limits;
no recipe migration, installed refresh, app update or yadm pointer bump is included.

Publish only against the actual current remote parent with the maintained
500-source batch workflow. Inspect all source outcomes, pending apps, quota/budget
stopping and history diagnostics. Verify the exact published pin and actual parent
through bounded distributed-reader, canonical/reference and identity/retained-release/
effective-observation preservation checks. A local rehearsal pin is not a substitute
for live verification. Scope/capacity problems require an explicit smaller verified
cohort or a separately measured proposal; do not silently widen limits.

Preparation: [real-source cohort report](../research/next-500-catalog-expansion.md).
No push or dispatch is authorized by this ticket alone.

## Authorization

Marek answered “yes” to pushing and publishing the prepared cohort at
`84d19a4c2`. Proceed with source push, workflow dispatch and exact-pin verification.

## Answer

Authorized source `b2e63b11a` is pushed. Manual run 42385542750 succeeds for
all 500 sources in one batch, zero failures/unattempted/pending apps, publishing
509 app identities at `cbda9fb78ce4a6f29bdabd63d57f3c0085e8744f` as a direct
child of actual parent `08a0fbd526156a456a8648e71d9d2be11734bc74`.
Both exact pins pass bounded reader/canonical/reference and prior identity,
retained-release and effective-observation preservation checks.
[Report and receipt](../research/next-500-publication.md) record 518.95 seconds
command, 341,439,276 response bytes, 63,690,470 YAML bytes and unchanged limits.
No installed-host change; broad 138 remains claimed and discovery follow-up 151
remains open. Real 500-source CI operation is observed; thousands are not qualified.
