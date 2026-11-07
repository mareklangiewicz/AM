# Agree system acceptance and implementation roadmap

Type: grilling
Label: wayfinder:grilling
Status: claimed
Assignee: codex-roadmap
Blocked by: 02, 03, 04, 05, 06, 07, 08, 09, ../../catalog-pages/issues/04-agree-delivery-and-acceptance.md

## Question

Do the accepted decisions now form an understandable, testable system spec and
a dependency-linked implementation route with no unowned choices before execution?

Consume the browser's accepted layout/education/acceptance decisions rather than
selecting a layout here. Set measurable desktop/mobile/keyboard/accessibility,
loading/search/parse/render, capacity/history and recovery targets with Marek,
using observations and named fixtures rather than invented performance claims.

Specify meaningful checks for interruption/resume, budgets/quota/redirects,
isolated failures, fairness/backoff, malformed/schema input, exact-parent races,
identity/retained-release/observation preservation, browser success/partial/failed/
stale/unknown states, correct recipe links and bounded summaries/history.
Require real browser verification for browser claims; no repeat of expensive
unrelated suites without reason.

Consolidate the brief into a reviewable final spec referencing each owning decision.
Create implementation tickets only now, with prerequisites, behavior acceptance,
bounded measurements and concrete push/publication gates. Include an educational
comprehension review: can a newcomer distinguish catalog coverage, AM support,
upstream assets, freshness and authenticity, and can a maintainer explain/resume
the supported pipeline from one short overview? Stop planning when the route is
clear; do not execute the roadmap in this ticket.

## Process steering — November 7, 2026

Prioritize a fast migration with less ceremony, as Marek explicitly requested.
Consolidate a short implementation route and the necessary behavior/compatibility
checks; reuse passing evidence unless changes invalidate it. Agents choose routine
parameters and bring material decisions together for review. Do not add speculative
benchmarks, infrastructure or approval rounds. Deployment remains separately authorized.

## Capacity acceptance input — November 8, 2026

