# Agree system acceptance and implementation roadmap

Type: grilling
Label: wayfinder:grilling
Status: open
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
