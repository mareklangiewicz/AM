# Establish the supported pipeline and operating constraints

Type: research
Label: wayfinder:research
Status: resolved
Assignee: catalog_system_research

## Question

What does the supported collection-to-publication-to-browser pipeline actually do,
which existing interfaces/checkpoints can be reused, and which current official
GitHub operating constraints must the new design honor?

Audit maintained source and authoritative docs at the recorded source revision:
entry points, saved-response/live parity, oldest-attempt scheduling, durable versus
end-of-run state, source failure isolation, exact-parent publication, whitelist/
reader bounds, recipe evidence and current browser ownership. Identify facts,
contradictions and unknowns; do not resolve architecture or a layout choice.

Recheck official primary documentation for Actions token primary/secondary quotas,
schedule behavior and credential boundaries, Pages direct-fetch/deployment
constraints, and Git repository/history health guidance relevant to generated YAML.
Explain any applicability caveats and distinguish documented limits from observed
headers. Do not infer the cause of the recorded 5,000 core allowance.
Use only public read-only research; no authenticated acquisition, dispatch or
remote mutation is needed. No quota/cap increase is decided here.

Produce one concise current-system overview, a source-linked constraint table and
a decision-relevant gaps list in one report. Use an isolated local research branch,
commit only the report, and provide its exact commit/path context pointer here.
Home guidance requires a separate push decision; do not push or merge the branch.

## Answer — November 7, 2026

The supported normalization, retained merge, saved-response replay, validation
and exact-parent publication seams are reusable. Current release successes stay
in memory until end-of-run publication; interruption loses that run's progress.
Discovery writes atomic evidence checkpoints but the CLI refuses an existing
output and does not ingest previous results for automatic continuation.

The report is written after local publication, left in runner temporary storage
and precedes the remote push. It cannot establish public latest-attempt health
or remote publication success. Current tree validation rejects added health files;
full-snapshot materialization and Git-history/reader bounds remain constraints.
The acquisition/publication job currently has write permissions throughout.
The browser prototype does not load recipe policy or fully validate domain schemas;
its separate prototype branch is not the accepted main-marek website-code home.

Current official documentation still gives the ordinary Actions GITHUB_TOKEN
1,000 requests/hour/repository. The historical 5,000 headers remain unexplained.
Anonymous browser ref lookup has its own IP-based API budget. Scheduled runs can
be delayed/dropped; hourly cron is not a freshness guarantee. Git repository-health
recommendations explicitly call out generated files/history and directory width.
These facts inform the open decisions; they do not accept new storage, quota,
permissions, contracts or browser behavior.

Context: isolated local branch `research/catalog-system-constraints`, commit
`04561383957be55899bad0872973f02fdf31d2b6`, report
`docs/track/catalog-system/research/supported-system-and-constraints.md`.

Read the concise overview, primary-source constraint table and gaps with:

```sh
git show 04561383957be55899bad0872973f02fdf31d2b6:docs/track/catalog-system/research/supported-system-and-constraints.md
```

Source audit is pinned to a149fe60aecf90671e555b1d53a0402c9a3db733 and browser
prototype e7539f5d2e592f4f599b8d2144dc3f754f0aa0d3. Report whitespace check
passed. No fresh remote-state check, acquisition, tests, capacity measurement or
browser acceptance is claimed. The research branch is committed, unmerged and
unpushed. The findings fit the existing questions; no additional decision ticket
is needed from this audit.
