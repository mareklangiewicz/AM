# Choose the catalog browsing experience

Type: prototype
Label: wayfinder:prototype
Status: claimed
Assignee: codex
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

## Prototype ready for human review — November 6, 2026

Context: local branch `prototype/catalog-pages`, commit
`7fa2ead2e`, worktree `/tmp/am-catalog-pages-prototype`.
Entry point `docs/track/catalog-pages/prototype/index.html`; run command,
measurements and limitations are in the adjacent README.md. Branch remains
unmerged and unpushed. Local preview: http://localhost:8765/ .

Three structurally different variants: A directory, B split-pane explorer,
C release desk. They use one exact catalog pin, lazy raw YAML reads, memory-only
cache and a dependency-free mapping-subset parser preserving integer text.
Expandable release assets page 60 at a time. UI exposes per-release observation,
partial history, source YAML and exact snapshot; platform matches are labelled
inferences, not AM-supported selections. Shared-repository AM identities remain
separate pending human verdict. No enrichment or generated index.

Live ref API/raw responses return HTTP 200 with wildcard CORS headers; the pin
observed was 03f63def325715a2621b5662b797ff967c8e439c. Node parsing measured
2.07 ms for the 1,474-byte map and 55.33 ms for 1,142,139-byte rclone data
(100 releases / 4,258 assets). Maximum 64-bit integer round-trips as decimal text.
JavaScript syntax checks pass. No browser was available: actual browser CORS,
visual/mobile/accessibility and DOM performance remain unverified. These are
not acceptance measurements. Prototype parser is not full schema validation.

Ticket stays claimed/open for Marek's layout and behavior feedback. No design
verdict or implementation readiness is claimed; no Pages settings/deployment,
production catalog changes or push occurred.
