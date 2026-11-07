# Bound identity-verification redirect transport requests

Type: task
Status: resolved
Triage: ready-for-agent

Code inspection during 149 found that `catalog_sources.verify` increments its
`requests` counter around `_get` invocations, while `_get` uses the default
`urllib.request.urlopen` redirect handling. Explicit alias/canonical identity
review protects source identity, but automatic redirect hops can add transport
requests outside that counter. Therefore the current 200-per-invocation limit
bounds logical GET invocations, not a proven total of underlying HTTP requests.
This concerns discovery verification, not `host_catalog` collection, whose
NoRedirect opener already refuses redirects before following them.

Make every discovery transport attempt consume the explicit shared request budget,
including rename hops, and constrain redirect destinations before forwarding any
credentials. Preserve explicit public numeric alias/canonical identity agreement,
checkpointed proposals, source-hash checks and no-enrollment behavior. Add focused
cases for request exhaustion during redirects and refusing unexpected destinations.
Do not infer actual extra wire counts from old receipts or rewrite their hashes;
record a correction distinguishing logical requests from transport attempts.

149's 383 logical GET invocations verify its identities and eight checked renames;
the exact underlying request count was not instrumented. Its separate real
500-source collector preflight uses the unchanged redirect-refusing transport.

## Answer

Discovery now disables implicit redirects and explicitly follows at most three
metadata hops only when redirect review is enabled. Targets must be exact HTTPS
GitHub API repository metadata endpoints, with no alternate origin, credentials,
port, query, fragment or traversal segments. Each allowed hop consumes the same
200-attempt budget before another request is constructed. Release-probe redirects
refuse. Exhaustion/refusal checkpoints account for attempted requests without
proposing an incomplete identity; canonical public numeric-ID agreement remains.
New receipts mark `request_accounting: transport_attempts_v1`. Historical receipts
and their hashes remain unchanged; their logical GET counters are not wire counts.

All 14 focused discovery/enrollment/declaration regressions pass, including mocked
transport budgets of 1–4, unsafe targets before credential forwarding, default
and probe refusals, bounded redirect loops, auth/rate failures and numeric-ID
mismatch. [Validation receipt](../research/discovery-request-accounting-validation.json)
records code/log hashes and the absence of live API calls. No enrollment, collector
refresh limits, installed-host or publication changes. Source-only, not pushed.

## Authorized push

Marek authorized pushing the fix. Source `9a78fc860` is pushed to
`origin/main-marek`. This supersedes the local-only status above. No catalog
workflow dispatch, enrollment change or installed-host operation was needed.
