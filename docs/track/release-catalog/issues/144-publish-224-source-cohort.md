# Publish the prepared 228-app / 224-source catalog cohort

Type: task
Status: resolved
Triage: ready-for-agent
Blocked by: 142, 143

Prepared source adds 97 catalog-only app identities, reaching 228 apps / 224
repositories, plus snapshot-processing and explicit rename-verification changes.
Source push and catalog publication are complete under Marek's authorization below.

## Proposed operation

Push the prepared commits, then dispatch the existing catalog workflow sequentially
until every enrolled source has a successful observation under the new source
revision (normally five batches). Fetch the latest published parent for each run;
the rehearsal parent is historical evidence, not a remote force-push target.
Read back each exact published pin and parent, preserving all prior app identities,
configured numeric source identities, retained releases and untouched observations.
Stop and investigate rate/auth failures or unexplained budget limits. Record the
source/run/catalog receipts and update operating policy after success.

The enrollment ceiling becomes 224. Per-run scope remains 52 requests; one page
of 100 releases/source; schedule remains every three hours. Response, transfer,
elapsed, document, file-count and Git-history bounds are unchanged. Nominal
rotation is five runs / 15 hours; this is not a guarantee of successful freshness.
The client still judges individual selected observations against 48 hours.

No recipe migration, client selection/policy change, installed module/recipe
refresh, app installation, binary update, website rebuild or yadm pointer change
is included. The 97 new app identities are catalog-only; existing declarations
and the installed 21-app host remain unchanged.

## Evidence

See the [cohort report](../research/next-224-catalog-expansion.md), its linked
metadata/preflight/whole-command/parser receipts and
[snapshot-processing report](../research/snapshot-processing.md). Actual GitHub
Actions operation at this scope is now recorded in the Answer; natural scheduled
operation and browser DOM/CORS/mobile acceptance remain unobserved.

## Comments

Marek authorized “Yes, push and publish” on November 7 local time. Source
`fde55f598` is pushed; five sequential exact-parent batches and readback are in
progress. The separate batch-size/quota assessment is tracked in 145.

## Answer

All five authorized runs succeed, with 260 successful attempts / 224 distinct
sources and zero failures. Final catalog
`26d82aa94bb5a8f70449e42500dc78a597583ab3` contains 228 apps / 224 sources.
Each exact pin and parent passes bounded reader/canonical/reference validation;
prior identities, retained releases and effective observations are preserved.
Final YAML is 33,152,148 bytes, largest document 1,159,110 bytes.
[Publication report and portable receipt](../research/next-224-publication.md)
record source/run/pin/timing/log and preservation evidence. Operating policy is
updated; installed host, recipes, apps, website and yadm pointers are unchanged.
The 500/hour proposal is separate; deployed cadence stays 52 / three hours.
