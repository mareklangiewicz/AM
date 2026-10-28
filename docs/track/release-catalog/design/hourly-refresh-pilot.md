# Reviewed hourly freshness pilot

Ticket [35](../issues/35-prepare-hourly-refresh-pilot.md).
Review targets: [proposed workflow](catalog-schedule.yml.proposed),
[controller](../../../../tools/catalog-collector/scheduled_dispatch.py),
[offline checks](../../../../tools/catalog-collector/test_scheduled_dispatch.py).
Preparation below is historical. Marek approved activation; schedule/controller
were pushed at 466e1facce4e66d4b26c06446fc1e524aa0d76df and armed for
2026-10-28T00:12:16Z through exclusive 2026-10-29T00:12:16Z. See
[activation record](../research/hourly-pilot-activation.json) and
[ticket 36](../issues/36-activate-hourly-refresh-pilot.md).

## Decision proposed for approval

Enable hourly dispatch at minute 17 UTC for one 24-hour window, same six enrolled
sources only. No app operations or source expansion. This explicit pilot approval
would replace the per-manual-dispatch approval requirement only for the scheduled
runs within this window, with the budgets and controls below. It would not approve
an indefinite schedule, retries, arbitrary source updates or future rearming.

An hourly pilot leaves substantial headroom under the reader's 24-hour freshness
limit, but is not a freshness SLA. Default branch was checked live as main-marek
on 2026-10-28, correcting the older historical main-default observation.
GitHub schedules run on the default branch; they may be delayed/dropped and public
repository schedules can be disabled after 60 days without activity. See
[GitHub schedule semantics](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).
Minute 17 avoids the documented start-of-hour load peak; it does not guarantee
execution. Built-in GITHUB_TOKEN can create workflow_dispatch runs, an explicit
exception to normal token recursion suppression; see
[GitHub triggering rules](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow#triggering-a-workflow-from-a-workflow).

## Small dispatcher, existing collector unchanged

Install the proposed file as .github/workflows/catalog-schedule.yml only after
approval. It checks out exact github.sha with the existing pinned action, then
runs the reviewed controller using contents:read/actions:write. That token can
manage Actions in this repository; it is not a contents writer or upstream
transport credential. This is additional repository-scoped Actions authority,
constrained by reviewed controller code rather than a branch-scoped token.

The existing catalog-collector.yml, adapter, six-source manifest, collector and
publisher are unchanged. Controller submits one ordinary workflow_dispatch with
exact approved source SHA, fixed manifest digest and freshly resolved full prior.
A source/ref race refuses in the existing collector before upstream collection;
a publication race refuses at exact-prior fetch or normal fast-forward push.
Controller never substitutes the actual schedule event as manual evidence: the
child workflow genuinely receives a workflow_dispatch event.

## Guards and budget

- Fixed repository/main-marek, exact cron, run_attempt=1, exact current source and
  workflow SHA equal a separately configured approved revision.
- Three repository variables: CATALOG_SCHEDULE_REVISION, CATALOG_SCHEDULE_START
  and CATALOG_SCHEDULE_UNTIL. Start/until are UTC Unix seconds, at most 86,400
  seconds apart. Source pushes stop future dispatch until separately repinned;
  missing/expired/malformed configuration refuses before any control API request.
- Refuse changed default branch, unexpected active workflow, a recently listed
  non-completed collector run, or an observed count of 24 collector runs since
  start. Counts include manual runs conservatively. Recent-run listing is an
  overlap optimization, not proof against arbitrarily old jobs. Existing collector
  concurrency and exact-prior checks remain authoritative. GitHub API list
  consistency/external actors are assumptions of the observed-count guard; this
  is not a server-enforced dispatch quota.
- A second wall-clock check refuses a dispatch if API reads consume the remaining
  window. No retry on failed/ambiguous API submission. Hourly ticks are separate
  scheduled opportunities, not automatic same-run retries or recollection to
  obtain particular HTTP statuses. Do not manually rerun controller/child jobs.
- Nominally up to 24 ticks and 144 release GET attempts in the 24-hour pilot;
  each successful child can publish one ordinary append-only catalog child.
  Collection retains existing six requests, 8 MB/body, 64 KB/headers, 10-second
  connect/30-second request/300-second batch and five-minute job bounds.
- Each controller makes six control API reads and at most one dispatch command,
  each capped at 30 seconds; total controller timeout five minutes. These plus
  checkout, artifacts, prior/ref Git reads and publication traffic are additional
  to release GETs. Control response length is checked after gh returns, not a
  streaming allocation bound. No new external package or secret is needed.

Observed last full six-body transfer was approximately 4.88 MB: nominal daily
release body ingress is about 117 MB if each tick returns similar full bodies,
not a forecast or upper bound. Worst per-body caps allow 1.152 GB over 24 batches.
Git compression/delta reuse and remote history growth remain unmeasured. Existing
128 MB local shallow-object/candidate bound is not a remote history cap. Do not
raise a bound or rewrite history to keep the pilot running. At the end measure
actual counts, traffic, archive size and full history Git-object growth before
proposing continuation. All-six failure gate preserves prior branch and age.

## Concrete activation sequence after approval

1. Recheck default branch, remote source/publication, active workflow isolation and
   absence of conflicting runs. Refuse drift that changes the review target.
2. Copy the proposed YAML to .github/workflows/catalog-schedule.yml, commit and
   push only reviewed controller/workflow plus supporting records. Record exact
   activation commit SHA. Existing manual collector remains active; unrelated
   workflows stay disabled. No broad repository Actions-settings change.
3. Set start to current UTC epoch and until=start+86400, then set approved revision
   to that exact pushed activation SHA last. Until all values are valid/matching,
   the dispatcher cannot collect. Record exact values and resulting window.
4. Observe the first naturally scheduled run and its child; no extra dispatch for
   testing. Validate source/prior/permissions/artifact/tree/freshness as in ticket
   34. A queued child may complete after window expiry; the window gates dispatch,
   not cancellation of already-submitted work. Each child keeps existing timeouts.
5. At window end disable catalog-schedule.yml, retain artifacts before seven-day
   expiry and assess results. The controller refuses further collection after
   expiry even if disabling is delayed; scheduled controller jobs can still start
   and refuse, so expiry is not removal of the workflow trigger.

Emergency stop: disable catalog-schedule.yml and clear CATALOG_SCHEDULE_REVISION.
An already-submitted child may still finish; cancel it separately if required and
record whether publication occurred. Do not delete/rewrite release-catalog or
change installed apps as a rollback. No source repinning/window extension is
implicit. A source push during the window deliberately freezes further dispatch.

## Verification and limits

Offline tests use fixture context and stub command outputs only. They exercise
exact source/prior forwarding, pre-network context/window refusal, expired window,
rerun refusal, moved source/default branch, unexpected workflows, active child,
observed-count exhaustion, invalid prior and no retry on ambiguous dispatch.
Full suite result is in ticket 35. No real schedule, scheduler token, dispatch or
live scheduled collection has been validated by this preparation.
