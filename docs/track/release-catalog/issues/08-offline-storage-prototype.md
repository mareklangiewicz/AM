# Verify storage and publication semantics offline

Type: prototype
Status: open
Triage: ready-for-agent
Blocked by: 07

## Question

Does the proposed exact-response format preserve provenance and freshness while supporting consistent selective reads from a publication commit?

## Scope

Use [v1 proposal](../design/storage-publication-v1.md), the complete baseline/hour evidence and synthetic failures. Create an offline temporary publication tree and local Git commits only. No HTTP, remote Git writes, Actions dispatch, installed-app changes or client migration. The proposal is revisable based on findings.

## Acceptance

- Exercise the apply interface with exact bodies, conditional 304, missing/mismatched body, empty lists, temporary errors, absence, redirects, invalid data and retired sources.
- Validate alias/descriptor identity, hashes, timestamp semantics, public-source enrollment, schema and safe paths.
- Show commit-pinned reads remain consistent as a new local publication appears; refuse a stale expected parent without force push.
- Record byte preservation, body/index/loose/packed sizes and any necessary schema revisions.
- Preserve app selection outside the storage module. Real public visibility, hosting delivery, remote write isolation and fleet retention limits remain separate work.

## Starting evidence

Use research/churn-hour-40508899451-evidence.tar.gz, which contains baseline and hour rounds. The failed baseline is separate evidence and must not be passed off as complete. The illustrative JSON index is not a valid full publication fixture: its manifest hash and exact receipt/validation timestamps are intentionally incomplete.
