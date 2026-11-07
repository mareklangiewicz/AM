# Public catalog browser on GitHub Pages

Label: wayfinder:map

## Current planning entry point

[Understandable catalog system and educational browser](../catalog-system/map.md)
coordinates the broader system specification. This browser map retains ownership
of its existing layout/prototype and browser-delivery decisions. Its historical
baseline below is not a current coverage claim. Consult the new brief for the
accepted educational and transparency requirements, without restarting resolved
hosting choices or treating prototype deployment as design acceptance.

## Destination

An agreed specification and implementation roadmap for a public, read-only
GitHub Pages catalog browser, with no unresolved decisions before implementation.

## Notes

November 8, 2026: Marek selected A (directory) as the default while keeping B
(split-pane explorer) and C (release desk) selectable. The existing claimed
[browser review](issues/03-review-browser-experience.md#accepted-default-view--november-8-2026)
records the default and accepted first-release experience. Delivery targets are
now accepted in ticket 04; actual browser verification and delivery evidence remain
outstanding.

Planning with an explicitly authorized public prototype deployment on November 6,
2026; this does not accept a final design. Live preview: https://mareklangiewicz.pl/AM/ .
See the browsing-experience ticket for the receipt. Marek accepted the destination and product direction on November 6,
2026: app discovery first; AM users and data enthusiasts also supported; grow
with published coverage. Searchable app directory and individual app pages with
descriptions, releases and assets; OS/architecture matching highlights with all
assets accessible; distinguish AM-supported selections from other upstream assets.
Show upstream attribution, observation freshness, partial history and exact snapshot.
Clean responsive design, light/dark themes, restrained branding; shareable links.
Use upstream descriptions/icons where available, with simple fallbacks, subject
to provenance, permission and acquisition research. No editorial-content dependency.

Consult wayfinder, grilling and domain-modeling for decisions; research for factual
investigations and prototype for human-reviewed experience exploration. Preserve
catalog facts/client selection separation and per-release observation semantics.
Current baseline: verified publication b54c4f267ef8a1eb0aca76f01b68e391ee24a0f7,
51 repositories, 53 AM recipes, 2,145 releases, 29,993 assets, 9,666,397 YAML bytes.
This is a recorded snapshot, not a guarantee about the latest remote tip.

Tracker adaptation: local files are map children by directory; Type/Label express
wayfinder type, Status/Assignee express claims, Blocked by expresses dependencies.
No triage labels on wayfinder decisions (explicit invoked-skill convention).
Frontier: open unblocked tickets in numeric order. Answers live in tickets;
map indexes only resolved decisions. Research uses isolated local branches;
AM pushes and publication remain subject to Marek's separate approval.

## Decisions so far

- [Choose snapshot delivery and GitHub Pages publishing](issues/01-pages-snapshot-delivery.md): research recommends separate generated presentation from an exact catalog pin; hosting and architecture acceptance remain human decisions.

- [Establish app metadata and trustworthy download presentation](issues/02-app-metadata-and-download-semantics.md): existing release facts suffice for browsing; research recommends optional attributed descriptions, icon fallbacks and explicit AM/inferred-match distinction.

- [Choose the Pages home and existing-site coexistence](issues/05-choose-hosting-and-coexistence.md): same repository, code on main-marek, direct JavaScript reads pinned to a release-catalog commit; supersedes generated-index recommendation, pending feasibility prototype.

- [Choose the catalog browsing experience](issues/03-review-browser-experience.md#answer--november-8-2026): accepted A default with B/C selectable, separate app/channel identities, scoped lazy search/detail, bounded retained history/all assets, and optional verified enrichment with fallbacks.

- [Agree the implementation route and acceptance criteria](issues/04-agree-delivery-and-acceptance.md#answer--november-8-2026): accepted explicit refresh/error behavior, measured processing/loading targets, WCAG 2.2 AA target and real desktop/mobile/keyboard/fetch checks; execution evidence remains required. System ticket 10 owns the shared implementation roadmap.

## Not yet specified

Browser experience and delivery decisions are resolved. The final shared roadmap
is owned by catalog-system ticket 10. Implementation must produce actual browser,
performance/mobile/accessibility and public-fetch evidence against these decisions;
planning acceptance is not implementation acceptance.

## Out of scope

Production implementation beyond the authorized public prototype; accounts, ratings, submissions,
application binary hosting; expanding catalog enrollment or migration capacity;
installing apps merely to display them; changing AM client selection semantics.
