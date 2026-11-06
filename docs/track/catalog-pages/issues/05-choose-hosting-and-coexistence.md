# Choose the Pages home and existing-site coexistence

Type: grilling
Label: wayfinder:grilling
Status: resolved
Blocked by: 01

## Question

Should the catalog browser use this AM repository's Pages site or a dedicated
repository, and must existing site content coexist? Inspect actual fork Pages
settings read-only before presenting factual options. The repository contains a
manual Jekyll workflow and inherited CNAME am.osowoso.org; neither establishes
that this fork owns or actively uses that domain. Choose the intended URL and
content boundary with Marek; do not change settings or publish during planning.

## Comments

November 6, 2026 read-only check requested by Marek:

- `gh api repos/ivan-hc/AM/pages` reports built, workflow publishing,
  custom domain am.osowoso.org verified, public site http://am.osowoso.org/.
  HTTPS URL https://am.osowoso.org/ loads AM documentation successfully.
- Latest three runs of the upstream Jekyll workflow succeeded: September 6,
  July 27 and May 26, 2026. Latest run:
  https://github.com/ivan-hc/AM/actions/runs/34003657406 .
  Current upstream workflow is manual-only (push trigger commented out).
  This establishes live upstream use, not automatic publication on each commit.
- Related public directory https://portable-linux-apps.github.io/ loads a
  searchable app directory and links to app pages. This is separate from our
  YAML release catalog. Old /apps.html is a moved-page notice.
- `gh api repos/mareklangiewicz/AM` reports has_pages=false; its /pages API
  returns 404 and no Jekyll runs were returned. Our fork has no configured
  Pages site per the observed repository metadata. Do not inherit upstream CNAME.

Hosting choice remains open for Marek; no settings or deployments changed.

## Answer

Marek accepted the November 6 recommendation: use this same AM repository,
maintain website HTML/CSS/JavaScript on main-marek and publish through Pages;
keep release-catalog as the authoritative YAML-only data branch. No inherited
custom domain. No existing fork Pages site was found to preserve.

Browser code resolves release-catalog to one exact commit per page load, then
reads apps.yaml and repository YAML at that commit on demand. No generated
catalog index, copied dataset or data synchronization in the chosen starting
approach. Catalog changes can appear on a new page load without site redeployment.
This supersedes the generated-presentation-index recommendation in the snapshot
research, not its underlying factual findings. Direct-fetch feasibility,
large-integer preservation, failure behavior and performance remain prototype
questions; this decision does not claim they have passed.

No implementation, push, Pages configuration or publication is authorized by this
planning resolution. The intended default project address is
https://mareklangiewicz.github.io/AM/ once separately configured and deployed.
