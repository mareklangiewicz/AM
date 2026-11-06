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

## Human feedback and keyboard iteration — November 6, 2026

Marek finds all three variants interesting, has not chosen, and requests keeping
all available for further exploration. Required: Vim-like full keyboard navigation.
Prototype iteration `9867c6ccb` on `prototype/catalog-pages` retains A/B/C and
adds j/k control traversal, h/l app/detail panes, gg/G endpoints, / search,
Escape input/scope reset, Ctrl-d/u half-page scrolling, bracket/arrow variant
cycling and ? modal help. Native Tab/Shift-Tab/Enter/Space remain available.
Focus outlines and restoration across redraws are included; typing fields keep
editing behavior. Moving focus does not activate links/downloads.
Syntax and keyboard-handler smoke checks pass; real-browser focus, mobile and
accessibility verification remain outstanding. No winning variant or complete
experience acceptance is recorded. Preview remains http://localhost:8765/;
refresh an existing tab to load updated code. No push or deployment.

## Public prototype authorization — November 6, 2026

Marek requested publishing now and continuing development publicly. This is a
specific exception to the planning-only deployment boundary, not acceptance of a
layout or authorization for catalog/runtime changes. Publish only index.html,
app.mjs, catalog.mjs and keyboard.mjs from prototype/catalog-pages. Reviewed
browser payload contains public catalog URLs and no credentials/private notes or
local paths. README/research/tracker/recovery files are excluded from the artifact.
Same-repository Pages, no inherited custom domain. All variants remain available.

The maintained main workflow stages that explicit allowlist and deploys Pages;
the prototype branch also carries it for automatic pushes affecting those files.
Inherited root Jekyll publishing is skipped in this fork to avoid replacing the
reviewed artifact with repository-root content. Public-browser verification and
actual deployment receipts follow; the ticket stays unresolved for human review.

## Public deployment receipt — November 6, 2026

Enabled repository Pages with build_type=workflow, no repository CNAME. GitHub
inherits the account domain, so the live HTTPS URL is
https://mareklangiewicz.pl/AM/ (not the initially predicted github.io address).
The repository was already public. Artifact allowlist review found no credentials,
private notes or local paths in the four browser files; this is a scoped payload
review, not a claim of auditing all repository history.

Prototype source `e7539f5d2` deployed successfully via main-marek workflow run
https://github.com/mareklangiewicz/AM/actions/runs/42216569353 .
Initial prototype-branch run 42216533345 failed because the newly created Pages
environment initially allowed main-marek only. Added exactly prototype/catalog-pages
to the environment's allowed branches; no arbitrary-branch permission. Future
prototype pushes matching browser/workflow paths automatically deploy; manual
main-marek dispatch also reads prototype/catalog-pages. No catalog dispatch/change.

HTTPS readback returned 200 and byte-equality for all four files:

- index.html: 5,993 bytes, SHA-256 0340d38bfaea666f3382bb29e5c0e4e1b57bd021f241d2e2e4cd95608cfed459
- app.mjs: 9,305 bytes, SHA-256 b8f68ef5422063519f7c8e4f09342d869ea9df7f113f54ff4362839dc8e765ed
- catalog.mjs: 1,395 bytes, SHA-256 56697b596744bc11e4f9b3650ae75d02d7168152ffa6d8307823e1210ab23c0f
- keyboard.mjs: 2,332 bytes, SHA-256 c9dfc153a2c40b6a03743fd1af9ab227489c8c52ed09e74e3fd2f02c15ad567c

No browser was connected for visual/interaction verification. Layout choice and
browser acceptance remain open. All three variants remain publicly available.
