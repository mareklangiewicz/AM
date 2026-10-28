# Review and stage enrollment for the concrete migration batches

Type: task
Status: claimed
Triage: needs-info
Blocked by: 45

## Scope

Prepare a concrete reviewed enrollment plan for the batches frozen in
[recipe-family-inventory.json](../research/recipe-family-inventory.json), beginning
with the single `https://api.github.com/repos/ivan-hc/am-utils/releases` request
(356 recipes), then the `proposed_enrollment_batch`'s 50 exact AppImage endpoints
(124 recipes). Keep every query, endpoint, repository spelling and alias exact;
plain `/releases` and `/releases/latest` remain different requests. No collector-side
asset resolution, runtime language dependency or silent endpoint substitution.

First prepare offline: inventory descriptor/provenance requirements, reuse genuine
saved identity evidence where available, enumerate missing evidence and specify
exact bounded identity/release requests needed. Do not invent numeric repository
IDs. Build a concrete reviewable payload and precise approval request before any
new live requests, collection, publication or schedule/source change; this ticket
is not authorization for those operations. Approval and evidence can progress the
same ticket in measured enrollment stages; do not create validation-only tickets.

Current plan/manifest/storage assume six sources/attempts; transport has an 8 MB
body cap, 300-second batch deadline and storage a 50 MB tree cap. Start with the
one-endpoint utility increment and prove its complete delivery/retention/resource
contract before extending the AppImage queue. Design bounded planning from actual
cost, rather than blindly changing six to 57 or relaxing existing refusal guards.
Retain existing sources, exact prior state, request identity, source pin/isolation,
conditional requests and unchanged observation age after failures. Document the
accepted source subset and per-stage publication state explicitly.

Do not disturb the hourly pilot; tickets 37/41's authorized closure/daily activation
remain independent. No external timer, extension or unapproved source push.
Retained observations must support original recipe selectors before dependent
migration is declared compatible. Enrollment/publication is distinct from recipe
implementation and installed payload delivery.

Deliver the reviewed plan, implementation appropriate to the accepted stage,
actual authorized evidence (if subsequently approved), resource/cadence limits
and reproducible checks. Resolve only when the dependent batch enrollment scope
is actually accepted and available; otherwise record exact partial stage/remaining
human action here, keeping blocked migrations honest.

## Partial stage — 2026-10-28 offline preparation

Claimed for offline preparation. [Review package](../design/migration-enrollment-plan.md)
and [exact queue payload](../design/migration-enrollment-queue.json) preserve the
356 utility paths and 50 later endpoints / 49 repository identity requests.
Unknown IDs/descriptors remain null; operational manifest and six-source guards
are unchanged. [Source audit](../research/am-utils-enrollment-audit.md) identifies
evidence gaps and the cross-boundary capacity/delivery requirements.

Awaiting user authorization for the package's one bounded unauthenticated
`GET https://api.github.com/repos/ivan-hc/am-utils` identity read. No release read,
collection, publication, push or schedule/source change is included. Status stays
claimed (partial preparation); 48/49 remain blocked. Do not resolve from a plan.


## Approved identity stage completed — 2026-10-28

The user approved the one bounded repository identity GET. HTTP 200 confirmed
public `ivan-hc/am-utils`, repository ID 1225768109; exact 4965-byte body and
1323-byte headers, hashes/timings and the guarded runner are retained in
[findings](../research/am-utils-enrollment-findings.md), committed as `4a9aadb90`.
Candidate queue fields now use that reviewed ID and computed numeric request ID,
with no validators; deferred rows remain unresolved. This supersedes the earlier
awaiting-identity-approval note.

No release request or enrollment/publication occurred. Next is a separately
reviewable bounded numeric release-read proposal and its authorization, followed
by 356-selector/resource verification. Status remains claimed/needs-info; 48/49
remain blocked. No push, repin, workflow or host change.
