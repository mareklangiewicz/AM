# Publish the verified 320-source catalog cohort

Type: task
Status: resolved
Triage: ready-for-agent
Blocked by: 147

After 147's recorded preflight passes, ask Marek to authorize pushing its source
commits and dispatching the metadata workflow. The proposed enrollment is
325 apps / 320 numeric sources, adding 97 catalog-only apps / 96 sources.
No recipe migration, host deployment, app update or yadm pointer bump is included.

Use the actual remote catalog parent at publication time. Run the maintained
500-source batch workflow, inspect all 320 source outcomes and pending-app counts,
and verify the exact published pin with the bounded reader, canonical/reference
checks and prior identity/release/effective-observation preservation. If the
parent has advanced, do not substitute the rehearsal pin or its recorded parent.
Preserve the 500/hour profile, existing bounds and 48-hour selected-record rule.

Preparation report: [next cohort](../research/next-320-catalog-expansion.md).
No push/publication is authorized by this ticket itself.

## Authorization

Marek answered “yes” to pushing and publishing the prepared cohort at
`74289d3ce`. Proceed with source push, workflow dispatch and exact-pin verification.

## Answer

Authorized source `5d7af4347` is pushed. Manual run 42369094432 succeeds for
all 320 sources in one batch, zero failures/unattempted/pending apps, publishing
325 app identities at `08a0fbd526156a456a8648e71d9d2be11734bc74` as a direct
child of actual parent `59b3f3f398bc1013c7b5caf0f37b19a4f3fc9821`.
Exact-pin reader/canonical/reference checks and prior identity/retained-release/
effective-observation preservation pass. [Report and receipt](../research/next-320-publication.md)
record live metrics, document/log digests and remaining limits.
No installed-host changes; broad 138 stays claimed.
