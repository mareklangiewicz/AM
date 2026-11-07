# Real 500-source catalog publication

Marek authorized push and publication of the prepared cohort at `84d19a4c2`.
Source `b2e63b11a3b37d10378a309cb06fbcfe103fb834` is pushed to `main-marek`.
[Manual run 42385542750](https://github.com/mareklangiewicz/AM/actions/runs/42385542750)
succeeds for **509 apps / 500 verified numeric sources** in one batch:
500 actual collector requests, 500 successful sources, zero failures/unattempted
sources/pending apps. The job runs from 15:16:11 to 15:25:17 UTC on November 7,
2026 (546 seconds). Collector command time is 518.95 seconds, including
434.66 seconds acquisition.

Exact published pin: `cbda9fb78ce4a6f29bdabd63d57f3c0085e8744f`.
Actual fetched parent: `08a0fbd526156a456a8648e71d9d2be11734bc74`.
The workflow pushes a direct child with an exact lease. Both exact pins pass the
maintained bounded distributed-reader, canonical-byte and cross-reference checks.
All 509 app mappings equal source enrollment; all 500 source names/numeric IDs
match, with successful collection status and the dispatched source in schema
provenance. All previous app/source identities and retained release IDs survive;
effective release observations never decrease.

[Portable receipt](next-500-publication.json) binds exact pins, per-document
hashes and source last-success observations, log archive digest and live metrics.
Response bytes total 341,439,276 / 536,870,912; YAML totals 63,690,470 bytes,
largest document 1,372,340 / 2,097,152. The history guard is
120,920,444 / 268,435,456 bytes, with 69,455,938 object bytes after publication.
The 500/hour ceiling and existing transfer/time/file/history/reader/freshness
limits remain unchanged. This is observed CI operation for 500 real upstreams;
whole-snapshot materialization, retained growth and attribution still prevent
claiming support for thousands or all-GitHub completion.

Core headers again report limit 5,000 (4,999 first remaining, 4,500 last).
The collector independently reports 500 actual attempts using its redirect-
refusing transport. Keep conservative documented 1,000/hour planning; the cause
of the larger measured allowance remains unresolved. Discovery's separate
logical-GET/redirect counting limitation stays with [151](../issues/151-bound-discovery-redirect-request-accounting.md)
and does not alter this collector receipt or verified numeric identities.
No source lacks success and the 24/36/48-hour source age counts are zero;
retained releases absent from the fetched page keep their earlier observations.

The preparation's 12 focused tests passed on this manifest; the earlier full
159-test collector result belongs to the preceding 320-source manifest. No
additional full-suite rerun, browser DOM/CORS/mobile acceptance or website rebuild
is claimed. Recent workflow inspection still shows this manual run as latest;
the first natural trigger at the hourly cadence remains unobserved.
No installed-host refresh, recipe migration, app installation/update or yadm
pointer operation occurred.

Raw logs, verifier and fetched publication objects remain at
`/home/marek/Documents/Codex/am-500-publication-20261107/`.
[150](../issues/150-publish-500-source-cohort.md) is resolved. Broad coverage,
remaining source attribution and storage scaling remain with 138.
