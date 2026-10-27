# Release catalog exploration

## Notes

Work in Marek's active AM fork, on main-marek. Goal: find a simple reliable approach, evolve it through experiments, then propose it upstream. This map and tickets are intentionally tracked by Git.

Earlier work: [2026-10-20 design and measurements](../../design/version-catalog.md), with throwaway code on proto/release-catalog in tools/proto-catalog/. Preserve that branch and its evidence. The earlier design combines a GraphQL collector, CI version selection, and a generic installer. The newer direction separates upstream observations from app-specific selection and leaves selection on the client. Neither is immutable policy.

## Decisions-so-far

- [01: prior research reconciled](issues/01-reconcile-prior-work.md): retain useful measurements, but distinguish the earlier resolved catalog from the current observation catalog. The reported 825-point sweep is GraphQL evidence, not a REST response-catalog capacity measurement.
- Working direction: collector preserves upstream metadata without ranking releases or selecting downloads; app scripts keep policy. Public upstream metadata is not independent binary authenticity.
- Explore a dedicated AM publication branch, hourly collection, reviewed endpoint inventory, retained observations on temporary failures, per-observation checked times, explicit stale-data acceptance beyond 24 hours, and selective client downloads pinned to a publication commit.
- Exact REST snapshots are the provisional direction after the baseline/hour sample. The day sample is optional; retain the six-endpoint, short-window limits on any storage conclusions. Reconsider representation with broader evidence or new consumer needs.
- Catalog work does not execute the active app installer or installed updaters. Existing app management behavior remains unchanged during experiments.

## Fog

- [06 resolved](issues/06-manual-rest-churn-experiment.md): baseline/hour measurements support provisional REST-first work; day sampling is optional. Fleet storage remains unmeasured.
- [08 resolved](issues/08-offline-storage-prototype.md): 64 offline replay checks support the bounded format/state/publication contract; [09 resolved](issues/09-review-offline-findings.md) records review refinements; [10 resolved](issues/10-offline-client-freshness.md) verifies bounded freshness/consent; [11 resolved](issues/11-review-client-and-collection-boundaries.md) accepts the initial policy/direction; [12 resolved](issues/12-offline-restricted-collector.md) implements the offline core; [13 resolved](issues/13-prepare-adapter-and-enrollment-review.md) prepares that review; [14 resolved](issues/14-offline-supervised-transport.md) implements the adapter offline; [15 resolved](issues/15-review-adapter-and-stage-manifest.md) staged the reviewed run package; [16 resolved](issues/16-first-supervised-live-validation.md) validates its first live six-route baseline after approved SQLite enrollment.
- [04 resolved](issues/04-compare-collection-strategies.md): REST-first experiment agreed; revisit the representation if churn/storage evidence or future consumer needs justify it.
- Retention and Git growth; volatile response fields; large asset lists; removed upstream data; standalone updater migration; actual publishing privilege separation; eventual upstream preferences.

## Progress

2026-10-27: read prior design and prototype source without checking out the prototype branch. Prepared a bounded sh/curl/jq workflow-token probe, using only read permissions and retaining public responses and quota headers as a seven-day Actions artifact. Default branch on GitHub is main while live development is main-marek, so the probe also has a narrowly scoped main-marek push trigger. Publishing/running requires the approved push; no schedule is enabled.

2026-10-27: fc0e2be7d pushed to origin/main-marek with Marek's approval. Probe did not appear in run/check listings or the public workflow registry. [Ticket 02](issues/02-workflow-token-probe.md) is open with ready-for-human triage pending a signed-in Actions configuration check. No runtime quota measurements yet.

2026-10-27 correction: gh works with keyring access outside the sandbox. It confirmed Actions is disabled repository-wide (enabled=false), while the five existing workflows are individually active. Marek requires manual-only experiments. Removed the probe push trigger and added a manual-event job guard; keep repository Actions disabled pending an approved isolation/registration plan. Earlier push-trigger and signed-in-browser suggestions are superseded.

2026-10-27: [03 resolved](issues/03-inventory-release-requests.md), with [measured inventory](research/request-inventory-findings.md): 8,337 literal release URLs, 164 unresolved dynamic occurrences, 1,559 shared URLs across architectures. Daily polling averages 347.4 REST calls/hour before overhead, so a full hourly sweep is not required by the 24-hour target. Existing classifier counts reproduced. Prepared local one-file registration commit 43cceedf7 without checking out or merging main. [05](issues/05-isolate-and-register-manual-probe.md) records the proposed isolation/enablement plan; all Actions settings remain unchanged.

2026-10-27: with Marek's explicit approval, changed fork default to main-marek via gh. GitHub immediately registered Catalog quota probe (398162689). This supersedes the main-branch stub plan; main was not modified. Actions remains disabled, and no experiment was dispatched. Updated [05](issues/05-isolate-and-register-manual-probe.md) with the remaining isolation/enablement steps.

2026-10-27: [05 resolved](issues/05-isolate-and-register-manual-probe.md). Disabled all five unrelated workflows, verified isolation while Actions was off, then enabled Actions and verified the probe is the sole active workflow and there are no pending runs. No experiment dispatched. [02](issues/02-workflow-token-probe.md) is ready for an explicitly authorized manual run.

