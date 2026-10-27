# Choose the next collection prototype from evidence

Type: grilling
Status: open
Triage: needs-info
Blocked by: 02, 03

## Question

Should the next prototype use exact REST responses, neutral structured GraphQL observations, or a bounded combination?

## Acceptance

Compare measured cost, coverage, ordering and selection compatibility, fields, asset pagination, payload size, volatile-field churn, and projected Git growth. GraphQL observations can remain policy-free, but transforming them into REST-looking responses may lose semantics. Present trade-offs and discuss with Marek before changing the design. Keep the collector free of release ranking and app-specific selection unless that decision is explicitly reopened.
