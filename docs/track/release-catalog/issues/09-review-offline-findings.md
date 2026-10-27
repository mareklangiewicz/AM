# Review offline findings before operational implementation

Type: grilling
Status: resolved
Triage: ready-for-human
Blocked by: 08

## Question

Do the bounded [offline findings](../research/storage-prototype-findings.md)
justify accepting or revising the storage/publication proposal before defining
remote publication work?

## Decisions to review

- Manifest embedding and explicit historical timing provenance; saved evidence
  cannot supply exact per-response completion times.
- Public-only enrollment method and exclusion of privileged token visibility.
- Whether to pursue a client freshness prototype or a bounded remote publication
  design next; neither implementation nor live runs are authorized by this ticket.
- Storage/job/request limits and retention/packing assumptions before expansion.
- Re-enrollment and alias-removal policy if needed beyond the six-source fixture.

## Scope

Review only. No HTTP collection, Actions dispatch, push, remote publication,
schedules or client migration. The publication branch name and remote delivery
transport remain undecided. No day sample is required.


## Answer — 2026-10-27

Marek authorized continuing the review. The bounded findings justify another
offline prototype, while the production schema and operational approach remain
unaccepted. [Review refinements](../design/storage-publication-v1.md#2026-10-27-offline-review-refinements)
record measured completion requirements, separate receipt/validation timing
provenance, embedded manifest verification, proposed experiment caps and the
public-only enrollment gap. Anonymous collection is an option to evaluate, not a
live collection decision; workflow-token quota evidence does not apply to it.

Review also exposed two schema gaps: a single timing-basis field conflates saved
receipt and later validation, and descriptor retirement cannot represent removal
of one alias while another remains active. Preserve those as explicit follow-ups.

[10](10-offline-client-freshness.md) defines the next offline frontier, including
exact freshness edges and acceptance binding. No HTTP, push, dispatch, scheduling,
remote publication or migration was authorized or performed by this review.
