# How AM's updater reads release facts

Type: grilling
Label: wayfinder:grilling
Status: open
Blocked by: 18

## Question

With twins and recreated tags recorded as separate release IDs (ticket 07): how
does AM's installer and updater (`APP-MANAGER`, `modules/catalog-*.am`) decide
that an update exists, and where does a recipe declare a rolling tag such as
`nightly`? If the updater compares tags, a recreated `nightly` is never seen as
an update. Check the current comparison in code first, then decide what the
host records about an installed release (ID, tag, asset ID, `sha256pre`) and how
it warns or updates silently.
