# Wider history sample and targeted tails — November 3, 2026

Historical evidence at the recorded schema/source revision. The [retention revision](../yaml-retention-revision.md)
supersedes mandatory full-history/default costs and repository check-time freshness.
Old fixtures and measurements are not validation of the revised schema.

## Observed result

A second deterministic uniform sample of 48 distinct active repository identities,
excluding the original 24, required 65 requests. All 48 reached the end of release
pagination, with 3,103 release records, 25,233 embedded assets, 50,874,912 raw
response bytes and 10,069,031 provisional YAML bytes in 78.8805 seconds.
Nine histories needed multiple pages; the largest had 448 releases across five
pages. The largest projected document was 2,087,326 bytes (repository 947512058,
400 releases, 4,776 embedded assets). Largest individual response: 4,589,234 bytes.
No duplicate release IDs were observed in this sample.

The original 24 plus these 48 form 72 disjoint randomly sampled identities:
91 requests versus 72 first pages. A purely illustrative scaling to 772 sources
is about 976 requests; scaling the second sample alone gives about 1,045.
Neither estimates the actual full-inventory cost or guarantees fit in a runner
quota. A local authenticated credential's quota is not evidence of the workflow
credential's quota. Request headroom needs an explicit operational budget.

## Targeted tails change the capacity question

A separate nonrandom probe selected five active identities with plausible frequent
release histories: neovim, Floorp AppImage, FreeCAD, PCSX2 and RPCS3 Linux binaries.
These identities came from the current prepared inventory, not guessed redirects.
It used six requests and 6,705,513 bytes in 9.0173 seconds. Three histories were
completed (56, 77 and 129 releases). PCSX2's first page advertised **58 pages**;
RPCS3's advertised **63 pages**. Only their first pages were acquired because
completing either exceeded the probe's remaining request budget. Those advertised
counts are observations, not an independently verified exact release count.
No full-history byte/YAML totals can be inferred from their first-page sizes.

This directly rules out treating the random sample's five-page maximum as an
inventory ceiling. A small page ceiling would intentionally fail these active
sources. A high per-source ceiling alone does not solve aggregate request cost.

## Reproduction, bounds and interpretation

Run `python3 docs/track/release-catalog/research/yaml-history-outliers-20261103/measure.py`
for the second random sample. Seed 20261104 selects 48 from the 748 identities
outside the earlier sample. Limits: 96 attempts, 16 MiB per response, 180 MiB
aggregate bytes, 240-second initiation deadline. The targeted script is adjacent
under `../yaml-history-targets-20261103/measure.py`; its explicit five IDs are checked
against the same inventory. Limits: 24 attempts, 16 MiB/response, 96 MiB aggregate,
120-second initiation deadline. Each script stops without retries on a request
failure. Network-enabled runs used gh's existing credential in memory. Initial
sandbox runs stopped on transport failure with no response bytes.

Both scripts reuse the prior provisional serializer: sizes are experiments, not
an exact format-2 publication. Raw bodies, release text, URLs and credentials are
not retained. JSON evidence contains only numeric identities, counts, timing,
bytes, pagination and quota remainder. No app download, workflow dispatch,
publication, source repin or remote mutation occurred.

These are bounded samples, not an inventory census, independent asset audit,
transactional release snapshot, runner benchmark or production-normalizer test.
Timeouts bound individual operations and when requests may start; the scripts do
not claim a hard wall-clock deadline across all reads/parsing. Embedded assets
are counted as returned. Inspect full JSON evidence for each observation.

For production budget recommendations see [resource strategy](../yaml-resource-strategy.md).
