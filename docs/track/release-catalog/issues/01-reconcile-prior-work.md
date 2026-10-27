# Reconcile prior catalog research

Type: research
Status: resolved
Triage: ready-for-agent

## Question

What can we reuse from the earlier experiment, and what differs from the current proposal?

## Answer

Read docs/design/version-catalog.md at main-marek de298a009 and classify.awk, resolve.sh, and shadow.sh from proto/release-catalog d33ccb4c0. The prototype batches GraphQL reads, then selects matching assets in CI and publishes small resolved rows for a generic installer. The new proposal publishes observations and leaves selection to app scripts. Reuse the survey, batching measurements, pathological cases, and comparison techniques; do not silently adopt its selection or installer design.

The earlier notes report 825 GraphQL points across two architecture sweeps. The resolver query reads five releases and fifty assets with a selective deeper pass; it does not collect complete REST response fields or reproduce REST ordering. This is promising capacity evidence for that specific projection, not proof that the newer response catalog fits the same budget.

A separate local check in this chat used connector-returned JSON for three upstreams and pinned upstream AM recipes at 5e96002699597af8996b77137bb72ece995bec2b. All three filters selected the same URL across the original connector serialization, compact JSON, and indented JSON. Response sizes were about 0.45, 1.10, and 0.82 MB. Those fixtures and results were not yet a test of this fork's current recipes or workflow-token behavior. The experiment must be repeated more broadly before claiming compatibility.
