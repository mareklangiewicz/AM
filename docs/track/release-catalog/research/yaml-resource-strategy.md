# YAML resource strategy — scoped retention revision, November 3, 2026

Status: trial proposals, not deployed budgets. [Current retention design](yaml-retention-revision.md)
supersedes this document's earlier mandatory full-history assumptions. Ticket 71
remains open for bounded implementation and operational measurements.

November 4 follow-up: [retained-growth and staging measurements](yaml-retained-growth.md)
exercise the revised schema. Thirty 100-new-ID merges grow to 5.00 MB; near-cap
staging reaches 16.73 MB at about 125 MiB peak RSS. A 16.67 MB reader fixture
passes mawk/GNU awk but BusyBox hits the local 55-second CPU cap, with zero query
output. The 16 MiB candidate below remains provisional, not a portable performance
ceiling. Hard collector limits and live run-capacity gates remain outstanding.

## Consumer

Keep record-scoped validation and private output spooling so malformed suffixes
expose no query output. The [memory experiment](yaml-reader-memory-experiment.md)
found roughly flat RSS on mawk/GNU awk for tested shapes, but BusyBox reached
54,360 KiB on a 16.38 MB fixture. Fixed storage slots gave no memory benefit.
The revised observation/scope schema now has the linked growth/staging matrix;
neither that matrix nor the old measurements establish portable worst-case bounds.

Bound acquired input bytes, line size, process memory, projected output and
private temporary storage independently. Restrict batch columns to schema scalar
fields without duplicates (now ten release scalar fields, five asset fields).
Test write failures, storage exhaustion, maximum string/row lengths and malformed
input. Callers must still check status after copying validated output.

## Incremental collector

Normalize each bounded page, discard its raw response, and stage a merge with the
previous retained catalog. Keep unfetched records unchanged and replace fetched
records with their actual response observation times. Commit per source only
after requested scope completion, normalization, merged-document validation and
all resource bounds pass. A safety stop before completion is `collection_limit`;
no staged fact/timestamp changes survive. A completed finite scope succeeds even
if more upstream pages exist. A completed empty page does not erase retained data.

Default scheduled scope: all configured sources, page_size=100, page_limit=1.
Manual requests can select other subsets and limits, including `all`, always
under explicit safety budgets. Resource limits never implicitly rewrite scope.
Partial absence never prunes records. Explicit full-history reconciliation follows
the retention policy; no automatic count/age eviction is part of collection.

## Candidate ceilings for a local integration trial

These are proposed guardrails, not accepted production budgets or guarantees.
They must apply to input and the retained merge, not just the latest page.

| Safety scope | Candidate ceiling | Required evidence |
| --- | --- | --- |
| Per-source page attempts | 64 | Separate from requested limit; a larger request fails if it cannot reach EOF within this guard |
| One response body | 16 MiB | JSON memory amplification/normalization CPU still unmeasured at the boundary |
| Aggregate raw source bytes | 96 MiB | Manual long-history behavior still needs exact-format measurement |
| Merged repository YAML | 16 MiB | Accumulation can exceed this even with one-page requests; fail without silent eviction |
| Physical YAML line | 64 KiB | Maximum-string CPU and allocation need measurement |
| Aggregate page attempts per run | 900 | Recount configured sources; reserve other calls and obey actual credential limits |
| Aggregate raw transfer per run | 1 GiB | Default one-page bytes and retained-merge costs need actual runner measurements |
| Source / run elapsed time | 120 s / 20 min | Enforce actual deadlines; fixture simulation is not runtime enforcement |

For the recorded 772-identity inventory the default is 772 first-page attempts,
not the earlier full-history extrapolation of about 976. This does not establish
that all bytes, processing or credential quota fit. Request budgets count failed
attempts; no retries initially. For manual wider scopes, reserve only the requested
remaining pages (or advertised pages for `all`), not the source's full history
when the request is limited. Continue validating changing pagination metadata.
Stop on auth/rate refusals; preserve observations and report unattempted sources.

If aggregate capacity is insufficient, test fair ordering based on last successful
collection with explicit first-observation handling. It governs scope scheduling,
not release freshness. A daily one-page success can coexist with very old retained
releases; this is expected. Installation must judge the selected release's
`observed_at`. Manual deeper collection may refresh it, or the existing explicit
stale override may be required. Never mint fresh timestamps to compensate for
budget or coverage limitations.

## Retention growth and remaining gates

One-page acquisition bounds fetched input records, not accumulated history.
Measure repeated partial merges across many days, including many new IDs and
large embedded asset sets. Measure peak staging and reader memory with a nearly
full retained document plus fetched updates. A merged-size refusal preserves the
previous observation, potentially leaving even recent releases unrefreshed until
maintenance succeeds. Full reconciliation may shrink retention but is itself a
bounded explicit collection; it cannot bypass acquisition/staging guards.

The earlier 58/63-page tail probes inform manual `all` and reconciliation costs.
They no longer imply mandatory daily costs. Before implementation, measure the
revised serializer, worst-case scalar/projection sizes, default runner capacity,
retained-growth behavior and actual resource enforcement. Budget/fairness choices
remain proposals; no deployment, workflow dispatch, push or source repin follows.
