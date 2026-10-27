# Adapter review and inactive run package

2026-10-27, ticket 15. Reviewed starting revision f223153cf on main-marek.
This package is offline preparation; no live request or workflow activation occurred.

## Concrete review

Reviewed collector.py, supervised_transport.py, existing focused tests and the
historical six-source audit. Core revalidation precedes transport calls; numeric
identity and own-repository exclusion precede worker creation. Request IDs bind
exact descriptors. Every planned request starts at most once (six total), without
redirect, pagination, retry or name fallback. The worker destination is fixed,
uses system certificate/hostname verification, isolated Python and an allowlisted
environment. Credentials cross private stdin only, not argv or saved evidence.
These observations concern code paths, not verified token provenance or real TLS.

Found and fixed an HTTP parser gap: email-style header parsing can silently ignore
malformed lines, including a framing header following a malformed field. A short
EOF body could consequently be treated as an unframed complete response. The
bounded reader now rejects malformed field lines and folding before HTTPResponse
parses them. Regression cases cover ignored fields, whitespace before the colon,
leading whitespace, folding and a valid interim 100 response. Strict refusal may
reject legal folded HTTP headers; broadening this requires deliberate review.

Aggregate header and chunk-framing caps precede parser allocation; body and IPC
chunks are bounded. End requires clean worker exit. Absolute deadline checks cover
nonblocking IPC and process waits; iterator cancellation kills/reaps the child.
Cleanup remains subject to POSIX scheduling and a one-second reap allowance.
No additional evidenced defect was found in these reviewed paths. This was a
focused implementation review, not a completed adversarial audit.

## Staged manifest

[Exact JSON](../design/staged-manifest.json) stages six rows with original consumer
aliases, historical evidence pointers, old/new request IDs and route-observation
limits. Its SHA256 is
`008a31f061014b00c93647d8cd317dffbae272ae2671a7caa73e7e904e1747f1`.
SQLite Browser has null identity, URL, evidence and request ID, plus an explicit
candidate path template. Loading refuses with unenrolled_source before transport
or token construction. Never substitute the synthetic test ID into this file.

Obsidian and Neovim use historical list Link evidence for the same reviewed names;
WezTerm uses saved redirect and numeric route evidence. Only WezTerm's exact numeric
route has prior successful observations. Changed descriptors receive new request
IDs. This first proposed run is unconditional for all six, including WezTerm, and
imports no historical validators or Actions artifacts.

## Inactive workflow integration

[Proposed workflow](../design/catalog-collector.yml.proposed) is the exact candidate
content for a future .github/workflows/catalog-collector.yml, deliberately outside
that directory. workflow_adapter.py supplies tested preflight and result writing;
it has no CLI, environment credential lookup or automatic invocation. The proposal
uses the existing checkout/upload commit pins, Ubuntu 24.04, a five-minute job,
manual-only events, a main-marek/repository guard, non-cancelling concurrency and
contents:read only. Unspecified token permissions are none in this declaration.
Upload retains bounded public evidence for seven days; no repository writer or
prior artifact download is introduced.

The helper validates positive decimal runtime repository/run/attempt IDs; requires
actual checkout HEAD, github.sha, github.workflow_sha and approved_revision to
match as full SHAs; and verifies the exact approved manifest hash before token
construction. The workflow supplies trusted context through environment values,
checks out github.sha with persist-credentials:false, and supplies github.token
only in the collection step. The parent removes that environment variable before
worker construction. Public result output excludes token and request authorization
headers. A complete transfer remains distinct from validated release content.

An approval input is still an operator assertion, not a cryptographic approval
service. Same-commit workflow/source checks deliberately refuse mixed revisions.
No runnable manifest or activated workflow exists yet, so no revision is approved
for dispatch. After the proposal is installed and enrollment is reviewed, record
the exact resulting pushed commit and manifest hash; do not reuse this package's
starting revision as approval. Server-side workflow isolation was not rechecked
because no dispatch is being proposed in this ticket.

## Verification and limits

48 offline tests pass on local Python 3.14.4/Linux: 17 collector, 20 transport,
three workflow-preflight and eight historical churn. New workflow tests cover
missing enrollment before transport/token creation, six synthetic numeric requests
and refusal of wrong repository/event/ref, malformed IDs, own ID, mismatched
checkout/source/workflow/approved revision and manifest hash. Synthetic enrollment
exists only in test memory. Existing transport tests use fake sockets and real local
processes/pipes, with parent production socket creation blocked. No outbound or
loopback HTTP and no actual credential was used.

YAML and embedded Python syntax checks pass; permissions/manual trigger/timeout/
concurrency/token-step assertions pass. No active workflow diff exists. Ubuntu
runner Python, the Python 3.10+ compatibility claim, real DNS/TLS/GitHub numeric
latest routes, server-side settings and artifact behavior remain unverified live.
No storage integration, release-content validation, publication or installer change
is included.

## Next authorized boundary

The next live action to request is **exactly one unauthenticated metadata GET**
for SQLite Browser, with the exact URL, caps, deadlines and stop rules already in
[the enrollment proposal](../design/transport-enrollment-review.md#separate-identity-enrollment-request-proposal--not-dispatched).
It does not require activating this workflow. Review and commit that response's
identity evidence, fill the manifest and repeat offline preflight. A push requires
Marek's approval under ~/AGENTS.md. The later six-release adapter baseline needs a
separate reviewed runnable manifest, exact pushed workflow/source revision,
server-side isolation verification and explicit dispatch authorization. There is
no 24-hour wait or day observation prerequisite.
