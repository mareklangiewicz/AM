# Retained growth and staging — November 4, 2026

Local synthetic experiment; no network requests, production changes, source push,
workflow dispatch, daily repin or host installation. Trial ceilings are not
approved operational budgets. Prototype source/results are committed at
`ccd0273e4` under `tools/catalog-yaml-prototype/` on
`research/yaml-bounded-collector`. Both worktrees are local only.

## Retention and staging

Thirty daily one-page merges, each adding 100 new IDs with eight assets per
release, retain 3,001 releases and grow to 5,002,015 bytes. The untouched initial
release remains stale while the final day's included release is fresh. An exact
5,003,682-byte merge allowance succeeds; one byte less refuses without changing
prior releases or last-success metadata. This is synthetic growth, not an upstream
growth forecast. Default bounded fetching does not bound accumulated retention.

Near the proposed 16 MiB cap, 9,939 retained releases plus 100 fetched IDs produce
16,734,401 bytes from 16,567,661 prior bytes. The staging measurement includes
fixture construction, copies, serialization and output-size calculation; it is
not a transport benchmark or isolated incremental-allocation measurement.
Peak staging RSS is 128,028 KiB in 4.02 s. The thirty-day growth process reaches
64,940 KiB in 13.90 s. The exact-size refusal test is part of that growth process.

The initial staging fixture-count estimate crossed the merge cap and correctly
failed its success assertion. The estimate was reduced before the completed run;
this was a harness sizing error, not a collector regression.

## Method and limits

Run `python3 tools/catalog-yaml-prototype/growth.py` from the prototype branch.
Children run serially under 384 MiB address-space, 55-second CPU, 60-second wall
and 64 MiB per-file limits. The wall watchdog kills the process group. These
limits belong to this measurement harness; they are not integrated collector or
consumer runtime policy. Address space is not an RSS or cgroup-memory guarantee.
The parent builds bounded fixtures but does not run under these child limits.

GNU time records peak RSS/elapsed time. Private spool size is sampled every 10 ms;
this is a lower-bound sample, not a guaranteed peak measurement. Query output and
private spool coexist while validated output is copied. Source fixture storage,
output destination, aggregate temporary storage and publication staging need
separate accounting. Per-file limits do not impose a total-filesystem quota.

Host: Linux 7.0.0-42-generic x86_64; Python 3.14.4, mawk 1.3.4 (20260129),
GNU awk 5.3.2 and BusyBox 1.37.0. These are single-host measurements, not
portable upper bounds.

This does not establish live collection throughput, credential capacity, fair
scheduling, full-history costs, maximum JSON amplification or worst-case Unicode
processing. Selected-release freshness remains per observation, independently
of collection success and publication time.

## Reader results and ceiling decision

The completed pilot (`growth-pilot-results.json`) exercises a 10,668,148-byte
retained document with 6,400 releases on all three tools. It passes, including
malformed-suffix refusal with no output. BusyBox reaches 35,780 KiB RSS and 36.88 s;
mawk/GNU awk remain around 8 MiB. These pilot timings include ordinary host load.

The larger 16,669,349-byte document contains 10,000 releases with eight assets
each. mawk/GNU awk complete the projected query; BusyBox reaches the harness's
55-second CPU ceiling and exits 137 after 55.01 s, with 52,420 KiB peak RSS.
It has accumulated a sampled 871,421-byte private spool but exposes zero query
output. This is a test-limit refusal, not a successful parse or a production
refusal guarantee. The previous 10.67 MB pilot provides its successful smaller
comparison. The reader's own current file-size guard is 32 MiB, not this harness's
16 MiB candidate; no production limit was changed.

| Tool | 16,669,349-byte retained query | Peak RSS (KiB) | Elapsed (s) |
| --- | --- | ---: | ---: |
| mawk | Success; 918,894 output bytes | 7,856 | 10.71 |
| GNU awk | Success; 918,894 output bytes | 7,824 | 22.25 |
| BusyBox awk | CPU-limit refusal; zero output | 52,420 | 55.01 |

A 60,000-asset fixture (10,849,597 bytes) produces 6,528,894 output bytes and a
sampled private spool of that size. All three pass; BusyBox reaches 35,524 KiB
RSS in 37.58 s, versus roughly 8 MiB for the other tools. This shape demonstrates
that projected output/storage can be large even when there is only one release.
The smaller pilot repeats that shape with similar results.

All three pass an exactly 65,536-byte physical title line and reject 65,537
bytes with status 2 and no output. A forced 4,096-byte per-file spool limit causes
all three to refuse (status 153) with zero query output. Near-cap malformed
suffixes emit no output on mawk/GNU awk; BusyBox's completed 10.67 MB pilot also
verifies malformed-suffix refusal, while its larger run stops on CPU before this
check. The final results file contains twenty reader cases; the CPU refusal is an
observed limit, not counted as a successful reader case. Python syntax and
whitespace checks pass. No production code changed.

Decision for the next local trial: keep the 16 MiB retained-byte value provisional,
and do not promote it to a portable reader performance promise. The tested
BusyBox shape already fails this explicit CPU allowance; lowering the file cap,
changing reader strategy or allowing more runtime needs its own evidence and
decision. Do not silently evict retained releases to meet a ceiling. A one-page
source scope does not address this consumer cost.

Production integration still needs enforced collector worker deadlines/memory,
bounded publication staging and total temporary storage, explicit reader/output
runtime limits, and actual default-run capacity measurements. The harness caps
protect this local experiment; they do not resolve those operational gates.
