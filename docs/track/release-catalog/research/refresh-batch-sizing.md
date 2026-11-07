# Larger metadata refresh batches

Assessment for [145](../issues/145-assess-larger-metadata-refresh-batches.md),
November 7, 2026 local time. This is a proposed operating profile, not a deployed
workflow change. The separately authorized 224-source publication is recorded in
[144](../issues/144-publish-224-source-cohort.md).

## Recommendation

Use **up to 500 distinct sources hourly**, at minute 17 UTC (`17 * * * *`),
oldest attempt first, one page of 100 releases per source. Keep requests serial.
500 is a ceiling, not an obligation to make 500 calls when fewer sources are
enrolled. Keep the existing 48-hour **selected-release observation** rule.

The candidate profile needs separate local changes: 512 MiB response bytes/run,
900-second cooperative acquisition budget and a 30-minute workflow timeout.
Keep the 16 MiB/response and 2 MiB/source-document caps, source failure isolation,
rate/auth stopping, retained observations and exact-parent publication. Do not
raise enrollment or reader/history limits merely because the request ceiling
increases. The workflow currently remains at 52 / three hours; this assessment
does not deploy the proposed profile.

Before rollout, record an allowlist of primary rate headers (`limit`, `remaining`,
`used`, `reset`, `resource`), request/response-byte/elapsed totals, and explicit
stop reasons for request/byte/time/rate limits. Check the live budget before
issuing subsequent requests, preserving a 100-request operating reserve shared
with other workflows. An ordinary 500-call run leaves 500 of the documented
1,000/hour allowance before other traffic; the 100-request reserve is our own
policy, not an extra GitHub restriction. Stop rather than retrying immediately
on rate limits; honor reset/Retry-After on resumption. Do not launch overlapping
manual full batches without checking the quota window. No new token is needed.

## Quota basis and actual request accounting

The [official-source research](github-refresh-quotas.md) distinguishes the
workflow's ordinary `GITHUB_TOKEN` allowance of 1,000 REST requests/hour/repository
from a personal token's ordinary 5,000/hour. Our local CLI observations use a
different credential and cannot establish the workflow's live remaining quota.
GitHub does not prescribe 52 repositories per refresh.
[REST quotas](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).

The maintained path makes one serial numeric-ID release-list GET/source, with
embedded release/asset metadata, no latest call, no asset bytes, no routine
identity lookups, no follow-on page and no automatic retry. Apps sharing a source
share a request. Git publication is separate from those release REST GETs.
For the currently enrolled 224 sources, the 500 profile would make 224 normal
release GETs. Identity discovery and local CLI operations are separate traffic.

Most GETs cost one secondary point. The documented secondary ceilings include
900 REST points/minute, 100 concurrent requests and server CPU limits; endpoint
costs and additional controls may be undisclosed. Serial operation with at most
500 requests/run stays below the ordinary 900-point count even if a small-response
batch finishes inside a minute, but does not guarantee exemption from secondary
enforcement. A compulsory one-second sleep per read is not GitHub's documented
rule; its one-second guidance concerns many mutative calls. Retain serial calls
and respond to actual rate signals.
[Quotas](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api),
[best practices](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api).

## Measured corpus and local bounds

The latest saved body for each of the 224 verified repositories totals
179,239,534 bytes: mean 800,176 bytes, median 320,308 bytes, 95th-percentile order
statistic 3,011,807 bytes and largest 6,071,759 bytes. A mean-scaled 500-source
batch is about 400 MB; the deterministic fixture below totals 411,527,373 bytes.
This is why changing only `REQUEST_CAP` fails. These are saved-response
measurements, not new transfers or a representative sample of every future app.

[Replay driver](refresh-batch-replay.py) cycles the saved real bodies into distinct
**synthetic** repository identities. It exercises the maintained normalization,
retention, distributed YAML validation, full prior read, Git publication and
exact-parent checks under a 1 GiB process address-space limit. It does not verify
500 upstream identities or measure HTTP, Actions setup/fetch time, browser use,
server CPU, or broad-source diversity. No fixture identity is enrolled.

