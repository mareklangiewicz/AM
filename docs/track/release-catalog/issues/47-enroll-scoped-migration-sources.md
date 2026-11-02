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

## Rollout preparation — 2026-10-31

Marek authorized preparation of the concrete seven-source rollout for review after
verified six-source daily operation and delivery of ticket 66. Prepare and validate
the local manifest/controller/workflow switch, exact source commit and guarded
execution/rollback payload. This authorization does not include source push,
live collection/publication or schedule repinning. Existing live operation remains
six-source; 48/49 remain blocked until accepted operational evidence exists.

## Rollout package ready for approval — 2026-10-31

[Concrete rollout and rollback](../design/am-utils-seven-source-rollout.md) prepares
the local operational manifest switch, controller hash and workflow labels.
Manifest SHA256 is
`96fd3477b59a9806584f155c9180be1cd9c7ce368d02e0973b28afd2e0c4da62`;
all original six rows are unchanged. Reviewed live source/pin both remain
`6dddde9f6f55a7f0919d59fc8be56aa93acb33ac`, with observed publication parent
`067f236b205d8fe01c6f4e79744887e4979437fc`. Recheck these before execution.

The full offline suite passes 199 tests. Current 356 recipe hashes and every
selected real asset reproduce the retained post-fix audit exactly. Replay proves
the same 7,621,340-byte tree and 553,748-byte ZIP within unchanged caps; local Git
object growth was 147,188 bytes in this replay, not operational history growth.
Historical six-source test fixtures now load their original archived manifest so
operational enrollment can advance without rewriting historical evidence.
[Verification payload](../research/am-utils-rollout-20261031.json) records exact
sources, implementation hashes, selector audit and replay results.

Status remains claimed/partial, ready-for-human. Approval must identify the actual
candidate commit SHA and cover source push, exactly one bounded seven-source
collection/publication, evidence acceptance and daily repin, with the documented
bounded rollback if needed. No live metadata request, dispatch/publication,
source push, repin, enrollment or host operation occurred in this preparation.
The utility-source acceptance may subsequently unblock 48; 49 remains blocked on
its separate AppImage enrollment. Do not resolve all of 47 from the utility stage.

## Utility source accepted — 2026-10-31

Marek approved the exact `c787efe3a42fac015f743255006fddd7ea9b3817` rollout.
[Live acceptance and retained evidence](../research/am-utils-live-20261031.md)
verify run 41232846271, publication `a113cd0aca3247111b6ba231f6a30b6477ac2c75`,
seven successful attempts, exact-prior recomputation/published tree, 356/356
unchanged-recipe asset selectors, actual pinned readers and unchanged resource caps.
Daily source/pin equality now uses the approved candidate, after acceptance.
Utility enrollment is accepted and 48 is unblocked. Status stays claimed/partial;
49's separate enrollment remains blocked. Natural seven-source repeat evidence
is still pending; no second manual run or recipe/host migration was performed.

## First deferred subset prepared offline — 2026-10-31

On “continue”, checked the next boundary and prepared the first frozen queue row:
[Brave subset and staged review](../design/brave-enrollment-preparation.md), with
[six recipe fingerprints and exact selectors](../research/brave-enrollment-preparation.json).
All install/update selector pairs match and shell syntax passes; baseline is
462 lines / 19,164 bytes. No numeric ID or asset availability is inferred.
Read-only GitHub inspection found no new run after 41232846271 and unchanged
publication `a113cd0ac`; natural seven-source repeat/retention remains pending.
The existing staged plan requires that evidence before proposing the next live
subset. No live identity/release request, manual dispatch, enrollment, host delivery,
source push or repin occurred. Status stays claimed/partial, 49 blocked. Next live
proposal will need a concrete reviewed runner and separate identity-only approval;
the saved am-utils runner is only a reference at this stage.

## Brave evidence stage accepted for preparation — 2026-10-31

