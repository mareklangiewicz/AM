# GitHub quotas and larger catalog refreshes

Research date: November 7, 2026. Proposal evidence, not an operational rollout
receipt. Scope is release metadata collection, independent of recipe migration
and installed applications. Local implementation inspected at `fde55f598`.

This is the quota sub-assessment. The [combined sizing report](refresh-batch-sizing.md)
uses the existing 6,504-name candidate inventory to prefer **hourly** operation;
the three-hour examples below demonstrate quota arithmetic rather than the final
cadence recommendation.

## Official restrictions

The ordinary Actions `GITHUB_TOKEN` allowance is **1,000 REST requests/hour per
repository**; authenticated personal access tokens ordinarily have 5,000/hour,
while unauthenticated requests have 60/hour. Budget against the workflow token,
not the local CLI credential. Secondary limits include 100 concurrent requests
shared with GraphQL, 900 REST points/minute, and 90 seconds server CPU per 60
seconds elapsed. Most GETs cost one secondary point; undisclosed endpoint costs
and other secondary restrictions exist. Response `x-ratelimit-*` headers describe
the live primary budget; secondary remaining capacity cannot be queried. These
limits are not a documented maximum number of repositories per catalog batch.
[GitHub REST rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).

GitHub recommends authenticated serial calls, efficient fixed-schedule polling
when webhooks are unavailable, and conditional GETs. An authorized unchanged
`304` response does not consume primary quota. Rate errors require respecting
`Retry-After`, or a depleted budget's reset; otherwise wait at least a minute,
then use bounded exponential backoff. The one-second pause guidance concerns
large numbers of mutative requests, rather than a mandatory delay after every
metadata GET. Pagination should follow response links.
[REST best practices](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api).

List-releases pages contain at most 100 releases. Published releases are public;
draft visibility depends on access. The documented response includes release
assets and download URLs, so reading the listed asset metadata does not itself
require downloading binaries or one API call per asset. This endpoint does not
list ordinary tags without releases.
[Release endpoint](https://docs.github.com/en/rest/releases/releases#list-releases).

Scheduled Actions can be delayed or dropped under load. GitHub recommends
avoiding the start of the hour; schedules use the default branch, require its
workflow file, and have a five-minute minimum interval. Public-repository
schedules disable after 60 days without repository activity. Cron is therefore
not a hard freshness SLA.
[Schedule documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).
GitHub-hosted jobs may run for six hours; the project's ten-minute job timeout
is substantially stricter.
[Actions limits](https://docs.github.com/en/actions/reference/limits).

## Actual current traffic and project limits

`.github/workflows/catalog.yml` passes `github.token` as `GH_TOKEN`, runs at
minute 17 every three hours, and invokes `host_catalog.py --batch-size 52`.
Publication uses Git fetch/push, rather than one REST write per source.

`host_catalog.py` selects distinct numeric repository IDs in oldest-attempt order.
Each selected source normally makes exactly one serial GET of
`/repositories/{id}/releases?per_page=100&page=1`. Apps sharing a source share that
request. There is no routine identity lookup, per-asset metadata request, asset
payload download, ETag request, follow-on pagination, or retry in this path.
The code stops subsequent requests on HTTP 401/403/429. Raw rate headers are not
currently reported. Local preparation/discovery requests and CLI inspection
are separate traffic, with the credential actually used determining their quota.

The following are project safeguards, not GitHub quota values: 52 attempts/run,
224 enrolled sources, 96 MiB input/run, 16 MiB/response, 300 seconds collection
loop, 30-second transport timeout, 2 MiB/source YAML, ten-minute workflow timeout,
and whole-snapshot Git/document/history bounds. Increasing requests alone does
not qualify transport, snapshot processing or publication for 500 sources.
The collection time check is cooperative and precedes each source, rather than
a hard whole-command deadline. Readback/validation and Git operations add time.

## Candidate sizing and freshness arithmetic

These are deductions from the documented quota and current request pattern,
not GitHub performance guarantees. Count all REST overhead, redirects and retries
against the live budget; reserve capacity for other workflows sharing it.

| Candidate | First-page release GETs | Ordinary token allowance left before other usage | Nominal rotation at three hours |
| --- | ---: | ---: | --- |
| 52 | 52 | 948 | `3 × ceil(N/52)` hours |
| 224 | 224 | 776 | `3 × ceil(N/224)` hours |
| 500 | 500 | 500 | `3 × ceil(N/500)` hours |
| 750 | 750 | 250 | `3 × ceil(N/750)` hours |

A **500-source ceiling every three hours** is a sensible quota candidate: it
uses half the ordinary hourly allowance even if every response is changed.
The present enrollment would make only 224 requests. Avoid two full 500-request
manual runs within the same quota window; they leave no overhead reserve.
For manual completion, use live response headers and wait for reset when needed.
750–900 is not prohibited as a batch count, but spends the failure/retry reserve
and needs stronger runtime and live-quota evidence. Conditional caching can
reduce normal usage but should not justify a quota plan that fails when every
response changes.

At 500 sources/run and three-hour cadence, 3,000 sources rotate in 18 hours,
4,000 in 24 hours, and 5,000 in 30 hours. A 24-hour nominal rotation target leaves
one additional nominal rotation within the 48-hour freshness window; 8,000 in
48 hours leaves essentially no allowance for delay or failures. These arithmetic
capacities are not enrollment authorization or validated snapshot capacities.
52/three-hours instead reaches only 416 sources in a 24-hour nominal rotation.

For `N` enrolled sources and `B` successful attempts/run, nominal cycle time is
`ceil(N/B) × interval`. Failed attempts, skipped sources, dropped runs and source
errors worsen actual freshness. The client checks the selected release's own
observation age: retained releases outside page 1 do not become fresh when the
source's first page is refreshed. A larger source batch cannot eliminate this
partial-history limitation. Preserve ADR 0002's observation semantics.

## Validation and operational gates

1. Measure actual saved and fresh response bytes/time, including worst observed
   sources and whole-command snapshot work. Current 96 MiB budget permits only
   about 197 KiB/source on average for 500 sources; actual source distribution
   decides whether it fits. Do not silently relabel budget truncation as a full
   500-source refresh.
2. Replay 500 distinct representative source documents with retained history
   through the real collector/publication command under explicit memory/time
   bounds. Duplicated fixtures test mechanics, not broad upstream diversity.
3. Add live safe rate diagnostics and preserve stop/backoff behavior. Capture
   actual `limit`, `remaining`, `used`, `reset`, request count, bytes, duration,
   attempted/succeeded/unattempted counts; never log credentials.
4. Use serial requests, initially with an explicit conservative request-rate
   target, then measure; no official requirement forces concurrency to achieve
   500. At one request/second, 500 calls alone require about 8.3 minutes before
   payload/processing overhead, exceeding the current five-minute loop budget.
5. Validate one full enrolled-scope Actions run and exact-parent readback before
   treating local replay as CI capacity evidence. As enrollment grows, alert on
   actual selected-observation ages and failed rotations; cron arithmetic alone
   does not establish the freshness requirement.

Quota research supports trying 500. Actual restrictions preventing more work
per refresh are presently the project's response/time/snapshot bounds and
unmeasured full-scope CI behavior, plus the 1,000/hour token budget and dynamic
secondary enforcement. Preserve independent bounds until measurements justify
explicit changes. If a future enrollment exceeds the measured snapshot budget,
changing batch size or cron cannot by itself fix whole-snapshot materialization.
