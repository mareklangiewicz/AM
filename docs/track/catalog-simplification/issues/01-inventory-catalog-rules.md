# Inventory the catalog's rules

Type: research
Label: wayfinder:research
Status: open
Blocked by: none

## Question

For each rule a user can meet (selection order, run limits, retention of 32 plus
newest stable, same-tag replacement and invalidation, the four kinds of time,
partial history and reconciliation, status reporting, recipe classification
labels, platform guesses) and each format-3/status-1 encoding (`download_base`/
`url_suffix`, media type aliases and `=` escapes, omitted defaults, `state`/
`value` wrappers, reason codes, commit pins): where it is implemented, which
ADR or ticket accepted it, what the webpage says about it today
(`web/catalog/app.mjs`), and what reads or depends on it (hosts' modules, the
browser, tests). One table row per rule, with file:line references.
