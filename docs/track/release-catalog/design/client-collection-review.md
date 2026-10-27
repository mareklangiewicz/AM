# Client policy and collection boundary — review proposal

2026-10-27. Ticket 11. Proposal only; no production schema adoption or operational
authorization. This review follows the completed offline storage and freshness
experiments. Decisions below remain pending Marek's answers.

## Recommended decision 1: keep the demonstrated freshness contract

Use validation age <= 86,400 seconds as fresh, greater age requiring explicit
acceptance. Refuse future validation/publication timestamps instead of clamping
negative ages. Keep receipt and validation times and their provenance separate.
A missing or fixture-only time is not production freshness.

Bind stale acceptance to the full publication commit, descriptor ID and exact
body SHA-256. No acceptance overrides unknown/unavailable/retired sources, removed
aliases, missing files or failed integrity checks. This can prompt again when
unrelated updates create a new publication during an outage; accept that explicit
tradeoff for the first bounded client contract. Defer a persistent consent store,
clock tolerance and installer UI rather than silently introducing them.

This recommendation is grounded in ticket 10's synthetic experiment, not proof
that every real client clock is correct. Future skew handling remains revisable.

## Recommended decision 2: design the restricted-token collector first

The earlier anonymous-first preference in storage-publication-v1.md was too strong.
GitHub says the built-in GITHUB_TOKEN has repository permissions limited to the
workflow repository. Release documentation says published information is public,
while draft listings require push access. Together these support the inference
that AM's workflow token lacks privileged release visibility into unrelated
repositories. This is a documented boundary argument, not a live visibility test.

Use only the job's built-in GITHUB_TOKEN, contents:read, and no PAT, broader App
token, ambient gh authentication, SSH credentials or other collection identity.
Explicitly exclude the workflow repository by immutable repository ID, including
all name/numeric aliases. Reviewed source enrollment must record identity evidence;
name comparison alone is insufficient. Do not dynamically enroll unknown targets.
Any change to credential scope or workflow-repository identity requires review.

Keep exact descriptors, no automatic redirects, strict public-header allowlisting,
draft/shape refusals, measured response completion and existing storage checks.
If an upstream becomes private, the token must not gain privileged access: refuse
current reads on non-rate-limit auth/absence responses, preserving historical
provenance under the existing retention proposal. Previously public Git history
cannot be made secret by changing current availability; visibility-related removal
and retention expectations remain a later operational decision.

Publication remains a separate permission boundary and is not implemented here.
Design this collector input boundary before choosing remote delivery. An anonymous
fallback would be an explicit different identity and request, not an automatic
retry; leave it absent initially.

## Capacity evidence and proposed future manual-job envelope

GitHub documents 60 anonymous requests/hour per IP and normally 1,000/hour for
GITHUB_TOKEN. The existing probe reported 5,000/hour for that particular token/run.
Preserve both facts without substituting the observed limit for the documented
planning baseline. The 8,337-URL inventory implies 347.4 calls/hour for one daily
sweep before failures/overhead; it is not a verified endpoint list or scheduler.
One-IP anonymous capacity does not support that arithmetic target. Shared runner
IP contention and secondary limits further prevent a throughput guarantee.

If later approved, the first bounded job would retain the six reviewed descriptors:
maximum six release GET attempts, serial execution, no pagination follow-up,
redirect/retry or implicit fallback. Proposed connect timeout 10 seconds, per-request
timeout 30 seconds, job timeout five minutes. Stop immediately on quota evidence,
non-rate-limit authentication failure or descriptor/provenance failure; stop after
two consecutive transport/5xx failures. Preserve partial run evidence explicitly.
Do not call /rate_limit just to consume a seventh request. Use response headers;
stop if reported remaining capacity is <=100 or Retry-After is present. This is a
conservative six-source proposal, not a fleet scheduler or demonstrated capacity.

Use the existing proposed body/index/tree caps (8,000,000 / 2,000,000 / 50,000,000
bytes), six-source cap and separately measured local-history limit. Missing response
quota headers must not be interpreted as unlimited quota. Before dispatch, reviewed
code must prove credential selection, repository-ID exclusion, output bounds and
response timing offline. The envelope does not itself authorize any live run.

## Design tree and pending frontier

1. Freshness contract: accept/revise inclusive 24 hours, no future-clock tolerance
   and commit/descriptor/digest-bound acceptance.
2. Next design direction: accept/revise the restricted-token, external-repository
   collector boundary before remote delivery.
3. After those answers: refine implementation acceptance and any disputed policy,
   then prepare reviewable code. No experiment dispatch follows automatically.

## Primary sources checked 2026-10-27

- [GITHUB_TOKEN scope](https://docs.github.com/en/actions/concepts/security/github_token)
- [Cross-repository privileged access](https://docs.github.com/en/actions/concepts/security/compromised-runners)
- [Release visibility](https://docs.github.com/en/rest/releases/releases)
- [REST rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)

Local evidence: research/probe-run-40496182929-findings.md,
research/request-inventory-findings.md and research/freshness-prototype-findings.md.
No new upstream API observation was made; web reads were documentation research.