The user approved proceeding with bounded identity/release checks without waiting
for natural repeat, superseding the preceding wait-before-evidence sequencing.
[Actual evidence](../research/brave-enrollment-findings.md) records exactly two
unauthenticated HTTP 200 GETs: public repository ID 947512058 and numeric releases
(639,169 bytes, 30 releases / 336 assets). All twelve original install/update
selectors for six Brave recipes select actual assets; frozen source hashes match.
Queue mapping updated, operational manifest unchanged. No pagination, retries,
binaries, recipe migration, push, repin or host operation. Status remains partial;
49 requires actual accepted operational publication. Natural repeat is independent
and still unobserved; next preparation is the offline eight-source contract.

## Brave eight-source offline contract — 2026-10-31

The user authorized the next offline preparation. [Contract and rollout review](../design/brave-eight-source-preparation.md)
preserve all seven accepted descriptors and add exactly Brave in a separate
candidate manifest, SHA256 `dfca1d3e7504e4c6fa83ae6260ba1bb6e2db4cca736fb3693db9ec4aeea1a8bf`.
Planner cap is eight; six/seven historical manifest profiles remain readable.
Ninth-source refusal happens before transport/credentials. Byte/time limits,
transport/storage/publisher runtime, operational manifest, workflow bytes and
seven-source controller hash remain unchanged.

[Replay](../research/brave-eight-source-replay.json) uses the hash-bound accepted
publication `a113cd0ac`, real retained Brave bytes and labeled synthetic seven 304s:
8,263,578-byte tree, 508,768-byte ZIP, 45,147-byte temporary Git object growth.
These are offline costs, not measured production churn or timing. Eight nominal
requests leave 60 seconds of the existing batch budget for overhead; actual future
collection may refuse rather than silently expanding caps.

A separate [six-file activation patch](../design/brave-eight-source-activation.patch)
prepares manifest/hash/workflow-label and operational-test changes. It was applied
only to a temporary copy, where 22 affected tests pass. Focused enrollment tests
cover real retained bodies, synthetic failures/repeats, exact-parent publication,
all aliases and actual pinned shell reader freshness/consent/integrity behavior.
Initial full-suite validation exposed an old preflight fixture that still called
eight sources excessive; updated to nine, and all 17 collector tests pass.
Final complete-suite results are recorded below after execution.

Retained identity/release evidence and exact original-selector audit are committed
locally as `104b06682`; raw HTTP headers preserve exact CRLF bytes in Git, with
staged hashes checked against the transport reports. No source push, live request,
collection/publication, daily repin, recipe conversion or host delivery occurred
in this offline stage. 47 remains partial/claimed and 49 blocked until separately
accepted operational availability; other 49 deferred endpoints are untouched.

Final [verification record](../research/brave-eight-source-checks.json): all **212**
catalog tests pass in 197.600 seconds; 22 activation checks pass in the temporary
copy. Recorded implementation fingerprints, new document links, exact retained
body/header Git hashes and diff checks pass. The operational manifest, workflows,
controller, modules and recipes remain byte-identical to published `7b31340a8`.
The containing preparation commit remains on local main-marek; a separate local
`prep/brave-eight-source` activation candidate applies only the six-file patch.
Its full SHA is supplied in the completion message for exact review. Neither
local commit nor activation branch is pushed, dispatched or pinned.

## November 2 accepted Brave stage

[Live acceptance](../research/brave-live-20261102.md): approved source
`3c44b0ba45bb78f5c55f61b179c9cc4a068c82d5`, one successful eight-source run
41429379232, exact publication `4c6000aea8704d6585325146b85ebdf21cf0a628`,
12/12 original selectors and both pinned readers verified, then daily repinned.
[Natural seven-source repeat](../research/daily-refresh-20261101.md) is also verified.
Only six Brave paths in 49 are unblocked; remaining 49 endpoints remain deferred.
Status stays claimed/partial. No host delivery or additional collection.
