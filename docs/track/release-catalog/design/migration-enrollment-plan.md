# Scoped migration enrollment: offline review package

2026-10-28. Ticket [47](../issues/47-enroll-scoped-migration-sources.md), partial
preparation only. No new identity/release request, collection, publication,
workflow change, source push or installed operation has occurred.

## Frozen payload and accepted subset

[Queue payload](migration-enrollment-queue.json) records the exact inventory hash,
current manifest hash, 356 utility recipe paths and 124 later AppImage recipe paths.
It is deliberately **not** a loadable collector manifest. Deferred repository IDs, numeric fetch URLs and request IDs remain null. The
utility candidate now uses reviewed identity evidence; its release route is still
unrequested and it is not operationally enrolled.
The six sources in [staged-manifest.json](staged-manifest.json) remain the entire
enrolled operational subset. Neither proposed stage is accepted/published yet;
48 and 49 remain blocked on actual source availability.

Utility stage first: preserve the exact consumer alias
`https://api.github.com/repos/ivan-hc/am-utils/releases`, with no query or latest
suffix. After reviewed identity evidence, propose only
`https://api.github.com/repositories/REVIEWED_ID/releases` as the fetch descriptor.
Compute its request ID using `collector.Descriptor.request_id`, with API version
2022-11-28 and Accept application/vnd.github+json. No initial validators for this
new descriptor. Do not import validators from a named route or another endpoint.

The deferred queue has 50 exact endpoints and 49 distinct name-based identity
requests: SuperTuxKart list/latest share an identity but remain distinct descriptors.
Repository spelling, suffixes and queries remain byte-exact in the payload. No
request to that queue is proposed for immediate approval. Static caller count
establishes neither release route success nor asset coverage.

## First approval boundary: one identity request

Request approval for exactly **one unauthenticated GET**:

`https://api.github.com/repos/ivan-hc/am-utils`

No push is required for this standalone public identity check. No release request,
workflow dispatch or schedule/source change is included. Follow the previously
used [bounded SQLite enrollment procedure](../research/sqlite-enrollment-findings.md):
clean allowlisted environment; no ambient proxy/config/netrc/gh credentials;
verified HTTPS; pinned Accept/API headers; identity encoding; no redirects,
retries, pagination or follow-ups; 10-second connect and 30-second overall deadline;
64,000-byte header and body caps enforced while reading, retained public header
values <=8,192 bytes. Parent supervision must interrupt/reap the process at its
absolute deadline or overflow, including on slow output. Recheck the runner before
use; a curl completion timeout or post-download size check alone is insufficient.

Retain exact bounded body and public headers, their byte counts/SHA256, local
UTC start/completion, monotonic elapsed time, status and exit/termination outcome
under a new public research evidence directory. Do not record credentials or
ambient host inventory. Require HTTP 200, positive integer `id` (not a release,
asset, owner or node ID), expected full_name case-insensitively, private=false and
visibility=public. Compare against workflow repository identity before future
collection. Redirect, mismatch, overflow, invalid JSON or quota/auth failure stops;
do not silently accept a renamed repository, follow Location or retry.

This request establishes only the observed name-to-ID/public mapping. It does not
prove the numeric release route, selector coverage or continuing identity freshness.
Review and commit real evidence before filling the candidate descriptor. Approval
of this request must not be interpreted as approval of the next stages.

## Second boundary: bounded release evidence and implementation

After identity review, prepare an exact numeric one-release-request proposal,
including a concrete source revision, descriptor/request ID and output paths.
Do not dispatch the current workflow with a one-source replacement manifest:
its loader requires six and storage would retire omitted sources. A separate
bounded evidence request must not publish or replace the operational tree.
Use the existing supervised transport's 8,000,000-byte body cap, 64,000-byte
header cap, 10-second connect/30-second request deadline and no redirects/retries/
pagination/fallback. Retain exact response bytes and actual timing/status/validators,
not a reconstructed summary. A failure preserves its evidence, without fallback.
That request needs separate authorization once its payload/runner is reviewable.

