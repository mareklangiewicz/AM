# 320-source catalog publication

Marek authorized push and publication of the prepared cohort. Source
`5d7af43478555f154d4cae99abe9ce30b5e125ad` is pushed to `main-marek`.
[Manual run 42369094432](https://github.com/mareklangiewicz/AM/actions/runs/42369094432)
succeeds, publishing **325 apps / 320 verified numeric sources** in one batch:
320 requests, 320 successes, zero failures/unattempted sources/pending apps.
The job runs from 11:39:31 to 11:45:39 UTC on November 7, 2026 (368 seconds).
The collector command takes 343.56 seconds, including 283.85 seconds acquisition.

Exact published pin: `08a0fbd526156a456a8648e71d9d2be11734bc74`.
Actual fetched parent: `59b3f3f398bc1013c7b5caf0f37b19a4f3fc9821`.
The workflow publishes a direct child with an exact lease. Both exact pins pass
bounded distributed-reader, canonical byte and cross-reference validation locally.
All 325 app mappings equal source enrollment; all 320 repository names/numeric IDs
match, source collection statuses are successful and schema provenance matches
the dispatched source. All previous app/source identities and retained release
IDs survive, and effective release observations never decrease.

[Portable receipt](next-320-publication.json) binds the log archive digest,
per-document digests, source last-success observations, actual parent and metrics.
Response bytes total 240,500,608; YAML totals 44,626,132 bytes, largest document
1,372,340 bytes. The local history guard is 100,065,961 / 268,435,456 bytes;
Git object bytes after publication are 63,807,434. The 500/hour ceiling and all
other deployed limits remain unchanged. These are 320 real sources, not a claim
that 500 sources or thousands have been exercised in CI.

Core headers again report limit 5,000, remaining 4,851 first / 4,532 last.
Keep conservative documented 1,000/hour planning; the cause of the larger observed
allowance remains unresolved. The collector independently reports 320 attempts.
No source lacks a successful observation and the 24/36/48-hour source age counts
are zero; this does not freshen releases absent from the fetched page.

The preparation's 159-test regression result remains applicable: this operation
changes no production code beyond that tested enrollment. Publication verification
is fresh; no additional full-suite rerun or browser DOM/CORS/mobile acceptance is
claimed. The first natural trigger at the new hourly cadence remains unobserved.
No installed-host refresh, recipe migration, app installation/update, website
rebuild or yadm pointer operation occurs.

Raw logs, verifier and fetched Git objects are preserved at
`/home/marek/Documents/Codex/am-320-publication-20261107/`.
[148](../issues/148-publish-320-source-cohort.md) is resolved; broad catalog
coverage and remaining storage/attribution work stay with 138.
