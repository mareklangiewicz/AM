# Replacement REST baseline — complete

[Run 40500475496](https://github.com/mareklangiewicz/AM/actions/runs/40500475496) succeeded on source 37bdb433c5b557e73b83033774d5f230f0789fa6. Exactly one separately authorized replacement baseline was dispatched. Observation interval: 2026-10-27 12:01:23.568343–12:01:28.351063 UTC (13:01 Europe/Warsaw). Job duration: 27 seconds.

Before dispatch the probe was the sole active workflow and queued/in-progress/waiting counts were zero. After completion all five unrelated workflows remained disabled. No further dispatch, retry, schedule or automatic follow-up was created.

## Coverage and response sizes

All six fixed requests returned HTTP 200 with ETags; complete=true. No redirect was followed, no extra page was fetched, and no GraphQL, app binary, installer or updater was executed.

| Endpoint | Body bytes | Releases | Assets |
| --- | ---: | ---: | ---: |
| Obsidian list | 450,991 | 30 | 269 |
| Obsidian latest | 13,889 | 1 | 8 |
| Neovim list | 822,241 | 30 | 376 |
| Neovim latest | 24,510 | 1 | 12 |
| WezTerm repository-ID list?per_page=100 | 2,935,202 | 64 | 1,675 |
| sqlitebrowser list?per_page=100 | 630,919 | 42 | 197 |

List and latest observations overlap; asset/release counts must not be summed as unique entities. Obsidian and Neovim list responses expose additional pages; preserving this page is the intended scope, not full-history collection. WezTerm's explicit target returned 200. Its observed download URLs contain github.com/wezterm/wezterm, but no owner-name API lookup was performed.

## Storage baseline, not churn

Runner comparison (git version 2.56.0), with identical 1,111-byte check/status indices:

| Layout | Body bytes | Sum of per-body gzip bytes | Loose object bytes | Pack plus index bytes |
| --- | ---: | ---: | ---: | ---: |
| Exact REST | 4,877,752 | 316,693 | 426,596 | 332,096 |
| Diagnostic projection | 622,062 | 53,817 | 71,799 | 58,368 |

These are one-observation totals. No changed-body frequency, retention cost, conditional-repeat behavior or annual growth has been measured. GraphQL was not used; the projection's savings come from omitted fields, and its lower byte count is not a drop-in compatibility result.

The Obsidian first-AppImage and WezTerm last-nightly-AppImage diagnostics agreed between exact and projected bodies in this sample. This is not a general compatibility guarantee; the actual recipe scripts were not executed. Events-based identity remains unsupported.

Quota headers reported 5,000 limits with at least 4,992 remaining, but latest endpoints had different reset/counter sequences from list endpoints. Do not interpret these counters as a consistent six-request budget delta or a universal future limit.

## Evidence and validation

All six saved body hashes match their manifest. Local offline analysis validated complete prior-history shape/hashes and reproduced body byte totals from the runner report. Artifact 12733090330 (catalog-quota-probe-40500475496), 330,497 bytes, reported digest sha256:6e94383ecf605712ebe6be97e85eaf13da9a7bfed82f4366785ef46dc4241866, has seven-day retention.

Persistent local repackaged archive: churn-baseline-40500475496-evidence.tar.gz, 316,425 bytes, SHA-256 7d8de7ff6260d65af7ed914bf1136717b8b7fbf83a3bc87725c74fdecbcd8d52. It contains the exact six bodies, observation metadata and runner comparison.json; it is not byte-identical to the uploaded ZIP. Adjacent summary JSON preserves artifact identifiers, the manifest and comparison. No request authorization header is saved.

## Next observation

This is the valid baseline for churn-hour; use previous_run=40500475496. The intended +1-hour point is approximately 2026-10-27 13:01 UTC / 14:01 Europe/Warsaw; the intended +24-hour point is 2026-10-28 12:01 UTC / 13:01 Europe/Warsaw. These are sampling targets, not scheduled jobs or authorizations. Each observation still requires explicit instruction. Actual elapsed time must be reported if the sampling time differs.