If accepted evidence fits the body cap, validate the entire release shape and run
all 356 original selectors against the saved bytes without executing installers,
updaters or downloaded assets. Preserve APP, architecture, filename/date filters,
JSON token order and original binary URLs. Report missing/multiple matches and
stop incompatibilities rather than adjusting filters to fit the sample. A new
observation must support the real family before claiming ticket 48 is unblocked.

Only then implement/review the smallest seven-source contract across planning,
manifest loading, attempt enforcement, storage and artifact reconstruction; do not
blindly replace every six literal or relax resource limits. Preserve the six old
rows/descriptors/aliases/evidence exactly and replay an exact retained prior tree.
Verify initial new 200, matching conditional 304, failure retaining previous age,
missing/invalid/oversized results, mixed successful/failed collection, exact
artifact recomputation/publication parent and pinned reader lookup. Check both
shell and reference readers and active aliases after publication reconstruction.
No one-source publication may retire the six existing observations. Current delivery
requires all transitions observed/validated: a failed seventh source blocks the
whole publication even when storage retains prior observations. Test and preserve
that refusal; changing partial-publication policy needs an explicit contract decision.

Current code ownership and limits are audited in
[the offline source audit](../research/am-utils-enrollment-audit.md).

## Capacity and retention acceptance

Keep the 300-second batch deadline, 8 MB per body, 2 MB index and 50 MB current tree
caps. Seven 30-second requests have a 210-second nominal request budget, but process,
serialization and publication overhead still need actual measurements. Seven
8 MB bodies alone could reach 56 MB, exceeding the tree cap before index/lookup;
there is no worst-case seven-source guarantee. Refuse an oversized candidate rather
than publishing partial corruption or raising the cap without review.

Measure exact prior and candidate body/index/lookup sizes, serialized artifact size,
request/total duration, 200/304 transferred bytes and validation results. Preserve
the existing complete prior and all six source validators/ages through failed new
attempts. Current-tree pruning is not Git history retention: compare reachable
object growth for one genuine publication and, after separately accepted repeated
operation, actual churn. A single baseline cannot prove daily retention cost.
Do not fabricate a conditional response or advance observation timestamps to
simulate capacity/freshness evidence.

After offline implementation and evidence review, prepare a separate explicit
seven-source collection/publication approval with exact code/manifest SHA, remote
parent, expected requests, storage bounds and workflow isolation. Wait for hourly
pilot closure (37) and coordinate with the authorized daily activation (41), whose
scope remains **six** sources. New enrollment must not hitchhike on that approval.
Keep old source pin unchanged during the pilot. No synthetic daily test dispatch.

## Later AppImage stages

Do not enroll all 50 endpoints at once. Use queue order (shared callers first,
then exact URL as frozen by the inventory) to propose a bounded next subset only
after utility collection/delivery/retention measurements. Reuse genuine identity
evidence when an exact name mapping is established; retain separate numeric
list/latest/query descriptors and validators. Each stage records accepted subset,
resource measurements and actual publication commit. Full ticket 47 resolution
requires its dependent enrollment scope actually accepted and available; utility
completion can unblock only 48 while the remaining queue stays explicit here.


## Identity stage completed — 2026-10-28

The user approved only the first identity request. It returned HTTP 200 and
confirmed public `ivan-hc/am-utils`, ID **1225768109**.
[Exact evidence and findings](../research/am-utils-enrollment-findings.md) were
committed as `4a9aadb90` before filling the candidate queue fields.
The candidate fetch URL is now
`https://api.github.com/repositories/1225768109/releases`; the queue computes its
request ID from the exact pinned representation and starts without validators.
The historical first-stage instructions above explain the procedure; this evidence
supersedes only its missing-identity state. No second-stage request is authorized
or performed. Six-source operation and 48/49 blockers remain unchanged.
