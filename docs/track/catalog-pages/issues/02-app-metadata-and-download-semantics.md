# Establish app metadata and trustworthy download presentation

Type: research
Label: wayfinder:research
Status: resolved
Assignee: metadata_research

## Question

What descriptions, icons and asset/platform metadata are already available, and what additional first-party sources could supply them? Establish provenance, reuse-permission limitations, acquisition costs, missing-data fallbacks, shared-repository identity cases, and the boundary between AM-supported selection and general upstream downloads. Recommend what the first version can truthfully show; do not download/execute binaries or expand collection.

## Answer

Research complete; recommendations await human experience/architecture decisions.
Existing YAML includes release and asset facts, sizes/content types and optional
digests, but no descriptions, logos, release-note bodies or structured platforms.
AM choices require pinned recipe policies alongside the catalog snapshot.
The 53 enrolled x86_64 recipe identities include shared stable/nightly repositories;
repository count is not a product count. Prototype must decide product/channel grouping.

Recommend optional cached, attributed upstream repository descriptions (roughly
51 extra GETs for a complete present-scope refresh), generated initials fallbacks,
and incremental logos only with source/permission evidence. Owner avatars are
not app logos. General OS/architecture matching is labelled inference, distinct
from maintained AM selection. Enrichment cadence and failures need explicit design.

Context: local branch `research/catalog-pages-metadata`, commit
`d8950aa2d294a474e6bbe347017eb7499863ffaa`, file
`docs/track/catalog-pages/research/app-metadata-and-download-semantics.md`.
Read with `git show COMMIT:PATH`; research branch stays unmerged and unpushed.
Report cites primary GitHub documentation and repository contracts. No collection,
implementation, binary download or publication occurred.
