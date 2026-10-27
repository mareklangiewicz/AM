# First repeat REST observation — 2026-10-27

[Run 40508899451](https://github.com/mareklangiewicz/AM/actions/runs/40508899451) succeeded on source 37bdb433c5b557e73b83033774d5f230f0789fa6, following Marek's instruction to continue with the next observation. Exactly one churn-hour dispatch used previous_run=40500475496. Its prior-artifact retrieval and validation succeeded. No extra experiment or retry was dispatched.

Observation began 2026-10-27 13:04:49.446419 UTC / 14:04:49 Europe/Warsaw, 3,805.878076 seconds (63 minutes 25.878 seconds) after baseline. Job duration was 13 seconds. Before dispatch the probe was the sole active workflow; queued/in-progress/waiting counts were zero.

## Response and change evidence

All six conditional requests returned HTTP 200, not 304. All six exact bodies changed. Each used the previous validated ETag according to the collector code; public response evidence is preserved, not request Authorization headers.

| Endpoint | Body bytes | Changed download_count paths | Other changed paths |
| --- | ---: | ---: | ---: |
| Obsidian list | 450,991 | 60 | 0 |
| Obsidian latest | 13,889 | 8 | 0 |
| Neovim list | 822,241 | 75 | 2 reaction counters |
| Neovim latest | 24,510 | 11 | 0 |
| WezTerm repository-ID list | 2,935,204 | 28 | 0 |
| sqlitebrowser list | 630,919 | 16 | 0 |

There are 198 download-count changes and two reaction-count changes across the six responses. These are response-path counts, not unique asset counts: list/latest endpoints overlap. The only two other JSON paths are Neovim list release [0] reactions +1 and total_count. No descriptions, URL fields, release/asset membership or ordering changed in these bodies.

To avoid interpreting positional paths after a reorder, offline verification compared the ordered release IDs/tags and ordered asset IDs/names in every observation; all sequences agree. The complete diagnostic projections also compare equal at every endpoint. The Obsidian first-AppImage and WezTerm last-nightly-AppImage filter results agree across layouts and across both times. These two diagnostics are not a general installer compatibility guarantee.

## Observed storage changes

Git version 2.56.0; layouts use identical index policy. Packed values below are complete history pack-plus-index sizes, not transfer sizes.

| Metric | Exact REST | Diagnostic projection |
| --- | ---: | ---: |
| Baseline body bytes | 4,877,752 | 622,062 |
| Hour body bytes | 4,877,754 | 622,062 |
| Baseline per-body gzip total | 316,693 | 53,817 |
| Hour per-body gzip total | 316,704 | 53,817 |
| Baseline loose object bytes | 426,596 | 71,799 |
| Two-observation loose object bytes | 853,112 | 72,652 |
| Baseline packed history bytes | 332,096 | 58,368 |
| Two-observation packed history bytes | 336,420 | 58,826 |
| Packed-history increase | 4,324 | 458 |

The unchanged projection still grows because index time/status and Git commits/trees change. The two-byte net change in total raw payload length does not mean two bytes of new Git objects. Exact bodies changed at every endpoint; loose objects roughly doubled, while repacked history reused data efficiently in this sample. Record loose and packed measurements separately.

This demonstrates short-window counter churn and an advantage for delta compression under the chosen Git settings. It does not establish long-term ETag hit rates, annual growth, packing cost at scale, representation compatibility, or fleet representativeness. Retain REST-first measurement through the agreed day observation before revisiting the design. The projection is offline field omission, not a measured GraphQL collector.

## Preserved evidence

All twelve body hashes (six per observation) match their manifests. Local offline analysis successfully validated both rounds and their Git/storage reports; an additional check verified stable projections and ordered release/asset identities. Artifact 12735613680, catalog-quota-probe-40508899451, 661,193 bytes, reports digest sha256:fb5e01cfdeda9907713ff744b4e325b519ed97d3ecbe0ab3fe1b7c506bc36b1a and has seven-day retention.

Repackaged local archive churn-hour-40508899451-evidence.tar.gz contains both rounds and runner comparison.json: 632,626 bytes, SHA-256 18a8d579f69f96e7a74d551dbd224877e6c7113ddb4efa476a4fe62689cc1a15. It is not byte-identical to the uploaded ZIP. The adjacent summary preserves run/artifact identifiers, the hour manifest and full path-level comparison. No request authorization header is saved.

## Next boundary

For a separately authorized churn-day, use previous_run=40508899451. Intended sampling time remains approximately 2026-10-28 12:01 UTC / 13:01 Europe/Warsaw, 24 hours from baseline rather than 24 hours after this repeat. No day dispatch, scheduled follow-up or push was authorized by this observation.