With a 500-request ceiling but the current 96 MiB / 300-second budgets, only
104 sources succeed. The 105th response crosses the shared byte allowance and
records a failed attempt; 395 sources are unattempted. Actual charged response
bytes are 100,663,297. Collection/candidate validation takes 40.65 seconds, first
publication 0.77 seconds and retained-prior read 58.99 seconds; peak process RSS
is 136,908 KiB. The local guard, rather than GitHub quota, stops this run.

With 512 MiB / 900 seconds, the 500-source fixture completes initial collection,
publication, a full retained-prior read, and a second 500-source retained refresh
and publication. Both exact pins have 500 successful source documents and the
same app/source identities, release records and effective observations. YAML
totals 74,963,368 bytes. The two-publication experiment takes 659.04 seconds,
peaking at 611,900 KiB process RSS under the 1 GiB address-space limit. This is
not a single live workflow timing: HTTP and Actions setup/fetch are excluded.

The initial replay's final whole-tree equality oracle fails because all 500
`collection.attempted_at` values legitimately advance. Both publications had
already completed. An independent exact-pin comparison confirms that **only**
that field differs, with all identities, records, observations and successful
statuses preserved. The raw failed receipt is retained, rather than relabeled
as a clean first run. The driver now compares retained facts and identities,
and passes evidence mode explicitly so saved receipt times also supply attempt
times. A four-source end-to-end check of the corrected driver passes; the costly
500 normalization/publication experiment was not repeated. Six batch regressions
pass, including byte exhaustion, rate stopping, failed transfer accounting,
retained data and the named acquisition-budget boundary. No full-suite rerun is
claimed for this behavior-preserving extraction of the existing 300-second
literal into `ACQUISITION_SECONDS`.

The maintained **whole main command** also passes on the actual enrolled
228-app / 224-source configuration and exact final published parent
`26d82aa94bb5a8f70449e42500dc78a597583ab3`, using `batch_size=500`, the proposed
512 MiB / 900-second overrides and unchanged document/history bounds. All 224
sources succeed in one command, zero pending apps: 179,239,534 response bytes,
126.35 seconds including prior read/collection/validation/publication/reporting,
284,692 KiB peak process RSS under 1 GiB. It excludes initial local Git transfer,
HTTP and CI setup. Saved bodies have explicitly synthetic receipt times; this
does not claim fresh live observations. This qualifies the local request profile
against today's enrollment, not 500-source published-history capacity.

[Portable validation receipt](refresh-batch-validation.json) binds the measured
corpus, raw/verified results, scripts and source hashes. Raw evidence and local
Git repositories remain under
`/home/marek/Documents/Codex/am-refresh-sizing-20261107/`. The initial fixed-path
driver is preserved there alongside the generalized committed driver.

A separate direct call to the real publisher confirms the 750-source fixture's
next unchanged snapshot is refused with `history_bound`, leaving its ref intact:
111,717,518 snapshot bytes + 20,587,206 existing object bytes = 132,304,724,
over the 128,000,000-byte local cap. It is not a GitHub error. The additional
750-source exploratory run also ends at that guard (988.06 seconds / 715,988 KiB
peak process RSS). Its second loop used a fixed saved receipt time older than
the later attempt, so it is not accepted as a clean retained-observation test;
the independent identical-tree publisher probe isolates the history boundary.

The current publication verifier's actual object layout contains 63,288,158 bytes.
Adding the 500-source fixture's 74,963,368-byte tree totals 138,251,526 bytes;
the real publisher likewise refuses before writing, and verifier refs stay intact.
This measures that verifier's fetched/loose-object layout. A fresh local Git
transfer of exact final published history separately uses 55,312,540 object bytes;
with the same fixture it totals 130,275,908 and again provably refuses with
`history_bound`, leaving the ref intact. GitHub Actions' fresh packing still need
not use identical bytes. Its fresh-run measurement and retained-growth headroom
are required before choosing a revised history allowance. Merely
passing the 500 fixture in a new empty repository cannot qualify it against the
published catalog's accumulated history.

## Schedule, broad coverage and freshness

