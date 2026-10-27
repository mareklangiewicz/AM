# Choose the next collection prototype from evidence

Type: grilling
Status: open
Triage: needs-info
Blocked by: 02, 03

## Question

Should the next prototype use exact REST responses, neutral structured GraphQL observations, or a bounded combination?

## Acceptance

Compare measured cost, coverage, ordering and selection compatibility, fields, asset pagination, payload size, volatile-field churn, and projected Git growth. GraphQL observations can remain policy-free, but transforming them into REST-looking responses may lose semantics. Present trade-offs and discuss with Marek before changing the design. Keep the collector free of release ranking and app-specific selection unless that decision is explicitly reopened.

## Available evidence

2026-10-27: prerequisites 02 and 03 resolved. Read the inventory and first workflow probe reports in ../research/. The daily REST request count may fit even the conservative 1,000/hour planning baseline; the actual probe reported 5,000 for that run. Representation/churn and compatibility, rather than the hourly sweep count alone, should drive the next comparison. The 26,054-byte GraphQL projection is not equivalent to the 450,991-byte REST release-list response.
