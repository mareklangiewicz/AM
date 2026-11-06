# Public catalog browser on GitHub Pages

Label: wayfinder:map

## Destination

An agreed specification and implementation roadmap for a public, read-only
GitHub Pages catalog browser, with no unresolved decisions before implementation.

## Notes

Planning only. Marek accepted the destination and product direction on November 6,
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

## Not yet specified

Operational recovery and stale-site behavior once snapshot delivery is chosen.
Performance targets and acceptance checks after data/UI approaches are concrete.
Accessibility details, release grouping and empty/error states after prototype review.
Implementation milestones and final handoff after the decisions settle.

## Out of scope

Implementation/deployment during this planning effort; accounts, ratings, submissions,
application binary hosting; expanding catalog enrollment or migration capacity;
installing apps merely to display them; changing AM client selection semantics.
