# App metadata and trustworthy download presentation

Research: November 6, 2026, source `cfd4f067a`; recorded production snapshot
`b54c4f267ef8a1eb0aca76f01b68e391ee24a0f7`. Recommendations for planning;
no implementation, binary download, collection expansion or push performed.

## Present data

The [normalizer](../../../../tools/catalog-collector/bounded.py) retains release
IDs, tags, optional titles, upstream release-page URLs, timestamps, prerelease
flags and optional source archive URLs. Asset records contain ID, name, exact
download URL, size, content type and optional upstream digest. It does not retain
release-note bodies, asset labels, download counts, descriptions, logos or
structured OS/architecture fields. Upstream API availability is not availability
in our published YAML. [Release API](https://docs.github.com/en/rest/releases/releases),
[asset API](https://docs.github.com/en/rest/releases/assets).

[Declarations](../../../../tools/catalog-collector/recipe_declarations.py) supply
AM app/architecture identity, repository ID, channel, asset patterns and lifecycle
settings, with no common app-description/logo field. The published apps map is
an identity-to-repository mapping, not the complete selection policy. Reproducing
an AM choice needs pinned recipe/policy source as well as a catalog snapshot.
[Publication code](../../../../tools/catalog-collector/yaml_publication.py).

All current [enrolled recipes](../../../../tools/catalog-collector/collection-recipes.txt)
use x86_64 paths. Neovim stable/nightly share repository 16408992; Neovide
stable/nightly share 226408450. Thus 53 recipes map to 51 repositories, and neither
count alone establishes the count of distinct human-facing products. Grouping
channels into products must preserve separate install identities and choices.

AM `about` descriptions currently come through `modules/database.am` from runtime
Markdown fetches to Portable-Linux-Apps/Portable-Linux-Apps.github.io. They are a
separate, generally third-party source, not descriptions present in catalog YAML.
Their reuse would need its own provenance/content review.

## Enrichment sources and costs

The repository endpoint offers nullable description, homepage, topics, license
metadata and owner avatar. It offers no generic app-logo field: an owner avatar
must not be called an app icon. A repository description may describe packaging
rather than the product. Attribute it as an upstream repository description and
allow unsuitable or missing values. [Repository API](https://docs.github.com/en/rest/repos/repos).

Recommend optional build-time cached metadata keyed by numeric repository ID,
with endpoint, retrieval time and response hash. Baseline full repository-metadata
refresh costs approximately 51 extra GETs; README, license or logo discovery adds
requests and bytes. This is a proposed side input, not authorization to spend the
production collector's existing budgets. Avoid per-app visitor API calls:
unauthenticated primary limits are 60/hour/IP; Actions GITHUB_TOKEN normally has
1,000/hour/repository. These limits are not a measured design budget.
[Rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).
Use bounded serial refresh, cached results, appropriate retries and conditional
requests; correctly authenticated 304 responses avoid primary-limit charges.
[API practices](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api).

For a first-party logo or metainfo file, record explicit source commit/path and
applicable reuse terms. The contents API accepts a commit ref; its returned
download URLs can expire and are transport, not durable provenance.
[Contents API](https://docs.github.com/en/rest/repos/contents).
Public availability or a detected repository license alone does not establish
permission for every logo or trademark. GitHub notes default copyright restrictions
without a license and describes limited license detection. Treat asset permissions
as per-source evidence, not a blanket claim about public repositories.
[Licensing documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).

Fallback: app/recipe name, upstream owner/repository and locally generated initials
tile. Missing icons must not block publication. Do not make README scraping,
binary icon extraction or arbitrary remote SVG/HTML insertion prerequisites.
Render enriched strings as text; richer content requires a deliberate sanitized path.

## Download semantics

Show exact asset name, size, tag, prerelease state and original upstream links.
OS/architecture inferred from filenames or content type is a labelled heuristic,
not verified compatibility. Permit unknown/ambiguous values and access to all
assets. A separately labelled AM selection must reproduce the maintained selector
for the declared architecture/channel using the same pinned catalog and source
policy. It establishes no AM support for other Windows/macOS/ARM assets upstream.
[Operating policy](../../../catalog-operating-policy.md).

An optional upstream digest is metadata, not independent binary/publisher
verification. Preserve the asset URL rather than substituting GitHub latest
shortcuts. Link upstream release notes; our YAML does not retain their bodies.
Show effective per-release observation time, including shared-default overrides,
partial-history status and exact snapshot. Collection/publication timestamps are
not substitutes for release freshness. AM's existing 48-hour selection freshness
policy does not prevent people browsing older release records.
[Retention semantics](../../../../tools/catalog-collector/retention.py).

## Recommendation and remaining decisions

Start with existing release facts and pinned AM declarations; allow optional
cached attributed repository descriptions and generated icon fallbacks. Add logos
incrementally with source/permission evidence. No catalog schema or enrollment
change is needed merely to prototype the experience. Human decisions remain:
product/channel grouping, inferred-platform and stale-choice wording, default
provenance visibility, enrichment cadence and enrichment-failure isolation.
