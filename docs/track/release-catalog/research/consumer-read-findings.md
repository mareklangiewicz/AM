# Read-only consumer verification

2026-10-27, ticket 19. Implemented and pushed consumer source
`046d9ebd9846f71cd80f1fd4dd341a094b8e7110` under Marek's continuation/push authorization.
Verified actual CLI reads from the already published catalog; no upstream release
request, workflow dispatch, new publication, schedule or installer change occurred.

## Result

Both commands succeeded with exact stdout body bytes and empty stderr:

| Lookup | Pin behavior | Catalog GETs | Body bytes | Existing filter |
| --- | --- | ---: | ---: | --- |
| Obsidian latest alias | Resolve ref once, pinned index/body | 3 | 13,889 | jq .tag_name -> v1.14.5 |
| Neovim latest alias | Explicit same full commit; no resolution | 2 | 24,511 | jq .tag_name -> v0.12.6 |

These tag strings are values in the recorded catalog snapshot, not fresh upstream
version recommendations. CLI stdout was byte-for-byte identical to the independent
original bodies in ticket 18's retained publication artifact, including whitespace.
No normalization, field filtering, release ranking or asset selection happened in
the consumer; jq was applied afterward to demonstrate the intended pipe boundary.

Both reads used publication commit
`d612ff34b492b337fe51128f769ec9d262d0ee86`, collector source
`86354b78b0ec00331ce43dfdef354349890e7e49` and run 40533858562/attempt 1.
Index SHA256 matched independently retained publication evidence:
`ecfcb74f40ef064d6766ac54756ff6a246ef515c535399a02b64cfecb446671a`.
Both observations were about 1,551 seconds old at the recorded checks, fresh under
the inclusive 86,400-second contract, with stale_accepted=false. Original receipt
and validation timestamps remained unchanged by this read.

The CLI's isolated unauthenticated transport performed one public ref GET plus
two pinned raw reads for the default path, and two raw reads for the pinned path:
five catalog GETs total, no redirects, retries, credential lookup or direct source
fallback. No additional read was needed for comparison with saved evidence.

## Implementation and offline verification

[Consumer design](../design/catalog-consumer.md) records API/CLI, fixed catalog
trust scope, exact stale-consent tuple, process deadlines, bounds and remaining work.
Shared storage.validate_index separates complete metadata checking from body IO;
full-tree validation and local pinned lookup reuse that same validation/policy.
The byte-tree format is unchanged and the existing catalog needed no republishing.

80 offline tests pass: 72 collector/storage/delivery/consumer tests and eight
historical churn checks. New checks cover selective one-resolution reads, explicit
pins, branch movement without mixed generations, missing files without fallback,
freshness equality and one-microsecond expiry, wrong consent commit/request/hash,
post-IO expiry and clock regression, future/unmeasured/unavailable/unknown/removed
alias cases, metadata/integrity mutations and CLI no-partial-stdout refusal.
Fake local child processes verify strict HTTP/header/body bounds, compression/
redirect/truncation refusal, isolated environment and killing/reaping hung or
trickling stdout. They do not connect outbound or use a loopback HTTP server.
Local tests and this consumer smoke used Python 3.14.4/Linux; broader
platform/Python/curl compatibility remains unmeasured.

## Persistent evidence and limits

[Evidence archive](consumer-read-20261027-evidence.tar.gz), 5,485 bytes,
SHA256 `7577e3c4014941dfa8488bdca2ec84fd1be80be5d4cbb8843c184da41586f841`, retains the two exact stdout bodies, metadata JSON,
empty stderr files and check report. [Machine checks](consumer-read-checks.json)
separate consumer/source/publication provenance, selected body/index hashes, ages,
request counts and the independent prior publication archive comparison.

There is no automatic stale approval. The CLI refuses old data before fetching a
body unless supplied the exact COMMIT REQUEST_ID BODY_SHA256 tuple; other
availability/future/integrity failures remain non-overridable. It rechecks freshness
after IO and emits bytes only after all validation. Public read success is a bounded
transport/integrity sample, not a full adversarial audit or binary authenticity proof.

No installed script consumes this module yet. The next useful integration is an
explicit opt-in read path for one app using the existing app-specific filter, tested
against this catalog snapshot without running an installer. Broader batching/cache,
portable dependency strategy, stale-consent UX, schedules and fleet migration remain
separate decisions. Existing AM updates still use their current behavior.
