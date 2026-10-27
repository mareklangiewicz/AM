# Restricted-token collector core (offline implementation)

Ticket 12; design: `docs/track/release-catalog/design/restricted-collector-v1.md`.
This module has no network transport, workflow adapter, live CLI or environment
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
