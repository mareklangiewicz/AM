# Choose truthful health summaries and bounded statistics

Type: grilling
Label: wayfinder:grilling
Status: resolved
Assignee: codex-health
Blocked by: 01, 03, 04

## Question

Which public run-summary fields, measurements and bounded historical aggregates
explain health without misleading users or creating a second operational system?

Define successful/failed/unattempted/deferred counts and denominators, source-age
buckets separately from individual release freshness, attempts/redirect accounting,
charged versus received bytes, acquisition versus command/job duration, configured
limits, quota observations, snapshot/history growth and meaningful remaining work.
Identify unavailable measurements rather than reporting invented zeroes.

Specify run identity, timestamps, stop/failure taxonomy, partial success, aborts
without finalization, last reported run versus last publication, history gaps, retention
and aggregate bounds. Show safe examples for success, budget stop, failed validation,
failed publication and abrupt interruption.
Use the consistency model from the contract ticket; do not invent another schema
or strengthen timestamps. Allowlist sanitized public fields, not environment/header
dumps. Decide the few useful initial charts with Marek, measurement definitions
and drill-down links. Feed these semantics into the educational/browser reviews.

## Answer — November 8, 2026

Marek accepted the prepared health semantics, retention and initial views together
with “yes.” The proposal below is the selected contract; its initial pending
wording records its earlier status. Collection, validation and confirmed catalog
publication remain separate outcomes, with explicit unknowns, exact run/attempt
and revision bindings, source/app denominators and scoped measurements.

Retain 64 reported-attempt summaries, complete available source detail for the
latest 8 reported attempts, and 90 daily aggregate records in the current status
tree. Show actual retained ranges and gaps. These are intentional retention bounds,
not source-count truncation or caps allowed to block normal thousands-of-apps
updates. Git history remains distinct from current-tree retention.

The three initial views are source-freshness buckets, measured resource usage
against each run's configured budgets, and separately labelled snapshot/Git-history
growth. Daily aggregates cover reported attempts only. Source freshness does not
replace release freshness; budget charges do not establish received bytes, local
objects do not establish remote storage, and a local candidate does not establish
remote publication. The examples and safe-field/finalization rules below apply.

No latest-attempt completeness, public start record or missing-run service is
introduced. Wire schemas and checks follow in implementation; this decision makes
no runtime, workflow, browser, remote-ref or installed-host change.

## Accepted update cadence — November 7, 2026

Marek replaced the earlier start/finish plan with final-summary-only reporting.
No public start update. Attempt a final summary for every normal outcome, including
collection, validation and publication failures. Abrupt termination or failure to
publish the summary may leave no report. Preserve the previous report's original
timestamps and label it “last reported run”; do not imply latest-attempt coverage,
current running state or complete run history. If there is no report, say so.

Include the specific GitHub Actions run link and a link to recent collection runs
for investigation. Actions may require GitHub sign-in; the public summary must
remain readable without it. No continuous feed, missing-run detector, public
registration or runner-loss recovery service. Detailed counts, enums, timestamps,
bounded report retention and charts remain this ticket's work. Include acceptance
cases for handled collection/validation/publication failures, abrupt termination,
failed summary publication, and an older report alongside a newer catalog.

## Prepared health contract proposal — November 8, 2026

Pending Marek's decision. Reuse the separate status channel and final-report-only
consistency rules. This defines meanings and initial retention/views, not final
wire field names or a new telemetry service. Source inspected at `aa0469367`:
`host_catalog.py` already records source counts, budget charges, acquisition and
command timing, quota observations, source-success ages and local object/tree
metrics. Its report precedes remote publication, so those existing fields cannot
prove remote acceptance. Existing 24/36/48-hour age counters overlap; expose
clearly defined disjoint buckets instead. No fresh operation was measured here.

### Identity, outcomes and denominators

Bind a summary to actual workflow run ID **and rerun attempt**, workflow/source/
policy/schema revisions, input catalog pin, requested scope, observation/evaluation
times and confirmed output pin when available. Keep rerun attempts distinct in
report paths/identity; do not overwrite a prior attempt with a rerun's timestamps.
Use original UTC stage timestamps and monotonic measured durations; identify
measurement scope. A finalizer cannot claim a complete job duration measured
before the job has actually ended.

Report collection, candidate validation and catalog publication as separate stages;
do not reduce them to a green/red verdict that conflates acquired and published
facts. Publication outcomes are confirmed success, confirmed conflict/refusal,
failed before a write, unknown after an ambiguous write, or not attempted. Link
the known confirmed output only after remote evidence. No current-running/idle
assertion. Report overall requested-scope completion only when supported by counts.

Define counts over **distinct numeric sources**, keeping app counts separate:

- Enrolled E: distinct sources in the exact enrollment input. Selected Q: requested
  source scope, at most E; excluded E-Q is intentional out-of-scope work.
- Attempted A: selected sources whose acquisition began, counted once regardless
  of pagination. Successful S: attempted sources whose requested scope and
  source-level normalization/validation/retention succeeded. Failed F: attempted
  sources with a known failed scope. Unknown U: attempted sources lacking a known
  terminal result. When all are measured, A=S+F+U, and selected-unattempted=Q-A.
- Deferred D: the subset of selected-unattempted sources explicitly left because
  of a known stop (quota, byte/request/time budget or handled cancellation).
  Do not add D to unattempted as another population. Failed sources eligible for
  a later retry stay failed for this run. No promised retry/completion ETA.

