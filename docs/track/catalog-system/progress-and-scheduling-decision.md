# Durable progress and fair scheduling

## Current accepted baseline — November 7, 2026

The accepted recovery scope, including Marek's final-report-only amendment:

1. If a runner dies, the next run may redo its unfinished work. Preserve the last
   published catalog and accept repeated requests instead of building cross-run
   recovery infrastructure. Work acquired but not published may be lost, including
   complete sources from the interrupted run. No separate checkpoint store,
   cross-run response-replay guarantee or durable per-request journal is required.
2. Publish no public start record. Attempt a final public health summary for every
   normal outcome, including collection, validation and publication failures.
   Abrupt termination or summary publication failure may leave no report.
   Keep the previous report with its original timestamp, labelled “last reported
   run”; never imply it describes the latest attempt or current running state.
   Link the report to its specific GitHub Actions run and to recent collection
   runs for investigation. Actions may require GitHub sign-in; reading the public
   summary must not. No continuous progress or missing-run reconciliation service.

Marek then accepted keeping the existing oldest-first batches and retrying failed
sources on a later scheduled run, without automatic retries inside a run.
Use the existing ordering: never-attempted first, then oldest recorded attempt,
then numeric source ID. Use published attempt metadata; no new durable scheduler
journal is required. If an interrupted run publishes nothing, its work may repeat.
Each selected source gets one acquisition attempt for its requested scope per run;
normal pagination is part of that attempt, not a retry. Keep existing budget,
quota-reserve and auth/rate-stop protections. The next scheduled run still obeys
those protections; it is an opportunity to retry, not an unconditional request.
Do not add the old cooldown counters, jitter or retry-state machinery.

Marek also accepted keeping discovery of new apps manually triggered for now;
scheduled runs only refresh explicitly enrolled sources. Discovery produces
reviewable candidates and identity evidence, not automatic enrollment. Keep
manual work explicitly bounded under the applicable budget/quota protections.
No mixed discovery/refresh queue, weighted lanes or fairness counters are needed.
This concerns maintainer source discovery, not visitors searching the app browser.

Marek accepted running only one collection at a time, allowing the active run to
finish when another is triggered. Use ordinary workflow concurrency controls with
no automatic cancellation of the active run; scheduled and manual collection
must share the same exclusion. No custom lease/fencing service or durable job
queue is required. This does not promise execution of every queued trigger;
pending-trigger behavior belongs to the workflow interface, not recovery storage.

Marek accepted stopping a run on an exact-parent publication conflict. Leave the
newer remote catalog intact and let a later scheduled run try again from its
then-current parent. No automatic merge, rebase or publication retry loop is
required. Unpublished candidate work may be discarded and reacquired later.
A confirmed conflict is a refused publication; an ambiguous network result must
remain unknown unless publication is evidenced, rather than being called a conflict.

Previously published observations stay intact until a new candidate passes
validation and exact-parent publication. A rerun uses actual new response receipt
times; a failed run does not freshen old data. Existing saved-response replay for
explicit local evidence remains useful, without becoming automatic crash recovery.

These decisions supersede both the earlier start/finish reporting plan and the
historical durability/fencing/gate/minute-update design. Recovery/scheduling policy
is resolved; detailed summary fields, storage bounds and workflow interfaces stay
with their owning tickets. The previous 4:1 weighting, cooldowns and 24-hour replay
window are not accepted requirements. This is planning, with no runtime changes.

## Historical superseded design

The separate-store, fencing, durable-replay and weighted-scheduler proposal is
preserved in Git history rather than repeated in this current baseline. It is
not implementation authority. Exact context:

```sh
git show c692bdc99:docs/track/catalog-system/progress-and-scheduling-decision.md
```

The intervening start/finish reporting proposal is also superseded by Marek's
explicit final-summary-only instruction recorded above and in the owning ticket.
