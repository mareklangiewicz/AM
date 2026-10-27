# Supervised transport implementation — offline findings

2026-10-27. [Ticket 14](../issues/14-offline-supervised-transport.md).
Implementation: tools/catalog-collector/supervised_transport.py.
[Recorded checks](supervised-adapter-checks.json).

## Result

The adapter behind the existing collector interface is implemented, without a public
live CLI, workflow change, source enrollment, real credential or API request. Its
public construction checks a validated plan, trusted current repository ID and
matching full source/approved revision before any worker can start. Fetch URLs must
use the reviewed numeric repository ID; owner/name URLs remain consumer aliases.
No old validator can cross the core's exact-descriptor check.

All 44 offline tests pass on Python 3.14.4: 19 supervised-adapter tests, 17 collector
core tests and eight historical churn tests. The tests use fake sockets and actual
local worker processes/pipes, never outbound or loopback HTTP. Production socket
creation is blocked in the parent test process; the internal child bootstrap check
supplies invalid configuration, which refuses before any connection attempt.

## Verified behavior

- One request per approved descriptor, at most six workers per transport session;
  expired/forged deadlines and unapproved revisions refuse before worker creation.
  Core own-repository/missing-ID checks are revalidated. Named fetches are refused
  by the stricter adapter profile.
- Each worker starts isolated Python with minimal environment and closed unrelated
  file descriptors. Credentials travel over private stdin, not argv/environment,
  configuration dumps or saved headers. Stderr is discarded. Poisoned ambient
  token/proxy/HOME inputs do not change the spawn configuration. Secret-bearing
  spawn exceptions are replaced with fixed diagnostics and suppressed chains.
- Explicit DNS/TCP/TLS connection precedes Connected; sending headers happens after
  that event. Slow response headers consume request time without falsely extending
  or reapplying connection time. Request and batch deadlines remain absolute.
- Parent nonblocking IPC checks remaining monotonic time for every read/write/wait.
  Blocked fake workers and trickle output cannot reset deadlines. Timeout, early
  iterator cancellation and End-without-exit kill/reap the worker and close pipes.
  Parent exposes End only after clean exit; extra output after End refuses.
- Frame lengths and kind-specific limits are checked before payload allocation.
  Bootstrap is capped at 65,536 bytes; frames at 100,000 bytes, body chunks at 8,192.
  Duplicate JSON keys, invalid ordering, short frames and oversized announcements
  refuse with fixed diagnostics, not payload/exception echo.
- A limited socket reader applies the 64,000-byte header budget before standard
  HTTP/email parsing and caps each line at 8,192. Header/trailer input cannot first
  allocate an unbounded value and only then be rejected. The HTTPResponse cleanup
  path requires flush as well as read/readline/close; the wrapper supplies it and
  connection cleanup remains in a finally block.
- Fixed-size body reads preserve exact entity bytes while HTTPResponse decodes
  transfer framing. Content-Length mismatch, duplicate Content-Length, TE+CL,
  compression, malformed chunk CRLF, chunk extensions and nonempty trailers refuse.
  Chunk framing has a separate cumulative 64,000-byte bound. One private overflow
  sentinel may be consumed to reject an undeclared oversized body, never forwarded
  as an accepted body event. Core byte metrics count forwarded events, not that
  sentinel or HTTP framing bytes.
- Conditional evidence is built from the actual worker request headers sent, not
  synthesized after a failure. Parent and collector require exact agreement with
  the plan before treating a 304 as complete. Fake socket and process integration
  exercise both matching and missing evidence, with no fallback or retry.

## Design refinements and limits

The adapter uses a direct standard-library TLS socket plus HTTPResponse instead of
HTTPConnection to put the bounded reader in front of all header parsing without
global monkey-patching or replacing the HTTP parser. This retains explicit handshake
signalling and the parent kill boundary. It uses no Python 3.15-only parser options.

The HTTP profile is intentionally strict: legal responses using compression, chunk
extensions/trailers, many small chunks or long header lines may refuse. Such a refusal
needs review; it does not authorize automatic fallback or looser parsing. Python
compatibility has been exercised only on the recorded 3.14.4 runtime, not a full
3.10+ matrix. Parent IPC targets POSIX/Linux, matching the proposed Ubuntu job.

Parent supervision relies on OS scheduling/process termination; this is not a hard
real-time guarantee. Cleanup allows up to one second to reap after kill, without
extending network time. Actual DNS/TLS interruption, trust-store behavior, GitHub
numeric-route responses and visibility transitions have not been measured live.

Source revision, workflow identity and Token provenance are caller-supplied assertions
until a concrete trusted workflow adapter exists. No comparison of strings alone
proves which Git checkout executed. The default worker receives no broad ambient
credentials, but the future collection step must establish the built-in token's
provenance and clear its temporary environment binding. No complete real identity
manifest or source-enrollment entry point has been added.

The collector still produces inert results, not a publication tree or installed
app choice. Storage integration, availability validation, production index schema,
remote delivery, schedules and client migration remain separate work. The existing
active catalog-quota-probe workflow and historical churn code are unchanged.

## Reproduction and next boundary

From the AM repository root:

```sh
python3 -B -m unittest discover -s tools/catalog-collector -p 'test_*.py' -v
python3 -B -m unittest discover -s tools/catalog-probe -p 'test_churn.py' -v
```

The synthetic replay entry point remains unchanged and never invokes this connector.
The module intentionally has no __main__ collection command. Its private child
bootstrap is a bounded implementation detail, not a workflow integration.

[15](../issues/15-review-adapter-and-stage-manifest.md) reviews the actual implemented
boundary and stages an incomplete numeric manifest before any separately authorized
identity read or six-release validation. Resolving this ticket authorizes neither.
