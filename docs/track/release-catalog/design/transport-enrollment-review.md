# Transport and identity-enrollment review package

2026-10-27. Ticket 13. This is a reviewable preparation package, not an installed
adapter, enrolled manifest, workflow change or authorization to make API requests.
The collector core at main-marek 19269778f is the starting implementation.

## Saved identity evidence

[Machine audit](../research/saved-identity-audit.json) records member/archive hashes
and the exact saved observations, without new GitHub API requests.

| Reviewed source | Historical repository ID | Evidence | Remaining limitation |
| --- | ---: | --- | --- |
| obsidianmd/obsidian-releases | 262342594 | Baseline and hour list-response Link headers | Historical name mapping, not a fresh repository metadata check |
| neovim/neovim | 16408992 | Baseline and hour list-response Link headers | Same limitation |
| WezTerm target; old alias wez/wezterm | 120568143 | Saved 301 Location plus two complete numeric-ID requests | Does not establish its current owner/name |
| sqlitebrowser/sqlitebrowser | unknown | Saved responses contain no repository-ID enrollment evidence | Needs one separately authorized metadata read |
| Workflow repository AM | supplied at runtime | Future trusted github.repository_id context | No artifact/manifest assertion may replace runtime context |

Latest/list requests for the same exact owner/name share the reviewed historical
mapping; release/asset/user IDs, opaque node IDs and avatar paths are not substituted
for repository identity. The incomplete baseline is not used to establish a complete
sample. This audit does not assert that any name still resolves to the same repository.

## Identity gap and proposed resolution

A static reviewed ID next to an owner/name fetch URL cannot guarantee that URL will
continue to reach that ID. Names can change or be reassigned. In particular, a stale
mapping could defeat own-repository exclusion if a named fetch resolves to the
workflow repository while the manifest still records some other ID.

For the eventual adapter, propose **numeric-ID fetch descriptors only**, with
consumer name URLs retained solely as explicit reviewed aliases. The live adapter
must reject owner/name fetch descriptors before credentials are supplied. This is
a stricter operational profile than the offline core, which supports both forms.
No promise is made that derived numeric latest routes work until tested explicitly.
The existing numeric WezTerm list route has direct saved successful evidence; the
other exact numeric descriptor URLs below are candidates, not observed successes.

Migrating a fetch URL creates a new request ID and drops prior validators, even
if its alias and repository ID are unchanged. Do not rewrite historical descriptor
provenance or silently reuse the old baseline. WezTerm's unchanged descriptor can
retain compatible state only after normal prior validation. Future enrollment must
review immutable source identity deliberately rather than follow arbitrary renames.

## Separate identity-enrollment request proposal — not dispatched

Exactly one unauthenticated GET, no redirects, retries or follow-ups:

`https://api.github.com/repos/sqlitebrowser/sqlitebrowser`

Pinned API version 2022-11-28; Accept application/vnd.github+json. Connect deadline
10 seconds, entire request 30 seconds, body <=64,000 bytes, headers <=64,000 bytes,
retained header values <=8,192 bytes. Record local start/completion, status, selected
public headers, exact bounded body/hash and canonical name/ID evidence. Require
200, positive integer id, expected full_name case-insensitively, private=false and
visibility=public before proposing the mapping. A redirect, mismatch, auth/quota
failure or invalid response stops with no additional request. Do not enroll from
a guessed ID or automatically accept a renamed target.

The workflow repository ID comes from trusted workflow context later. This proposal
therefore needs one public metadata request, not five metadata reads or another
quota probe. Enrollment evidence must be reviewed and committed before collection;
failed enrollment does not trigger retries or a collection run.

## Future six-release validation proposal — separate authorization

After enrollment and offline adapter checks, propose one manual baseline with these
six exact targets, serially, at most six GET attempts and no redirects/retries:

