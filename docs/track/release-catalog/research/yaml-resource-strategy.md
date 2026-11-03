# YAML resource strategy — measured proposal, November 3, 2026

Status: research recommendation, not an accepted production budget or deployment.
Ticket 71 remains open. Preserve the accepted complete-history/failure model.

## Consumer strategy

Prefer one-pass record-scoped validation with private output spooling over a
whole-document object store. Validate required fields as each asset/release
closes, keep previous sibling IDs to enforce strict ordering, and discard closed
facts. Keep full paths for query matching; fixed storage slots gave no measured benefit.
The schema's fixed depth and fixed field sets permit bounded logical live state,
but BusyBox process RSS still grows on the large fixture.
The private spool holds query output until EOF and root-state validation succeed.
There is no second read of a mutable input, and malformed suffixes expose no
query output. An interrupted output copy can still produce partial bytes; callers
must check status. The [completed experiment](yaml-reader-memory-experiment.md) supports the contract
but does not establish portable constant RSS. Production resource/failure tests
remain necessary.

Do not transplant the prototype wrapper unchanged. Production needs bounded
network acquisition into a private file, private temporary directory/cleanup,
explicit disk/write failure handling and output bounds. Limit projections to
schema fields without repeated columns (at most nine release scalar fields or
five asset fields). Budget each command's input and output separately. Keep
validation and decoding shared with scalar lookups. Repeated per-field scans
remain the wrong selection loop; use a batch projection.

## Collector strategy

Normalize each bounded API page promptly and discard raw JSON after checking it.
Retain only bounded normalized facts plus release-ID bookkeeping; sort numeric
IDs before final output. A temporary directory can hold staged normalized records
if a bounded in-memory representation exceeds the measured worker allocation.
Never collect all raw pages in RAM as the measurement script does. Measure Python
JSON expansion and normalization CPU at the response and document ceilings.

A source is successful only after reaching the end of published release pagination
and passing normalization/validation. Exhausting any source or aggregate ceiling
is `collection_limit`: retain the previous complete observation and check time,
or publish failed-before-first-observation. Do not publish a truncated history as
success. Embedded assets retain the accepted as-returned scope.

## Concrete candidate limits for the next integration experiment

These values deliberately define a bounded trial, not guaranteed inventory
coverage. All units below are binary MiB/KiB. They require exact-format measurements
and tests before adoption.

| Scope | Candidate trial ceiling | Reason / unresolved cost |
| --- | --- | --- |
| Per-source page requests | 64, no retries initially | Accommodates advertised 58/63-page tails; future growth can still exceed it |
| One response body | 16 MiB | Wider sample maximum 4.59 MB; JSON memory expansion remains unmeasured |
| Aggregate raw bytes per source | 96 MiB | Finite upper transfer bound; the two long histories were not fully measured |
| Normalized repository YAML | 16 MiB | Consumer stress fixture is 16.38 MB; real tail documents still need exact measurement |
| Physical YAML line | 64 KiB | Preserve existing trial bound; maximum-length scalar CPU still needs measurement |
| Aggregate page attempts per scheduled collection | 900 | Proposed operational allowance, not a claim about current credential quota; must reserve capacity for actual other API calls and honor live limits |
| Aggregate raw transfer per scheduled collection | 1 GiB | Explicit stop bound; neither random sample proves the full inventory fits |
| Source / collection elapsed time | 120 s / 20 min | Candidate initiation and operation deadlines need actual runner validation |

A source budget must reserve its advertised remaining pages against the aggregate
allowance before acquiring them. Check subsequent pagination too; Link counts can
change. Page-count reservation cannot prove byte/time fit. Account failed attempts
against the run budget. Stop acquisition on auth/rate refusals and retain facts.

The aggregate allowance is intentionally below a nominal 1,000-request envelope;
verify the real workflow credential quota and all non-release API calls instead
of inheriting the local credential's observed 5,000-scale remainder. The two
random samples extrapolate to roughly 836 and 1,045 requests respectively; the
pooled sample gives roughly 976. None establishes daily full-inventory feasibility.
The 58/63-page targeted sources make a single normal refresh materially costlier
than one-request-per-source reasoning suggests.

A fixed inventory order risks starving later sources whenever an aggregate cap is
hit. Before integration, implement and test deterministic oldest-successful-check
priority with explicit first-observation handling, and prove retained failures do
not reset that priority. A source whose advertised history exceeds its own ceiling
must be reported distinctly, without wasting its page budget on every attempt.
If fair bounded daily runs cannot keep successful checks within the existing
48-hour installation freshness rule, the trial is unacceptable: revisit cadence,
budget or collection acquisition strategy. Do not quietly alter freshness or
replace full histories with a release window.

## Remaining gates

1. The reader resource experiment is complete: BusyBox RSS grows despite record
   disposal. Stress maximum string lengths, spool limits,
   temporary-storage exhaustion and reader transfer failures before production.
2. Measure the two detected long histories within explicit separate bounds using
   the actual serializer. Determine source bytes, document bytes and runner cost.
3. Inventory-wide page-count evidence or a staged bounded refresh is needed to
   size run budgets and freshness capacity. Samples do not rule out larger tails.
4. Implement local normalization/selection migration only after the budgets and
   scheduling proposal are settled. Review exact source publication and daily
   repin separately. This document authorizes no remote mutation or host delivery.

Evidence: [wider and targeted history probes](yaml-history-outliers-20261103/findings.md),
[original reader experiment](yaml-reader-experiment.md), and ticket 73's memory
follow-up. Natural November 3 run acceptance remains a separate operational task.
