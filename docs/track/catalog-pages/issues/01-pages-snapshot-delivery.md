# Choose snapshot delivery and GitHub Pages publishing

Type: research
Label: wayfinder:research
Status: resolved
Assignee: pages_research

## Question

Which static generation or browser-loading approach can serve the published YAML catalog on GitHub Pages, preserve exact-snapshot consistency and useful deep links, and scale beyond the recorded 9.67 MB baseline? Investigate current official Pages/Actions constraints, existing repository workflows and data contracts. Compare viable approaches, failure behavior, refresh triggers and maintenance costs; recommend a route without implementing or publishing it.

## Answer

Research complete; engineering recommendation remains subject to human design decisions.
Use generated app HTML, compact search and lazy paginated history from one exact
catalog SHA, in a separate Pages artifact. The authoritative catalog allows YAML
only. Prefer a dependent Pages job after successful catalog publication; do not
rely on GITHUB_TOKEN pushes triggering another push workflow. Current documented
Pages constraints include 1 GB published size, soft 100 GB/month bandwidth and
ten-minute deployment timeout. No scale performance has been measured.

Context: local branch `research/catalog-pages-delivery`, commit
`931f4ebc551b3d890dc909995c1d91717ce841ca`, file
`docs/track/catalog-pages/research/pages-snapshot-delivery.md`.
Read with `git show COMMIT:PATH`; research branch stays unmerged and unpushed.
Report cites primary GitHub documentation and repository contracts.

Existing Jekyll workflow and inherited CNAME require a human hosting/coexistence
decision; actual fork Pages settings remain unverified. No deployment or setting
change occurred. Stale-tab retention and acceptance budgets remain later decisions.