| Source | Proposed fetch path |
| --- | --- |
| Obsidian list | /repositories/262342594/releases |
| Obsidian latest | /repositories/262342594/releases/latest |
| Neovim list | /repositories/16408992/releases |
| Neovim latest | /repositories/16408992/releases/latest |
| WezTerm list | /repositories/120568143/releases?per_page=100 |
| SQLite Browser list | /repositories/REVIEWED_SQLITE_ID/releases?per_page=100 |

The final row is deliberately non-runnable until an ID is enrolled. No extra request
is allowed to discover routes, resolve redirects or fetch pagination. A 404 on a
candidate numeric route is a recorded refusal requiring review, not a fallback to
an owner/name URL. Use the accepted request/response/byte/quota/error limits from
restricted-collector-v1.md. Record the new exact source commit and manifest hash
when ready; the future implementation SHA is not known yet and cannot be approved
by this draft. No initial conditional validators for changed descriptors.

This one run would establish candidate-route behavior and real adapter completion
records for the bounded sample; it would not establish fleet capacity or retention.
Enrolling the one missing ID does not authorize this six-release run automatically.

## Real transport proposal: one supervised worker per request

Use Python's standard-library HTTP client in a child process supervised by the
parent collector adapter. The parent enforces absolute monotonic deadlines with
bounded pipe reads and kills/reaps the worker on deadline, overflow or cancellation.
A worker process makes blocking DNS/TLS/body IO interruptible from the parent;
event-boundary checks alone or a thread with a socket inactivity timeout do not.
No new package, installed app or existing updater is required by this proposal.

Worker sequence:

1. Receive one validated numeric-ID request and opaque credential over a private
   pipe, not argv, a saved file or a child environment variable. The parent clears
   the token variable after constructing the credential. Other environment values
   and inherited file descriptors are allowlisted; stderr is discarded and no
   HTTP debug logging, trace or request dumps are enabled.
2. Explicit HTTPSConnection.connect to api.github.com:443 with certificate and host
   verification. Emit Connected only after DNS/TCP/TLS completes. The parent kills
   a worker that has not reached that event by the connect deadline.
3. Send exactly one GET with the approved Accept/API-version, User-Agent,
   Accept-Encoding: identity and optional validated conditional headers. Build the
   reported actual-condition tuple from the same header values actually sent;
   do not reconstruct it from the plan after an exception. Never follow a 3xx,
   call set_tunnel or discover proxy/netrc/config/gh credentials.
4. Bound status/header input before parsing/allocating it. A limited socket-file
   reader caps total header wire bytes at 64,000 (including status/interim blocks),
   each retained public value at 8,192 and each bounded read at a small fixed chunk.
   Only after final headers complete does that reader switch to body accounting.
   A check on response.getheaders alone is too late to establish allocation bounds.
5. Stream entity bytes through fixed <=8,192-byte buffers, permitting one overflow
   sentinel beyond the body cap solely to reject. Preserve entity JSON bytes while
   normal HTTP transfer framing is decoded; do not gzip-decompress/reformat JSON.
   Reject unexpected content encoding. Validate framing/Content-Length/chunked
   completion before End. A partial/invalid response cannot claim completion.
6. Emit only typed bounded event frames, then close/reap. Keep cumulative frame
   lengths bounded before JSON/base64 decoding; chunk data uses bounded binary
   frames so a huge announced length cannot trigger an allocation. An unrecognized
   frame, malformed sequence or unexpected worker exit becomes a fixed refusal.
   No arbitrary exception message crosses the IPC boundary.

The parent recomputes time remaining from the original supplied monotonic deadlines
on every select/read/wait; partial pipe traffic and worker chunks never reset them.
It tracks the earlier of request and batch deadlines and caps connect separately.
Closing the event iterator must cancel and reap the process even on early return.
A bounded cleanup grace interval is diagnostic overhead, never extra network time:
kill at the deadline, close the socket via process termination, reap promptly.