2026-10-27: [02 resolved](issues/02-workflow-token-probe.md). Authorized run 40496182929 succeeded: real token reads public upstreams, REST 304 did not increase usage, small GraphQL batch cost 1, and both budgets reported 5,000/hour for that run. Final /rate_limit GraphQL counters disagreed with direct GraphQL response evidence; recorded without speculating. [Findings and persistent evidence](research/probe-run-40496182929-findings.md). No extra run; unrelated workflows remain disabled. [04](issues/04-compare-collection-strategies.md) is now unblocked.

2026-10-27: [04 claimed](issues/04-compare-collection-strategies.md); [strategy comparison](research/collection-strategy-comparison.md) records matched-coverage payload measurements, compatibility limits and a proposed three-observation manual REST churn experiment. Awaiting Marek's design decision; no run or push authorized.

2026-10-27: [04 resolved](issues/04-compare-collection-strategies.md) after Marek accepted REST-first measurement. Prepared bounded collection, offline storage/Git/filter diagnostics and manual choices in the existing probe workflow; seven fixture tests and workflow shell/YAML checks pass. [06](issues/06-manual-rest-churn-experiment.md) tracks separately authorized observations and result interpretation. No push or experiment run.

2026-10-27: approved push through 6f9648bb2 and exactly one baseline dispatch. [06 partial result](research/churn-baseline-40499617203-findings.md): run 40499617203 stopped on WezTerm HTTP 301 after four successful responses. Evidence retained; incomplete baseline cannot seed repeats. No further dispatch.

2026-10-27: [redirect investigation](research/wezterm-redirect-investigation.md) captured GitHub's repository-ID destination in one separate public GET. Prepared explicit sample URL and bounded error evidence retention, with eight fixture tests passing; automatic redirects remain disabled. No target read, push or replacement baseline.

2026-10-27: [replacement baseline succeeded](research/churn-baseline-40500475496-findings.md), run 40500475496 at 13:01 Europe/Warsaw, source 37bdb433c. Six HTTP 200 responses; 4.88 MB exact versus 0.62 MB diagnostic body totals. Evidence preserved; next is separately authorized churn-hour with previous_run=40500475496. No churn claim or automatic follow-up.

2026-10-27: [hour observation succeeded](research/churn-hour-40508899451-findings.md), run 40508899451, +63m26s. Six changed HTTP 200 bodies; differences were download/reaction counters only, with stable ordered identities and projections. Packed growth 4,324 bytes exact / 458 bytes projection in this short sample. Next is separately authorized day observation around 2026-10-28 13:01 Europe/Warsaw; no schedule.

2026-10-27: Marek accepted moving ahead without waiting for the day sample. [06 resolved with revised scope](issues/06-manual-rest-churn-experiment.md); [07 design proposal](design/storage-publication-v1.md) records request identity, exact bodies, separate freshness/error state and atomic commit-pinned publication. [08](issues/08-offline-storage-prototype.md) is the next offline frontier. No live collection, branch publication, schedule or app integration enabled.


2026-10-27: [08 resolved](issues/08-offline-storage-prototype.md).
[Offline findings](research/storage-prototype-findings.md) and
[machine report](research/storage-prototype-report.json) record 64 passing replay
checks, exact-byte preservation, explicit timing/enrollment limitations and
commit-pinned/stale-parent behavior. Full-repack growth was 5,071 bytes; incremental
GC yielded a larger layout. Prototype source is captured separately on
`proto/offline-storage-v1`; no production code is merged. [09](issues/09-review-offline-findings.md)
is the review frontier. No HTTP, push, dispatch or app change.


2026-10-27: [09 resolved](issues/09-review-offline-findings.md) after Marek authorized
continuing the review. The proposal now records separate receipt/validation timing
provenance, public-only enrollment constraints, provisional offline limits and
alias lifecycle gaps. [10](issues/10-offline-client-freshness.md) specifies an offline
client freshness/lookup experiment. Production schema and remote operations remain
unaccepted; no network action or push performed.


2026-10-27: pushed main-marek through ce1d81537 with Marek's explicit approval,
then completed [10](issues/10-offline-client-freshness.md) offline. [Findings](research/freshness-prototype-findings.md)
and [report](research/freshness-prototype-report.json) record 54 outcomes covering
freshness edges, consent binding, alias/re-enrollment, pinned reads and limits.
Prototype source is 694613538 on proto/offline-freshness-v1, separate from main.
No live experiment or integration ran. [11](issues/11-review-client-and-collection-boundaries.md)
records the remaining review choices.


2026-10-27: [11 claimed](issues/11-review-client-and-collection-boundaries.md).
[Review proposal](design/client-collection-review.md) records freshness/consent
recommendations, documented workflow-token isolation and a bounded six-attempt
future-job envelope. The earlier anonymous-first recommendation was too strong;
a restricted token excluding its own repository is a design option. Policy answers
remain pending. Documentation research only; no new upstream API experiment.


