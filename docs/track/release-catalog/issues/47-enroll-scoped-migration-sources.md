# Review and stage enrollment for the concrete migration batches

Type: task
Status: claimed
Triage: ready-for-human
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


## Approved bounded release stage — 2026-10-28

The user's follow-up approved the next bounded release read. One unauthenticated
numeric GET returned HTTP 200: 2,722,290 bytes in 1.777211 seconds, six releases /
1750 assets. [Exact evidence and offline audit](../research/am-utils-release-findings.md)
retain request/body/header hashes, bounds and original-selector differential checks.
All 356 selectors reproduce original behavior; 354 select actual assets. Both
c++filt recipes miss because actual URLs encode the plus signs as `%2B%2B` and
the original patterns use unescaped APP regex text. Diagnostic only; filters were
not changed. No additional request or automatic fallback.

This supersedes the earlier missing numeric-route evidence, but does not establish
full family compatibility or operational enrollment. Next is explicit treatment of
the two selector exceptions and coordinated seven-source offline storage/delivery
verification, before a separately approved collection/publication stage. Six-source
manifest/guards, pilot source pin and schedule are unchanged. Status remains
claimed/needs-info, with 48/49 still blocked.


## Authorized offline selector/contract preparation — 2026-10-28

Marek approved repairing the two c++filt selectors and preparing/testing the
seven-source path offline. Commit `033ed3d57` fixes both actual install/update
filters to match encoded-plus asset URLs; focused regression was red before/green
after, and the separate [post-fix audit](../research/am-utils-release-20261028/selector-report-fixed.json)
confirms all 356 selectors choose actual retained assets. The historical 354/356
report remains unchanged. Shell syntax passes; warning ShellCheck reports only the
pre-existing unused SITE assignment in both legacy recipes.

[Seven-source preparation](../design/am-utils-seven-source-preparation.md) records
the separate candidate manifest, coordinated count guards, exact-prior tests and
resource replay. Historical six-source manifests remain readable; the operational
manifest/workflow paths/controller hash remain unchanged. Max seven planned
requests, each once, exact approved attempt count and all-source success remain
required; byte/time caps are unchanged.

The offline candidate tree is 7,621,340 bytes, compressed test artifact 553,748
bytes, temporary local object-file growth 147,193 bytes. These use genuine saved
bodies and explicitly synthetic six-source 304 events, not a live workflow or
new publication/freshness claim. Storage/ZIP/publisher/readers, failed seventh
source, exact conditional handling, byte/count bounds and local Git parent/child
are verified. The new source is not yet available in the operational catalog.

Status remains claimed/partial; triage is now ready-for-human for the next scoped
acceptance after 37's closure and coordination with the already authorized
six-source daily switch. No push, remote repin, workflow/schedule or host change,
new collection or live publication occurred. 48/49 remain blocked.


Final [verification record](../research/am-utils-enrollment-preparation-checks.txt):
192-test full catalog suite plus the newly added staging regression pass, covering
193 distinct tests; focused enrollment seven and supervised transport 21 pass.
Operational manifest hash, syntax/diff/link checks and unchanged warning baseline
verified. No outstanding offline failure; remaining work requires actual accepted
live enrollment/publication and does not justify resolving this ticket yet.
