# Publish the bounded 128-source catalog cohort and four source recipes

Type: task
Status: resolved
Triage: ready-for-agent

Concrete publication package from 138/139: 131 app identities / 128 repositories,
including 77 additions and four reviewed source-recipe migrations. The installed
host stays untouched. Marek authorized the source push and publication on November 6; the operation
below is complete. See the Answer for actual receipts.

## Proposed operation

Push the prepared source, including the 128-source enrollment ceiling, oldest-
attempt-first batches of at most 52 release-list requests, and the three-hour
schedule. Existing 16 MiB response / 96 MiB run / 300-second cooperative acquisition /
2 MiB file / 1,024-file read / 128,000,000-byte Git history bounds stay unchanged.
No new credentials, copied browser data or Pages deployment.

Dispatch the existing catalog workflow sequentially, reading back each exact
published pin and its parent, until the whole cohort has successful observations
(normally three batches; stop and investigate rate/auth failures or unexplained
budget limits). Never assume the first run includes all newly enrolled apps.
Require every previous app identity to remain; verify all configured numeric
identities, current statuses and new-app publication coverage. Preserve per-release
observations on failures and unattempted sources. Record actual source/run/catalog
receipts and update the operating policy after success.

Four source recipes move from catalog-only to declared enrollment without any
app/source identity change: agent-smith, agent-switchboard, agent-teams-ai,
agent-toolkit. Agent Skills remains catalog-only because of its build-host icon
link. The compiled source policy adds only their data; no host module/recipe or
binary refresh, app execution, installation, ordinary update or yadm operation
is included in this proposed publication.

## Evidence

- [Inventory / explicit source proof](../research/catalog-expansion-inventory.json)
  and [77 verified identity proposals](../research/catalog-expansion-identities.json).
- [Fresh three-batch rehearsal](../research/catalog-expansion-preflight.json): all
  128 sources attempted, 131 app identities, no failures, all previous identities
  preserved. Actual batches took 169.33 / 192.07 / 181.41 seconds, with 47.19 /
  38.87 / 56.83 MB response bytes respectively. Final YAML 21,699,088 bytes;
  largest document 1,159,110 bytes. These are current-scope observations.
- [Offline whole-command replay](../research/catalog-expansion-workflow-replay.json)
  includes reading the retained 128-source snapshot, validation, exact-parent
  publication and reporting: 311.45 seconds, 175.35 MiB peak process RSS under a
  1 GiB address-space limit. It excludes network, checkout/fetch and CI overhead;
  it is not a measured fresh CI job or a universal 10-minute guarantee.
- [Existing browser parser](../research/catalog-expansion-parser.json) reads the
  map and all 128 documents in Node. No DOM/CORS/mobile acceptance is claimed.
- [Four source migrations / one exclusion](../research/simple-five-evidence.json)
  bind exact originals, full payload digests, static metadata and saved selectors.

146 collector regression tests and 44 reconstruction tests pass; the five final
focused batch tests cover partial-transfer budget accounting and failure isolation.
The separate final main-report workflow test passes. Python/workflow syntax and
diff checks pass. No remote write or host refresh is included until authorized.

## Answer

Pushed both prepared commits through `42abcbc8e` with Marek's authorization.
Three sequential successful manual runs publish the full 131-app / 128-source
cohort at `e9d713eb74ca02dca24a5269ace5ee9e28466f41`. All 128 enrolled sources
have successful observations across 156 attempts, with zero failures or pending
apps. Exact-parent pin readback, canonical distributed-reader validation, source
identity checks, previous app preservation, unchanged untouched documents and
retained-release/observation checks pass. Final YAML is 21,703,160 bytes; largest
file 1,159,110 bytes. [Report and portable receipt](../research/bounded-catalog-publication.md).

Operating policy now records the deployed source cap and three-hour bounded
schedule. No installed-host refresh, app installation, binary update, website
rebuild or yadm operation. New browser acceptance and a natural scheduled trigger
were not observed. Broad GitHub coverage remains incomplete under 138.
