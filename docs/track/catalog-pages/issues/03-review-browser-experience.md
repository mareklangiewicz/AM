# Choose the catalog browsing experience

Type: prototype
Label: wayfinder:prototype
Status: open
Blocked by: 01, 02, 05

## Question

Which directory, app-detail, release-history and download-selection experience best serves the accepted audience and style? After research, prepare a cheap prototype for Marek to react to, including freshness, partial history, snapshot provenance and missing metadata. Resolve only through live human feedback.

Include an explicit product/channel grouping decision for shared stable/nightly
repositories, and distinguish inferred platform matches from AM-supported choices.

## Accepted starting architecture and prototype gates

Follow the resolved Pages-home decision: website code on main-marek, direct
browser reads of unchanged YAML from one resolved release-catalog commit.
The prior research's generated-index recommendation is superseded.
Prototype real cross-origin fetches and ref-to-pin resolution, lazy per-repository
loading, a YAML parser that preserves large decimal IDs exactly, and worst-source
parse/render responsiveness. Record dependency size, actual transfer/loading
behavior and failures. Never silently mix commits or convert IDs through unsafe
JavaScript numbers. No copied dataset or generated index is the default route;
bring measured blockers back to Marek if this approach is inadequate.
Human review must cover search limitations before all repositories are loaded,
shareable links, snapshot provenance and stale/missing/network-failure states.