If evidence is missing, mark the affected counts unknown; do not force these
identities with invented zeros. Successful source collection does not imply its
facts reached the remote catalog. Report catalog-map coverage separately at an
exact pin: published app/source counts and enrollment identities not represented.
Do not count intentionally excluded sources as collection failures or claim a
selected subset is a full-catalog refresh.

Use closed sanitized stop/failure categories: transport/upstream, authentication,
rate/quota, configured request/byte/time budget, identity/schema/source validation,
exceptional document overflow, whole-candidate validation, parent conflict,
publication transport and internal/unknown. State stage and whether remaining
sources were unattempted. No arbitrary exception strings or environment dumps.

### Measurements and freshness

Show configured budget/profile values beside measured usage. Count transport
attempts including explicit redirects (if any), separately from pages and distinct
sources. Saved replay has zero HTTP attempts; original response sizes/receipt
times are saved evidence, not new network usage. Charged transfer allowance and
actually received body bytes are distinct; incomplete instrumentation means
received bytes unknown, not equal to a conservative charge. Quota values identify
resource and observation/reset time; never present the last response header as
current remaining quota or assume the historical 5,000 allowance.

Separate acquisition, collection/validation command and publisher durations.
Give memory measurements their process/scope and units when measured; otherwise
unavailable. Separate current YAML tree/largest-document bytes, local object-store
bytes, local history-guard accounting, fetched bytes/depth and consistently packed
reachable-history bytes. Unmeasured remote GitHub storage remains unknown.

For source freshness, evaluate last successful source-scope times at a stated
catalog pin and UTC evaluation time. Use disjoint buckets: <24h, 24–<48h, >=48h,
no successful collection, and invalid/unknown time. These are descriptive source
buckets, not a replacement for selected-release observation ages or an automatic
48h system-health verdict. Keep failed refresh context visible while last-good
facts remain usable. Meaningful remaining work is known selected-unattempted and
known missing coverage; no guessed backlog across unreported attempts.

### Retention and initial views

Recommend keeping the **64 most recent reported-attempt summaries**, full per-source
final detail for the **8 most recent reported attempts**, and **90 UTC daily
aggregate records** in the current status tree. At twice-daily cadence these
correspond roughly to 32 days of summaries and four days of detail; manual runs,
reruns and missing reports change that coverage. Display actual retained time
ranges and gaps, never a promised number of days. A retained attempt's detail
includes every source outcome available for its supported scope, including
thousands; no first-500/1,024-file truncation. Size transport/parsing safeguards
for that scope with headroom, rather than dropping ordinary detail to fit them.

Prune oldest records during a successful status update; preserve a valid latest
summary and root references. Detail removal is explicit in retained coverage, not
an implied successful/absent attempt. Keep current daily aggregates recomputable
from retained summaries where possible; preserve older bounded aggregate records
with their coverage/method rather than pretending all their details remain.
Daily totals describe only reported attempts, never complete Actions activity.
Do not interpolate gaps, call a missing day zero attempts, or invent success.
Old Git commits remain historical metadata; pruning the current status tree does
not purge Git history. Measure status history churn in the shared capacity work;
no automatic rewrite or separate archive service.

Recommend three initial views: (1) source-freshness buckets at the chosen catalog
pin; (2) reported-run request/charged-byte/acquisition-duration usage against each
run's actual configured budgets; (3) separately labelled tree and measured Git
history growth over reported runs. Keep unknowns/gaps visible and link points to
retained summaries/detail when present, otherwise explain removed detail. A small
run outcome/count table accompanies these; no extra dashboard metrics or charts
until they answer a concrete question. Layout remains the browser ticket's work.

### Required examples and finalization behavior

| Case | Truthful public result |
| --- | --- |
| Full requested-scope success and confirmed publication | All known counts/stages, exact resulting C; full-catalog completion only if Q=E and all selected sources succeeded. |
| Budget stop after partial collection | Actual S/F/U and selected-unattempted/deferred counts, stop/budget context; publication stage shown independently. This is a partial update. |
| Source failure with prior facts | Failed scope and retained prior source freshness; other successful sources may publish. |
| Whole-candidate validation failure | Candidate refused, catalog not published, acquired successes labelled as acquired only; old catalog remains usable. |
| Confirmed parent conflict | Publication refused; no merge/retry. The remote catalog may have advanced independently. |
| Ambiguous publication transport | Unknown outcome, no fabricated confirmed output pin. |
| New catalog published, status publication fails | Previous S remains the last reported run with original times; a reader of newer C sees confirmation lag. |
| Missing candidate/report artifact but finalizer runs | Only known workflow/stage failure facts; source outcomes/counts unknown. |
| Abrupt termination without finalization | No required public record; old last-reported timestamp remains, with specific/recent Actions investigation links. |

Public summaries and safe per-source detail use a closed field allowlist. No
credentials, raw headers, arbitrary diagnostics or local paths. Root S binds the
status schema set and identifies actual retained summary/detail/aggregate coverage;
no document embeds its own enclosing commit. Finalization attempts status after
normal failures without requiring catalog advancement. Source-attempt explanations
join C only under the accepted exact input/output and numeric-identity rules.

Decision requested: accept these measurement meanings, 64/8/90 current-tree
retention and the three initial views as one small health contract. These are
intentional report-retention choices, not caps that block a normal full update.
Field names, ordinary parsing safeguards and focused fixtures follow in implementation.
