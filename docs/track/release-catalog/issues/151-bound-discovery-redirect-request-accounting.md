# Bound identity-verification redirect transport requests

Type: task
Status: open
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