Connected is a genuine connection event, not first-response-header time. A curl
subprocess design was considered but deferred because completion-only timing output
does not supply the core's timely Connected event; verbose traces would introduce
unnecessary credential exposure. Local curl 8.18.0 was inspected only with help and
version commands, not used to make collection requests. Python's HTTP parser still
requires the bounded-reader work and tests above; its standard limits alone do not
prove this stricter aggregate header cap. This is a design, not tested adapter code.

## Workflow adapter review

Do not alter .github/workflows/catalog-quota-probe.yml in this ticket. It remains
the historical manual quota/churn experiment, with contents:read/actions:read and
previous-artifact retrieval for repeat runs. Its 10-minute timeout, generic GH_TOKEN
entry points and older churn body/time behavior do not meet the new adapter contract.

A future collector-only job proposal must have workflow_dispatch only, an explicit
manual-event/repository guard, five-minute timeout, concurrency without cancellation,
and permissions contents:read only (all unspecified permissions none). Artifact
upload must not smuggle a publication writer into this stage. Do not retrieve old
Actions artifacts or add actions:read merely because the old probe does so.

Inputs from trusted context, passed as typed environment values rather than shell
interpolation: github.repository_id, github.repository, github.sha,
github.workflow_sha, github.run_id and github.run_attempt. Parse the ID strictly as
positive decimal; verify the reviewed workflow repository and approved code revision.
Use github.token only for the collection step; no PAT/App secret or generic GH_TOKEN
fallback. Checkout has persist-credentials:false and executes the approved source
revision, not code from response artifacts. Pin third-party Actions to reviewed
commit SHAs; do not silently replace existing pins based on this review.

Before proposing a dispatch, record the exact pushed code/manifest/workflow SHA and
inputs. Because code is not yet implemented, there is no currently dispatchable
approved revision. No push trigger, schedule, remote publication branch or installed
app changes are part of this proposal. Response artifacts contain bounded public
results only and explicitly distinguish incomplete transfers from usable observations.

## Smallest offline adapter checks

Use pipes/fake sockets only, without outbound API or loopback HTTP:

- Worker hangs during simulated DNS/TLS/body/pipe output; parent kills and reaps at
  short injected deadlines, including a stream that trickles often enough to defeat
  inactivity-only timeouts. Cancellation leaves no worker or open credential pipe.
- Connected arrives only after simulated handshake. A slow server header after a
  quick handshake consumes request time, not connect time.
- Header/framing/length/chunked/trailer bounds apply before allocation; oversized
  frame announcements, duplicate sensitive/public headers, malformed lengths,
  compressed bodies and unexpected worker exits refuse without End.
- Exact entity bytes and actual sent condition match the input/output contract;
  truncated 200 and invalid/unconditional 304 never become candidates.
- Poison ambient proxy/config/gh/token variables and fake debug/exception paths;
  assert they cannot affect destination, credential selection or emitted output.
- Named descriptors, own numeric ID, missing identity and unapproved revision stop
  before worker creation. Verify six-attempt cap and that no endpoint fallback exists.
- Run the existing 17 collector and eight churn tests unchanged; do not claim fake
  socket tests establish real GitHub TLS/visibility/quota behavior.

After these pass, review the concrete code and identity-enrollment result before
requesting the separately bounded baseline above. Storage integration, public
hosting, scheduled collection and client migration remain separate work.

## Primary documentation consulted

- [Python HTTP client](https://docs.python.org/3/library/http.client.html): explicit
  connection and bounded body APIs; timeout APIs do not establish the parent kill
  design by themselves. The documentation currently includes newer 3.15 features;
  do not rely on those in the Python 3.10+ implementation.
- [GitHub context fields](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts):
  repository_id, sha and workflow_sha are distinct provenance inputs.
- [curl manual](https://curl.se/docs/manpage.html): connect/overall timeout options
  and configuration isolation were considered; no claim that a CLI timing summary
  provides an event stream follows from them.

The worker, IPC, stricter numeric profile and staged authorization plan above are
engineering proposals, not promises made by these documentation sources.
