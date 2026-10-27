# Review client policy and public-only collection boundary

Type: grilling
Status: claimed
Triage: ready-for-human
Blocked by: 10

## Question

Which bounded operational design, if any, should follow the completed offline
storage and freshness experiments?

## Review inputs

[Client findings](../research/freshness-prototype-findings.md) and
[storage refinements](../design/storage-publication-v1.md#2026-10-27-offline-review-refinements).

## Decisions needed

- Accept or revise the inclusive 24-hour freshness edge, no-skew refusal and
  consent bound to publication commit/descriptor/body. Commit-bound consent can
  repeat during an outage even when bytes are unchanged.
- Choose how to establish public-only collection across visibility changes.
  Anonymous collection avoids privileged reads but its usable quota has not
  been measured here. Workflow-token quota does not establish anonymous capacity.
- Decide whether to design that collector boundary or remote delivery next.
  Specify bounded live request/job/error budgets before any live experiment.
- Review separate receipt/validation timing provenance, independent alias state,
  re-enrollment and the experimental size caps before production schema adoption.

## Scope

Review and design only. No HTTP, Actions dispatch, schedule, installed-app change,
client migration or remote publication is authorized by this ticket. Pushes must
remain independent of experimental dispatch. No day observation is required.


## Comments — 2026-10-27 review round 1

Marek authorized continuing. Prepared a [concrete review proposal](../design/client-collection-review.md)
with two pending decisions: retain the demonstrated freshness/consent contract,
and design the restricted workflow-token collector before remote delivery.
Official documentation supports a narrower credential boundary than the previous
anonymous-first preference: workflow-token privileges are limited to the workflow
repository, which must be excluded by stable ID and aliases. This is an inference,
not a new live visibility test. No broader credential may enter collection.

Preserve documented 1,000/hour planning and measured 5,000/hour run evidence
separately. Proposed first-job bounds are six attempts, serial, no retries/redirects,
explicit time/byte/error limits. No dispatch or implementation is authorized by
this proposal. Ticket remains claimed/ready-for-human pending policy answers.