The already-recorded source scan at `f657f4d7876f0164b6705795527f5a33738d0f73`
contains 6,732 candidate app identities and **6,504 distinct repository names**
after case folding. Those names are not verified numeric identities: aliases may
collapse, some sources may fail review, and unsupported bindings may add others.
The scan digest is
`3bca3fe2989a648f64bfbfa04fa505b44c2501b79003af4543f2c9d9396cbc6e`.
This uses the existing scan, rather than repeating identity collection.

| Scope | 52 / three hours | 500 / three hours | 500 / hour |
| --- | ---: | ---: | ---: |
| 224 sources | 15 h | 3 h | 1 h |
| 500 sources | 30 h | 3 h | 1 h |
| 4,000 sources | 231 h | 24 h | 8 h |
| 6,504 candidate names | 378 h | 42 h | 14 h |

These are successful full-batch rotation arithmetic, `ceil(N/B) × interval`,
not measured storage capacity or a freshness guarantee. The 14-hour target
allows three nominal rotations in 42 hours; 42-hour rotation leaves only six
hours for delay/failure. Prefer a <=24-hour nominal cycle, with actual oldest
successful in-scope observations monitored before they reach 48 hours: warn at
24 hours and escalate at 36 hours. Track retained observations outside page 1
separately; they are not evidence of a recent in-scope collection. Budget truncation
reduces effective B, so report actual success throughput and rotation age.
An outage lasting long enough still makes clients refuse stale records.

GitHub may delay or drop scheduled runs. Minute 17 avoids the documented
start-of-hour concentration, but cron remains best effort; public-repository
schedules can disable after 60 days without activity. The repository's checked
default branch is `main-marek`, matching the workflow.
[Schedule rules](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

Refreshing page 1 does not reobserve retained releases outside its 100-release
window. A client selecting one of those records may still refuse it as stale.
Such sources need explicit deeper or targeted collection, with its extra requests
counted against the same quota and byte/time budgets. Increasing B or changing
the cron must not stamp all retained history fresh. ADR 0002 remains binding.

## What prevents simply going larger

750 requests is not forbidden by the primary quota, but leaves only 250/hour
before other traffic and recovery; 1,000 spends the entire ordinary hourly
allowance. Undisclosed secondary enforcement and response latency remain real
upstream constraints. 500 leaves useful quota headroom without relying on 304s.

The present enrollment ceiling is 224. The reader permits 1,024 files, of which
one is the app map: at most 1,023 source documents, independently of batch size.
Local publication also requires existing object bytes plus the uncompressed next
snapshot to fit 128,000,000 bytes. Snapshot reads/writes materialize and validate
the whole catalog each run; network batching does not remove this work. These
are project constraints, not GitHub quotas. Broad coverage needs a separately
measured snapshot/history design before enrolling thousands of sources.
The 16 MiB raw-response and 2 MiB retained-document limits can also refuse an
individual dense or growing repository; a larger batch cannot fix that source.

GitHub's separate repository-health guidance recommends keeping generated files
outside Git, compressed `.git` at most 10 GB, directory width at most 3,000 and
single objects at most 1 MB; the latter are recommendations, not these project
guards. It enforces 2 GB pushes and 100 MB objects. Its large-file guidance is
stricter about healthy repository size: ideally below 1 GB, strongly recommends
below 5 GB. A 75 MB snapshot spread across small files does not hit the 100 MB
per-file block, but repeatedly retained generated history and a flat directory
of thousands of source files deserve redesign before broad deployment.
[Repository limits](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits),
[large-file guidance](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

Conditional GETs can reduce transfer and primary quota when unchanged (authorized
304s do not consume primary quota), but the current collector has no conditional
cache. A correct implementation must persist the membership of the previous
requested page and refresh observations only for those records on a 304, leaving
retained records outside that page untouched. Do not budget on a hoped-for cache
hit rate or weaken per-release freshness.
[Conditional requests](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api#use-conditional-requests-if-appropriate).

For this request, 500/hour is a proposed metadata-throughput profile. It does not
claim that the current full-snapshot store already supports the 6,504-name queue.
