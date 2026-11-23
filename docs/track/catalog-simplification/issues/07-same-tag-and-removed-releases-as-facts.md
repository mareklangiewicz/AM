# Record same-tag and removed releases as facts

Type: grilling
Label: wayfinder:grilling
Status: open
Blocked by: 01, 02

## Question

With the facts-only principle: how does the catalog record several release ids
under one tag (in one fetch, or across runs), an asset whose digest changed, and
a release no longer returned upstream, without invalidating, replacing or
reconciling? Which first/last-seen facts does a client need to warn or to treat
a rolling tag as expected, and how does retention bound the history kept? Revises
ADR 0002; takes over the same-tag part of catalog-system ticket 20.
