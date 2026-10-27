# Restricted-token collector core (offline implementation)

Ticket 12; design: `docs/track/release-catalog/design/restricted-collector-v1.md`.
The collector.py core has no network transport, workflow adapter, live CLI or environment
credential lookup. The historical quota/churn probe and workflow remain separate.

From the repository root (Python 3.10+):

```sh
python3 -B tools/catalog-collector/replay.py
python3 -B -m unittest discover -s tools/catalog-collector -p 'test_*.py' -v
```

Replay emits JSON to stdout using synthetic identities, credentials, response bytes
and clocks. No real source enrollment or public-visibility evidence is claimed.
There are no packages to install. `collector.py` has no runnable entry point.

## Interfaces

`plan(tuple_of_sources, workflow_repository_id, previous_state)` returns an
immutable Plan. Sources contain exact descriptors, reviewed immutable repository
IDs, identity evidence pointers and additional aliases (the descriptor URL is
already an alias). Previous state is an ID-to-Prior mapping. Body integrity and
conditional validators are checked before reuse. Unavailable/retired/unknown
priors supply no conditional request. The planner does not enroll or look up IDs.

`collect(plan, transport, clock, credential, workflow_identity=trusted_current_id)`
revalidates the plan against a separately supplied current identity before any
transport call. The extra keyword is intentional: an identity embedded only in
an incoming plan cannot establish the current workflow identity. A future trusted
adapter must supply it from workflow context and establish the built-in token's
provenance. An opaque object is not evidence of token scope by itself.

The credential is opaque to the core; no default, environment variable fallback,
repr/str conversion, command line or saved request Authorization header exists.
The transport receives it explicitly. Transport exception text is never emitted,
including an exception of the core's own Refusal type. A future trusted adapter
must keep credentials out of response events; the core cannot prove the provenance
or behavior of arbitrary injected Python code.

`transport.execute(request, credential, limits)` yields Connected, Headers, Chunk,
then End. Headers also reports the actual conditional values sent; they must
match the planned conditions before the result is accepted. HTTP 200/304 or failure statuses are inert transport results. Partial
responses, timeouts and bound violations have no response completion time or
candidate body. Status/selected headers and attempt finish time may still survive.
The core never updates prior state or writes files. Storage remains responsible
for release content validation, availability and candidate publication validation.
Do not interpret `outcome=response` or run `complete` as successful observation:
these mean complete HTTP transfer(s), possibly including HTTP errors/redirects.

The clock supplies aware UTC `utcnow()` and numeric `monotonic()` methods. Request
start, response completion and attempt finish are measured at separate boundaries.
Monotonic deadlines are absolute and passed to transport: connect 10 seconds,
request 30 seconds including all body reads, batch 300 seconds. Equality reaches
the deadline. Each event is checked against those deadlines; chunks cannot reset
request elapsed time. **The adapter must also interrupt blocking I/O itself.**
This core cannot preempt arbitrary injected Python code or a blocked iterator.
The fake event transport verifies event-boundary semantics, not socket behavior.

Header size accounting includes discarded headers; retained public headers have
individual bounds and duplicate public names refuse. Byte bounds apply to bodies;
a future adapter must also bound allocations before yielding events. No automatic
redirect, retry, pagination, quota check, identity fetch or auth fallback occurs.
Quota reserve/missing-header checks also apply when headers arrived but the body
failed. Two consecutive transport/5xx failures stop; other complete statuses reset
the streak. Missing quota evidence after a received response stops the remaining
plan. Not-attempted request IDs and total received bytes are explicit in reports.

Index/tree/history caps belong to storage/publication and are not falsely rechecked
here on nonexistent publication trees. A future adapter and real reviewed identity
manifest require separate review; nothing here dispatches a live experiment.

## Supervised adapter (ticket 14)

`supervised_transport.py` targets POSIX/Linux pipes and implements the reviewed numeric-ID-only operational
profile. It is an importable API, with no public live command or workflow wiring.
The older `replay.py` remains synthetic and does not invoke the real connector.