The [accepted capacity target](05-choose-scalable-snapshot-and-history-storage.md#accepted-capacity-target-normal-full-catalog-updates--november-8-2026)
is routine full-catalog updates at thousands of apps without predictably hitting
internal safeguards. Specify representative app/source counts, release/asset
variation, history horizon, refresh objective and operating headroom in the final
roadmap. Reassess existing defaults instead of making their current values mandatory
acceptance ceilings. Include an appropriately scoped scale check after the initial
saved 500-source rehearsal; identify synthetic data and do not present it as real
acquisition or verified enrollment. Keep actual service/host constraints explicit.
A normal budget stop with sources left untouched cannot count as a completed full
refresh. Choose a small useful set of checks, not a new lengthy approval sequence.

## Readiness check and prepared sequence — November 8, 2026

System decisions 02–09 are accepted. This ticket stays open and blocked by browser
04, which still depends on the existing claimed browser 03 experience review.
Do not resolve either browser decision here or create implementation tickets before
its input arrives. No runtime/capacity/browser acceptance is inferred from planning.

The accepted cutover plan supplies this short sequence for the final roadmap:

| Slice | Depends on | Required result |
| --- | --- | --- |
| Shared format-3 contracts/readers and collect/validate interface | Accepted system contracts | Lossless common-fact round trips, exact identity/observation/encoding and unknown/version refusal fixtures; explicit intentional retention/selection differences. |
| Incremental candidate/publication and final health path | Shared contracts and interface | Pinned parent/rule validation, source isolation, explicit publication/confirmation, truthful final reports on normal failures and safe transferred evidence. |
| Main-owned browser/health integration | Accepted browser experience and delivery targets, shared contracts | Preserved A/B/C exploration and native/Vim operation, contextual education and exact recipe links; real fetch/DOM/mobile/accessibility checks. |
| Scale/compatibility and rollback rehearsal | Shared pipeline and browser integration | Saved seed plus three update cases, representative thousands-of-apps/source variation and history growth, dual-output cost, checked old-pin/site recovery. |
| Reviewable rollout package | Passing relevant checks and final acceptance | Exact source/policy/schema/candidate pins, measured settings/margins and consumer inventory; explicit push/publication/Pages authorization before activation. Installed-host delivery remains separate. |

This is a prepared sequence, not implementation tickets or authorization to execute.
Reuse existing evidence where the relevant inputs and behavior are unchanged.

Remaining measurable choices for the final review: representative app/source count
and large-asset cases; full-refresh completion objective under actual quota/runner
constraints; history horizon and resource margin; browser loading/search/parse/render
and mobile/keyboard/accessibility targets from browser 04. Set useful values from
named fixtures/measurements rather than perpetuating old caps or inventing claims.
The browser review also owns stable/nightly grouping, lazy-search disclosure and
empty/stale/partial/error states. A final educational check must verify that users
can distinguish catalog coverage, recipe/support evidence, release freshness and
binary authenticity, and maintainers can explain the supported rerun/publication
path from one short overview.

### Browser input update and quota constraint — November 8, 2026

Browser 03 is now resolved: A default, B/C selectable and the first-release
behavior are accepted. Browser 04 is claimed with a concrete pending refresh/error,
performance/accessibility and verification proposal. Earlier readiness notes above
are chronological; the remaining blocker is browser 04 and this ticket's final
system targets, not an unresolved default layout.

A November 8 read-only primary-document check still gives ordinary GITHUB_TOKEN
1,000 requests/hour/repository:
[GitHub REST rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).
This is an external constraint, not an internal cap to lift. Historical observed
5,000 headers do not establish a durable allowance. Before choosing a thousands-
of-distinct-sources full-refresh deadline, account for actual requests/source,
quota reserve, secondary limits and acquisition/validation/publication time.
The two-runs-daily direction and stop-on-quota policy must not be combined with an
unsupported promise that all thousands refresh within one short job. Any needed
cadence/pacing-policy change is an explicit material choice for the final review,
not a silently invented credential entitlement or a new storage backend.

## Final system-target proposal — November 8, 2026

Pending Marek's decision. Browser 04 is now resolved; all prerequisites for this
final planning decision are accepted. Earlier blocked/pending notes above are
chronological. The five-slice prepared sequence remains the proposed route; do
not create implementation tickets until this final decision is accepted.

### Proposed supported workload and refresh objective

Use **5,000 apps and up to 5,000 distinct numeric sources** as the initial
representative scale target, not an enrollment ceiling. Include the saved real
500-source cohort with preserved provenance and deterministic synthetic expansion
for local processing, separately labelled. Exercise 32-plus-stable, rolling-tag
replacement and the largest supported release/asset/document cases; do not
manufacture a thousand-source live qualification from duplicated observations.
Support ordinary full-catalog work without predictable internal cap failures.

Propose **every healthy enrolled source successfully refreshed within 12 hours**
under the documented ordinary quota and the recorded representative workload.
This concerns requested one-page source-scope observation, not full upstream
history or freshness of every unfetched retained release. Upstream/rate/service
failure or dropped schedules must remain visible exceptions, not fabricated
success. Track app/source coverage and actual observations, not only attempt age.

To make that objective feasible without a new credential/service, recommend
**hourly quota-aware oldest-first collection batches**, sized using measured
transport/CPU/Git costs and live documented quota reserves. This explicitly
supersedes the earlier twice-daily scheduled-run target if accepted. Retain one
active collection, manual dispatch, later-run retries, stop-on-auth/403/429 and
no in-run retry/sleep/journal service. A source batch is intentional requested
scope, not a falsely labelled full-catalog update; full-refresh coverage is reached
only when the whole enrolled population has fresh successful source observations.
Ordinary internal limits must fit each supported scope with headroom; normal
batching does not authorize unexpected cap stops or silently skipped sources.

At the documented ordinary 1,000-request/hour allowance and the existing reserve,
thousands of one-request sources cannot all fit in one short acquisition window.
The saved real 500-source run also received 341,439,276 response bytes, so total
full-refresh transfer and per-job request count must both be planned. This is
historical density evidence, not a claim that every future source has that cost.
Actual headers may guide safe pacing, but an observed 5,000 allowance is not the
capacity planning premise. Hourly batches avoid a long-running wait/recovery
mechanism and reuse the maintained oldest-first schedule. If representative
measurements cannot meet 12 hours with the actual quota/host, stop scale rollout
and bring the concrete failed resource assumption back for review; do not claim
qualification or silently reduce scope.

At hourly cadence, the accepted 64-summary/8-detail counts ordinarily cover
roughly 64 hours and 8 hours, not the earlier twice-daily illustrations; actual
reported coverage remains explicit. Keep those accepted counts unless a later
retention decision changes them. The 90 daily records remain daily. Account for
increased publication opportunities/history churn in the horizon below rather
than claiming the cadence change is free.

### Proposed headroom and history acceptance

For configurable internal request/byte/time/document/file/object safeguards,
choose initial values from measured representative normal work with **at least
25% unused allowance** at the measured peak, also considering normal source/asset
variation. This is an engineering sizing margin, not another cap against the
workload. Where host/service hard bounds prevent that margin, reduce per-job scope
or improve processing and verify the full 12-hour objective still holds; changing
normal coverage/refresh guarantees requires an explicit decision. Peak RSS must
be measured for the collector/publisher and included in the recorded runner-memory
profile rather than assigned an unsupported arbitrary ceiling.

Plan **12 months of catalog and status Git-history growth** at the proposed hourly
cadence, including temporary dual-format publication, observation timestamp churn,
64/8/90 current-status retention and realistic stated release/asset change ranges.
Preserve existing history. The seed-plus-three rehearsal is a behavior/short-run
measurement; combine it with saved real observations where available and separately
label synthetic scenarios/annual projections. Do not call the projection a
12-month test or remote server-storage measurement. Report uncompressed tree,
local/fetched objects and consistently packed reachable history separately.

Set warning/review points from that projection early enough to leave the 25%
margin and time to improve processing/packing/settings. A warning does not halt
normal supported updates, erase history or authorize a new backend. A measured
host/service hard limit still stops unsafe publication and preserves last-good
facts. If the projected normal workload would hit a safeguard inside the horizon,
fix the implementation/settings or bring the measured constraint to the final
rollout review; do not accept routine stopping as the design.

### Final route and acceptance

After acceptance, create only five implementation tickets from the prepared table:
contracts/readers/interface; incremental publisher/final health; main-owned browser;
scale/compatibility/rollback rehearsal; exact rollout package. The first two form
the small end-to-end slice; browser work consumes them, and shared rehearsal then
feeds the concrete rollout package. Split further only for an observed independent
need. Each ticket gets exact dependencies, behavior fixtures and necessary checks;
reuse passing unchanged-input evidence instead of repeating historical suites.

Include the full named semantic, failure, pin/race, schema, source isolation,
quota/redirect, reporting-gap, retained-observation, dual-format, actual-browser
and educational checks already owned by the accepted decisions. Interruption may
lose unpublished work; test simple rerun and last-good preservation rather than
resurrecting a checkpoint service. Final acceptance records actual results and
remaining limitations before explicit push/publication/Pages authorization.
Installed-host delivery stays separately scoped. This proposal authorizes no
implementation, acquisition, enrollment, production setting or remote mutation.

Decision requested: accept the five-slice route, 5,000-app/source reference target,
12-hour healthy-source refresh objective with hourly quota-aware batches, 25%
measured headroom and 12-month history planning horizon. The schedule change is
the material amendment; ordinary profile values and fixture mechanics follow
measurements without another sequence of small approval rounds.
