# Compare every deployed browser file, not only the definitions

Type: task
Label: implementation:task
Status: open
Triage: ready-for-agent
Blocked by: none

## Outcome

`release.py plan` and `ship` report "deployed browser … differ from HEAD;
redeploy when ready" whenever any file the catalog page serves from the contract
or the page itself differs between the deployed site and HEAD. That includes
`tools/catalog-contract/reader.mjs` and `web/catalog/*`, not only
`tools/catalog-contract/definitions.mjs` (`DEPLOYED_DEFINITIONS`). A test shows a
changed reader with unchanged definitions producing the redeploy line.

## Why

November 24, 2026, catalog-simplification ticket 18: `reader.mjs` stopped
refusing repeated tags, but the generated definitions were byte-identical, so
the plan printed "deployed browser definitions match HEAD" while the live page
still ran the old reader. Without a manual redeploy, the page would have failed
to read every repository with twin releases once they were collected. The
redeploy was dispatched by hand with Marek's OK (catalog-pages run 45439666753).
