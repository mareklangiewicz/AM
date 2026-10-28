# Approved manual freshness refresh succeeded

Ticket [34](../issues/34-one-manual-freshness-run.md).
[Run 40606441534](https://github.com/mareklangiewicz/AM/actions/runs/40606441534)
executed once, attempt 1, at approved source
`3ad023822c4df52e3f69874b21200899bf7d3e82`. Immediately preceding read-only
checks confirmed only the manual catalog workflow active, other six disabled,
Actions enabled and both exact planned source/publication refs unchanged.
No settings changes were made.

All six serial conditional requests returned 200, 4,877,766 entity bytes in
6.319 seconds. All six actual sent validator tuples match prior index entries.
No 304 claim, pagination expansion, retry or additional collection. Actual job
logs confirm contents:read/metadata:read for collection and
contents:write/actions:read/metadata:read for publishing.

The same-run artifact ZIP SHA256 is
`86a1ec4a715e532517797c3c1eb7a99b9eaf8511c12d64e5204b8d331e67c1e2`.
Downloaded artifact digests match GitHub metadata. Local bounded ZIP parsing and
complete recomputation against the exact prior reproduce the candidate tree.
The fetched public Git tree matches it byte for byte, and parent linkage is exact:

- Parent: `a0fdd125558c4629a07c7edd0d7f6f7f96b1dcc1`
- Child: `e8e5cf96295369d90402d7584853eb1d3436463d`
- Tree size: 4,898,621 bytes
- Index SHA256: `6f58c31251c093a202d81a5a715b8e6b01c8f09744f62ab98502e8bfbbb12f28`

At 2026-10-28T00:06:24.216719Z through 00:06:25.866077Z, the unmodified
shell helper with explicit fork AMREPO and the child pin made exactly two real
public GETs, both 200. Exit 0, empty stderr, 450,991 stdout bytes. Public lookup
and body equal the validated published tree; stdout equals body. Real freshness
passed with no stale override. Current recipe filter selected the same original
Obsidian 1.14.5 AppImage URL. No app binary download or host app execution occurred.

Obsidian's response-completed validation time is
2026-10-28T00:05:15.676301+00:00. Its inclusive 24-hour freshness boundary is
**2026-10-29T00:05:15.676301+00:00**, or 01:05:15.676301 Warsaw time.
This is the selected observation's boundary, not a guarantee for every catalog
entry or a recurring refresh commitment.

[Machine checks](manual-freshness-run-checks.json) retain exact run, publication,
conditions, status counts, permissions, observation and public-read relationships.
[Evidence archive](manual-freshness-40606441534-evidence.tar.gz), SHA256
`dad402a7aa734508facad88b5759e0358a47486bd4bcffac39c18c8b2e0c025c`,
contains exact ZIPs, full published-history Git bundle, metadata/logs, scripts,
prechecks and public response/stdout/stderr bytes. It persists evidence beyond
Actions' seven-day artifact retention. Scripts use recorded temporary paths and
are evidence, not installed runtime commands.

All authorized run work is complete. Targeted artifact, tree, hash, conditional,
permission and public-read checks passed. The 107-test result is the preceding
preparation result, not a newly repeated suite. No schedule, extra dispatch,
source expansion, installed-file change, updater/app execution or source-branch
push occurred in this run. Recurring cadence remains a separate decision.
