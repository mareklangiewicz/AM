# Agree the implementation route and acceptance criteria

Type: grilling
Label: wayfinder:grilling
Status: claimed
Assignee: codex-browser-delivery
Blocked by: 01, 02, 03, 05, ../../catalog-system/issues/02-choose-contextual-education-and-health-navigation.md, ../../catalog-system/issues/03-choose-public-yaml-contracts-and-revision-consistency.md, ../../catalog-system/issues/06-choose-evidence-bound-recipe-classification-and-provenance.md, ../../catalog-system/issues/08-choose-truthful-health-summaries-and-bounded-statistics.md

## Question

Given the research and accepted experience, what architecture, refresh/recovery behavior, accessibility/performance criteria and implementation milestones make the route ready to execute? Resolve with Marek; specify the separate publication authorization boundary.

## Standing direction

The Pages-home decision chooses same-repository Pages with code on main-marek
and direct lazy YAML reads pinned to one catalog commit. Assess the prototype
against this direction; do not silently restore generated indexes or a second
catalog representation. Choose final budgets, refresh/error behavior and optional
enrichment after measurement and human feedback.

## Cross-system planning coordination — November 7, 2026

Resolve browser-specific behavior, delivery and measurable acceptance here after
the linked educational, contract, recipe-provenance and health definitions settle.
Cross-directory blockers are relative to this ticket's directory. Preserve the
existing browsing-experience ticket's layout verdict and claim. The umbrella's
[Agree system acceptance and implementation roadmap](../../catalog-system/issues/10-agree-system-acceptance-and-implementation-roadmap.md)
consumes this answer and owns the final cross-system implementation sequence;
do not produce a competing system-wide roadmap here.

## Prepared delivery and acceptance proposal — November 8, 2026

Pending Marek's decision. Browser 03 now resolves experience direction, including
A default with B/C selectable. This proposal sets testable targets, not claims
that the current prototype meets them. Existing Node timings/HTTP receipts are
reusable context only; no fresh DOM, device or accessibility measurements ran.

### Refresh, caching and failure behavior

Resolve C once on entry, then fetch lazy source/provenance documents only at C.
Resolve S independently when needed for health. Cache by full pin and path, never
by moving ref alone; bounded eviction may refetch at the same pin without losing
route state. No persistent offline/service-worker cache in the first release.
Keep an open tab on its chosen snapshot. “Load latest” is explicit and resolves a
new pin, preserving app/view/release context where it exists and explaining missing
identities/releases. Browser Back/Forward and pinned links restore their own
context, not whatever latest ref exists at navigation time.

Do not poll every source, auto-refresh an active detail view or replace snapshot
facts after a background ref change. A retry reads the failed path at the same
pin. On first-load catalog failure show a useful retry/explicit-latest action;
on detail failure retain the directory and already validated same-pin content.
Unrecognized schema or malformed data is refused, never passed to permissive
parsing. Status failure leaves catalog browsing useful; confirmation lag and
old/new C/S relationships use the accepted contract labels. No arbitrary stale
health verdict or latest-attempt assertion; show original times and known gaps.

### Proposed measurable acceptance targets

Use named pinned fixtures: the saved 500-source snapshot
`cbda9fb78ce4a6f29bdabd63d57f3c0085e8744f` after explicit v3 conversion, its
largest/most asset-heavy retained source cases, shared stable/nightly and unknown
recipe cases, and a labelled synthetic 5,000-app directory. Include the largest
supported source/root documents established in the capacity work; passing today's
small fixtures alone does not qualify future supported sizes. Synthetic directory
results establish local browser behavior only, not real enrollment/acquisition.

Record actual browser/device/version, viewport, cache state and throttle profile.
Use desktop plus narrow mobile layouts and a reproducible browser CPU-throttled
mobile profile (4x slowdown), with an actual mobile-engine/device smoke check
before rollout. Measure a small repeatable set of interactions, reporting range
and worst sample; do not call a tiny sample a population percentile.

Recommend these engineering targets on that recorded reference profile:

- App-name search and view switching visibly settle within 150 ms after input,
  with no directory-wide source fetch. Virtualize/page long lists if necessary;
  every app remains reachable/searchable.
- Directory parse/validation/first usable render completes within 1 second after
  required bytes arrive; opened-source parse/validation/first usable detail within
  500 ms after its required bytes arrive, including the largest supported fixture.
  Show loading immediately and keep navigation usable during expensive work.
- On a recorded cold-network test at 10 Mbit/s and 100 ms latency, target a usable
  directory within 5 seconds from navigation, including required roots but without
  waiting for optional health/provenance detail. Measure real public HTTPS/CORS
  separately; do not guarantee a third-party network SLA. Record failures and
  separate transfer from processing. Avoid making unrelated provenance a
  prerequisite for ordinary name discovery.
- Target applicable WCAG 2.2 AA requirements. Check reflow at 320 CSS px, zoom/text
  resize, light/dark contrast, meaningful headings/labels/status announcements,
  visible unobscured focus, target sizing, screen-reader order and no keyboard
  traps. Native Tab/Shift-Tab/Enter/Space operate all actions; Vim shortcuts respect
  text editing, dialogs and focus restoration and never activate downloads on focus.
  No automated scan alone establishes accessibility conformance.

These are proposed targets to test and fix against, not production kill switches
or permission to reject normal catalog documents that exceed today's caps. A miss
requires a measured explanation and focused optimization/review; do not hide it
by dropping sources/assets or weakening validation.

W3C reference for the selected accessibility target:
[WCAG 2.2](https://www.w3.org/TR/WCAG22/), including
[reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html).
The timing figures are project proposals, not requirements attributed to W3C or
measurements inferred from earlier Node results.

### Focused browser gates and ownership

Exercise one representative journey in all three views: name search → app →
release → all assets/platform inference → evidenced AM choice or explicit unknown
→ exact recipe review/context explanation → health. Check shared stable/nightly
identity/policy differences, catalogue-only-with-existing-recipe and large integer
IDs. Exercise valid/partial/failed/stale/unknown data, unavailable status, schema
refusal, mismatched input pins, old pinned links, explicit latest, and refresh/
Back/Forward focus/state recovery. Keep network failures distinct from absent data.

Desktop Chromium and Firefox plus a mobile browser engine/device must support
core navigation/fetch/parser behavior; document any checked limitations. Run
actual anonymous public fetch/CORS and deployed allowlist readback before public
acceptance. Reuse unaffected fixtures; no full historical per-app lifecycle suite.

The accepted cross-system cutover owns main-source migration, reviewed public
artifact, preview retention and exact deployment rollback. Browser implementation
feeds its checked result into system ticket 10's shared roadmap; this ticket creates
no competing pipeline or implementation sequence. Include a short newcomer/
maintainer comprehension review of coverage/support, source/release freshness,
recipe execution and authenticity, using the accepted app examples.

Decision requested: accept explicit-refresh/error behavior and these performance/
accessibility/browser-check targets. Implementation measurements must establish
whether they are met; remote publishing remains separately authorized.