2026-10-27: [11 resolved](issues/11-review-client-and-collection-boundaries.md).
Marek accepted both recommendations: initial freshness/consent contract and
restricted workflow-token collector design before remote delivery. The
[implementation design](design/restricted-collector-v1.md) defines pure planning,
injected transport/clock, own-repository identity exclusion and bounded collection.
[12](issues/12-offline-restricted-collector.md) is ready for offline implementation.
No network transport or workflow change has been implemented or dispatched.


2026-10-27: with Marek's push-and-continue instruction, pushed the accepted design
through f986e5c93, then resolved [12](issues/12-offline-restricted-collector.md).
The injected collector core and synthetic replay are in tools/catalog-collector;
17 focused tests and eight historical churn tests pass. [Findings](research/collector-offline-findings.md)
record the event/deadline/identity/conditional boundaries and remaining adapter
limits. No active workflow, live transport or installer was changed.
[13](issues/13-prepare-adapter-and-enrollment-review.md) is the preparation frontier.


2026-10-27: [13 resolved](issues/13-prepare-adapter-and-enrollment-review.md).
[Transport/enrollment package](design/transport-enrollment-review.md) and
[saved identity audit](research/saved-identity-audit.json) establish three historical
IDs and one missing upstream ID. Review exposed name-reassignment drift and proposes
numeric-only operational fetch descriptors. Proposed identity enrollment is one
separately authorized metadata GET, with any later six-release baseline separate.
No requests or workflow changes were made. [14](issues/14-offline-supervised-transport.md)
is the next offline implementation frontier.


2026-10-27: [14 resolved](issues/14-offline-supervised-transport.md). Supervised
numeric-ID adapter implemented with private IPC, genuine Connected event,
bounded HTTP parsing and parent kill/reap deadlines. [Findings](research/supervised-adapter-findings.md)
and [checks](research/supervised-adapter-checks.json) record 44 passing offline
tests using fake sockets/local worker processes only. Active workflows are unchanged,
SQLite identity is still missing and no live CLI or run was added.
[15](issues/15-review-adapter-and-stage-manifest.md) prepares the concrete review,
incomplete manifest and inactive workflow proposal.


2026-10-27: [15 resolved](issues/15-review-adapter-and-stage-manifest.md).
[Concrete adapter review/run package](research/adapter-review-and-run-package.md)
records a malformed-header framing fix, the six-row incomplete numeric manifest,
and an inactive workflow proposal with tested context/revision/hash checks.
48 offline tests pass on Python 3.14.4/Linux; YAML/embedded Python checks pass.
SQLite enrollment still refuses before workers. No API request, active workflow
change, push or dispatch. Next is separately authorized one-read enrollment, then
review of the runnable manifest and exact pushed revision before any baseline.


2026-10-27: with explicit user approval, pushed f8182c6e9 and performed exactly
one unauthenticated SQLite Browser metadata GET. [Reviewed enrollment](research/sqlite-enrollment-findings.md)
records HTTP 200, public identity 19416551 and exact bounded response evidence.
Filled the sixth numeric manifest row with that evidence; preserved aliases and
new request identities. No release endpoint, workflow activation or dispatch.
The inactive workflow and six-release baseline require separate approval.


2026-10-27: [16 claimed](issues/16-first-supervised-live-validation.md). Marek
explicitly approved pushing enrollment, installing/pushing the prepared manual-only
workflow and one six-release adapter run. Current server settings retain the five
unrelated workflows disabled; recheck exact revision/isolation before dispatch.


2026-10-27: [16 resolved](issues/16-first-supervised-live-validation.md). Approved
manual workflow installed/pushed at 79159ba68; historical probe disabled so only
the collector is active. Exactly one authorized dispatch, run 40529551070,
succeeded with six HTTP 200 complete transfers (4,877,758 bytes / 5.198 seconds).
[Findings, machine checks and persistent exact evidence](research/supervised-baseline-40529551070-findings.md)
verify every body hash, six numeric routes, quota and timing. No retry, schedule,
publication or app change. Storage/publication/client integration remain separate;
no day sample or wait is required. Further collection needs explicit instruction.


2026-10-27: [17 claimed](issues/17-integrate-observation-storage.md). Implemented
[collector/storage integration](design/storage-collector-integration.md), closed
candidate artifact validation and local-only publication/pinned reads. 62 offline
tests pass against saved measured evidence and synthetic transitions. Preparing
one authorized six-source live validation with unchanged contents:read boundary.


2026-10-27: [17 resolved](issues/17-integrate-observation-storage.md). Actual
collector/storage staging implemented with pure transitions, closed-tree bounds,
local atomic Git publication and pinned freshness reads. 62 offline tests pass.
One authorized run 40531417616 (9679305de) succeeded on Python 3.12.3/Linux:
six valid observations, 12 aliases, 4,893,975-byte candidate.
[Persistent evidence and checks](research/storage-integration-40531417616-findings.md)
include exact candidate files and a local publication bundle. Workflow remains
contents:read and starts a fresh candidate per run. Next delivery seam is trusted
prior-state loading plus a separate artifact-validating publisher; no remote
catalog branch, schedule or installer change has occurred.