Construct `SupervisedTransport` with the validated plan, trusted workflow ID and
matching approved/current full source revision. Pass an explicitly constructed
opaque `Token` to `collect`. These supplied values still require a trusted future
workflow adapter; matching strings and a Token object alone cannot establish their
provenance. This transport is scoped to one run: each planned request may start
once, at most six workers total. Aliases never become fetch targets and a changed
numeric URL still changes request ID and invalidates old state.

A fresh isolated Python worker gets one bounded bootstrap over private stdin.
Its argv/environment never contain the token; only LANG is inherited, Python uses
-I/-S, unneeded descriptors close, stderr is discarded and no debug/request trace
is enabled. No proxy/netrc/gh/config identity discovery or default credential path
exists. The child explicitly connects DNS/TCP/TLS, emits Connected after handshake,
then sends one direct HTTPS GET with identity content encoding and actual approved
conditional headers. System CA verification and api.github.com hostname checks stay
enabled. No redirect/retry path exists.

The parent uses nonblocking bounded IPC and select with absolute connect/request/
batch deadlines, kills/reaps on timeout or cancellation, and requires clean worker
exit before exposing End. Cleanup has a one-second reap bound after kill; it does
not extend allowed network time. A blocking DNS/socket worker and a trickling pipe
cannot indefinitely stall the parent. OS process scheduling/reaping remains an
operating-system assumption, not a hard real-time promise.

Before HTTP header parsing, the limited socket reader bounds total wire headers
at 64,000 bytes and individual lines at 8,192. Retained public values keep the core
bounds. Body chunks are <=8,192; body cap is 8,000,000 with one possible consumed
rejection sentinel. IPC lengths are rejected before payload allocation. Core
received-byte metrics count forwarded body events, not that private overflow
sentinel or HTTP framing bytes. HTTPResponse handles transfer decoding; JSON bytes
remain exact. Duplicate Content-Length, TE+CL ambiguity, compression, malformed
chunk delimiters, chunk extensions and nonempty trailers refuse. This strict
profile can refuse otherwise legal HTTP responses; record and review such a refusal
rather than broadening it implicitly. Cumulative chunk framing has its own 64,000
byte cap, in addition to the initial header budget.

Tests add real local subprocess/pipe timeout, trickle, cancellation and cleanup
checks, plus fake socket parsing and core integration. They never connect outbound
or to a loopback HTTP server; any production socket creation in the parent tests is
blocked, and the internal bootstrap test supplies an invalid config before connect.
No real token is used. Parser compatibility has been exercised on the recorded local
Python version, not every Python 3.10+ release. Real TLS/DNS, GitHub route behavior,
workflow context provenance and the missing SQLite ID still need separate review.

## Inactive run package (ticket 15)

The staged manifest in docs/track/release-catalog/design/staged-manifest.json now
contains reviewed SQLite Browser identity 19416551. workflow_adapter.py still
refuses any missing identity before transport/token creation. This helper has no CLI or ambient token
lookup. The exact candidate workflow is catalog-collector.yml.proposed beside the
manifest, outside .github/workflows. See the tracked adapter-review-and-run-package.md
research report for review, approval boundaries and 48 offline checks. Malformed or
folded HTTP header lines now refuse before Python's permissive header parser.

Ticket 16 installs the separately approved workflow as
.github/workflows/catalog-collector.yml. Each live dispatch still requires explicit
authorization. The .proposed file remains the historical review artifact.

## Observation storage integration (ticket 17)

storage.py applies inert measured results to a bounded, validated byte tree. The
manual workflow now exports candidate/index.json and candidate/bodies/ with
storage-report.json beside the original response evidence. See
docs/track/release-catalog/design/storage-collector-integration.md for format and
transitions. artifact_io.py reads closed candidate directories; publication.py
provides local-only atomic Git commits and pinned freshness-checked reads. Neither
has a network/remote publication path. No installer calls these helpers.

## Persistent delivery (ticket 18)

The manual workflow now accepts previous_publication: an exact release-catalog
commit, empty only for branch creation. It loads validated available observations
into conditional planning and applies storage against that prior. A separate
publisher job validates the same-run artifact and recomputes it before a normal
fast-forward push to release-catalog. See docs/track/release-catalog/design/catalog-delivery.md
for permissions, bounded ZIP/Git handling, conflict behavior and limits. No schedule
or installed-app integration is enabled.
