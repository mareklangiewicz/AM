# Choose snapshot delivery and GitHub Pages publishing

Type: research
Label: wayfinder:research
Status: resolved
Assignee: pages_research

## Question

Which static generation or browser-loading approach can serve the published YAML catalog on GitHub Pages, preserve exact-snapshot consistency and useful deep links, and scale beyond the recorded 9.67 MB baseline? Investigate current official Pages/Actions constraints, existing repository workflows and data contracts. Compare viable approaches, failure behavior, refresh triggers and maintenance costs; recommend a route without implementing or publishing it.

## Answer

[Snapshot delivery research](../research/pages-snapshot-delivery.md) recommends
build-time app HTML, a small search index and lazy paginated history data, all
from one validated exact catalog SHA and deployed as a separate Pages artifact.
Current Pages limits and trigger behavior are verified against official docs;
source catalog limits/format remain unchanged. The inherited Jekyll workflow and
custom-domain file require reconciliation with actual Pages settings. Hosting
location, architecture acceptance and stale-tab retention remain human decisions.
This resolves factual research, not acceptance of the recommendation. No push,
implementation, settings change or publication occurred.
