# Release catalog exploration

## Retained-growth experiment — November 4, 2026

[76 resolved](issues/76-measure-retained-growth-and-staging.md): thirty 100-new-ID
merges grow to 5.00 MB; near-cap staging reaches 16.73 MB at about 125 MiB RSS.
[Revised-reader results](research/yaml-retained-growth.md) include line/spool
boundaries and zero-output refusals. BusyBox hits a 55-second CPU cap at 16.67 MB;
mawk/GNU awk complete. Trial ceilings remain provisional; hard runtime/staging
limits and live capacity remain 71's gates. Local prototype `ccd0273e4` only.

## Latest local experiment — November 4, 2026

[75 resolved](issues/75-bound-offline-response-normalization.md): file-backed JSON
normalization with actual byte accounting, lazy finite scope and atomic retained
merges. Six new acceptance groups pass on all three awk tools, alongside the
prior sixteen groups. [Findings](research/yaml-bounded-offline-normalizer.md)
separate cooperative elapsed refusal from hard deadlines. Retained-growth,
staging/reader resource stress and operational ceilings remain open under 71.
Prototype branch is local only; production remains format 1.

## Current design — scoped retention, November 3, 2026

[74 resolved](issues/74-revise-scoped-retained-catalog.md) applies Marek's
[retained-observation revision](research/yaml-retention-revision.md). This supersedes
mandatory full-history and replacement-only windows throughout historical entries.
Scheduled default: all sources, one page of 100 releases. Parameterized scopes
merge successful fetched records into retention; untouched releases keep their
observed_at, which determines selected-release installation freshness. Safety
budgets and retained-size/reader-memory bounds remain required. Reconciliation is
explicit all-only in the local proposal. Schema and experiments are local only;
no deployment, dispatch, push or repin is authorized.
Sixteen test groups pass on all three awk tools. Prototype source is local on
research/yaml-retained-observations at 4600ae084; production memory/CPU bounds
remain unproven for the revised schema.

## Notes

Work in Marek's active AM fork, on main-marek. Goal: find a simple reliable approach, evolve it through experiments, then propose it upstream. This map and tickets are intentionally tracked by Git.

Earlier work: [2026-10-20 design and measurements](../../design/version-catalog.md), with throwaway code on proto/release-catalog in tools/proto-catalog/. Preserve that branch and its evidence. The earlier design combines a GraphQL collector, CI version selection, and a generic installer. The newer direction separates upstream observations from app-specific selection and leaves selection on the client. Neither is immutable policy.

## Decisions-so-far

- **Current adoption direction (2026-10-27):** simplify total AM client logic;
  remove independent proxy/source trust; use shell and existing utilities on the
  consumer side, with no Python/jq/checkout runtime requirement. CI may retain
  Python. **Corrected 2026-10-28:** catalog ownership follows configured AMREPO;
  our fork reads mareklangiewicz/AM, with no upstream-AM fallback or acceptance
  prerequisite. Keep original app binary URLs. [29](issues/29-respect-configured-catalog-repository.md)
  supersedes the fixed-upstream interpretation in historical entries below.
  See [accepted direction](spec.md#accepted-adoption-direction-2026-10-27).
- **[29 resolved: configured catalog ownership](issues/29-respect-configured-catalog-repository.md).**
  Reader, manager install/update handoff and generated standalone updater follow
  AMREPO. Missing/unsupported sources and selected-catalog failures refuse without
  upstream-AM fallback. 107 tests plus syntax/lint pass; current client delta is
  +194 net lines. Historical fixed-upstream guidance and ticket 28's frontier are
  superseded throughout the tracker; original evidence bytes are preserved.
- **[23 resolved: shared shell implementation](issues/23-shell-consumer-and-small-recipe-migration.md).**
  [Implementation and adoption boundary](design/shell-consumer.md): derived TSV,
  one shared reader (initially 96 lines), ordinary Obsidian recipe/generated updater, and foreground
  single-app refusal propagation. Initial 89-test result is historical; current
  ownership and validation are in ticket 29. Installed migration remains separate.
  This supersedes ticket 22's Python zipapp/runtime-packaging recommendation.
- [24 resolved: published shell roundtrip and module distribution](issues/24-shell-publication-roundtrip.md).
  Real temporary bare-Git publication, conditional repeat, pinned reads across ref
  movement and exact stale consent pass; actual module sync/cleanup preserves the
  standalone updater's reader. That ticket passed 92 tests. Fixed stale
  README instructions. Ticket 27 subsequently verified the bounded fork public
  read. Upstream acceptance is not a fork-use prerequisite (ticket 29).
- [25 resolved: standards/spec review and integration fixes](issues/25-review-shell-adoption.md).
  No documented standards breaches; four spec regressions fixed (retry, checksum
  repair, install preflight mutation and launcher-only routing). Actual installation
  dispatch was covered by 100 tests; net client source cost then was +179.
  These are historical ticket-25 results; tickets 27 and 29 add bounded public
  fork-read evidence and correct repository ownership. Net simplification remains unproven.
- [01: prior research reconciled](issues/01-reconcile-prior-work.md): retain useful measurements, but distinguish the earlier resolved catalog from the current observation catalog. The reported 825-point sweep is GraphQL evidence, not a REST response-catalog capacity measurement.
- Working direction: collector preserves upstream metadata without ranking releases or selecting downloads; app scripts keep policy. Public upstream metadata is not independent binary authenticity.
- Explore a dedicated AM publication branch, hourly collection, reviewed endpoint inventory, retained observations on temporary failures, per-observation checked times, explicit stale-data acceptance beyond 24 hours, and selective client downloads pinned to a publication commit.
- Exact REST snapshots are the provisional direction after the baseline/hour sample. The day sample is optional; retain the six-endpoint, short-window limits on any storage conclusions. Reconsider representation with broader evidence or new consumer needs.
- Catalog work does not execute the active app installer or installed updaters. Existing app management behavior remains unchanged during experiments.

## Latest completed rollout — November 2, 2026

[69 resolved: approved 65-recipe rollout completed](research/appimage-exceptions-next-20261102/live-rollout-accepted.md).
Same run 41479232632 passed full acceptance: 16 shards, 987 recipes, all 1,974
selectors and pinned shell/Python readers. Source and daily pin now equal exact
reviewed recipe commit 5ab112d25; accepted catalog e391f35f6 is unchanged.
Final workflow/run controls passed. The subsequently approved evidence publication
and daily repin advanced source=pin to `519c0e484`; accepted catalog is unchanged.
Earlier refusals remain preserved. [70 resolved](issues/70-diagnose-installed-obsidian-clock-refusal.md):
uutils date 0.10.0 confirmed in Marek's original terminal; Marek synced the
corrected helper and successfully updated Obsidian 1.15.0. Installed helper
matches repository bytes. Original failure predicates remain uncaptured.
Published correction source=pin was `0464ec126`; this documentation follow-up
is local only. Natural sharded daily repeat remains unproven.

## Historical rollout stop — November 2, 2026 (superseded by completion above)

[69: 65-recipe rollout stopped at client acceptance](research/appimage-exceptions-next-20261102/live-rollout-stop.md).
Enrollment ab04b9d8c and exactly one successful 16-shard run 41479232632 published
catalog e391f35f6. Both read-only acceptance attempts passed artifacts/Git and all
1,974 selectors, then shell-reader acceptance refused. A trace reproduced a
0.501250-second local wall-clock regression; body hash matched and the guard
correctly refused. Recipe delivery 5ab112d25 remains unpushed; pin stays f6b3c349c,
so source/pin mismatch intentionally gates scheduled dispatch. Establish a stable
clock and complete same-run read-only acceptance before the already approved
recipe/pin steps. No collection rerun or host operation.

## Latest accepted stage — November 2, 2026

[68 resolved: next 65 exception recipes prepared locally](research/appimage-exceptions-next-20261102/findings.md).
Explicit redirect identities, actual selectors, preserved 719-source inventory,
16-shard replay and all 65 inert installs/updates pass. Two exact local stages
and [rollout review](research/appimage-exceptions-next-20261102/rollout.md) await
the separate push decision; 13 exceptions remain unchanged. No new collection,
source publication, repin or host delivery; no natural sharded repeat observed.

[67 resolved: 922-recipe sharded rollout accepted](research/appimage-next-large-batch-20261102/live-rollout.md).
Approved run 41471816957 passed all 14 shards and publisher; independent acceptance
verified all artifacts/Git, 1,844 selectors and pinned readers. Published source
and daily pin: `f6b3c349cf4d590d0591b9c601bb8ac01c4fc629`; catalog:
`6f21b8c1d2bf271f570a0177bc1068bb9ca43d0a`. Only sharded collector/dispatcher
active; 78 exceptions unchanged. No host delivery. One live run establishes no
long-term reliability or Git-growth claim. Earlier stage details follow.

[52-source enrollment and 107-recipe publication accepted](research/appimage-52-live-20261102.md).
Exactly one approved run 41442000508 returned 52 HTTP 200 responses in 42.44 seconds;
full artifact/Git recomputation, 214 original selectors and both pinned readers pass.
Catalog tip `29e37bd9207ae9557e8f57afa010699c649d4cde`; published source and daily
pin both `d6e7421579d5a0f65588e39bb72995a675b9f08a`. No rollback or host delivery.
Tickets 47/49 remain partial only for eleven unchanged legacy exception paths
(four redirects and one 404). Older operational boundaries below are historical.

## Resource continuation — November 3, 2026

[73 resolved](issues/73-bound-yaml-reader-memory.md): [reader memory experiment](research/yaml-reader-memory-experiment.md)
preserves the contract, but BusyBox still reaches 54,360 KiB on a 16.38 MB fixture.
Fixed storage slots do not fix that growth. Prototype source is local on
research/yaml-reader-memory at ae1f216b4; production remains unchanged. [Wider and targeted history probes](research/yaml-history-outliers-20261103/findings.md)
completed 48 additional random histories in 65 requests, and identified two active
sources advertising 58/63 pages. Their full histories were deliberately not fetched.
[Candidate resource strategy and ceilings](research/yaml-resource-strategy.md)
remain proposals; aggregate request capacity and fair freshness need validation.
No production integration, push, daily repin, natural-run acceptance or host change.

## Current continuation boundary

**Current frontier (updated November 3, 2026):**

- [71 open: design simple YAML catalog](issues/71-design-simple-yaml-catalog.md).
  Design confirmed and [72 reader experiment resolved](issues/72-prove-yaml-reader-feasibility.md).
  See [findings](research/yaml-reader-experiment.md): strict validation is feasible;
  Unicode escape extension accepted; production resource strategy remains open.
  Prototype archived on research/yaml-reader-prototype at 8a3e5c623; production
  remains unchanged.

- [70 resolved](issues/70-diagnose-installed-obsidian-clock-refusal.md): original
  terminal uses affected uutils date 0.10.0; normal module sync delivered the
  fix and Marek's named Obsidian retry completed successfully.
- Last verified published source=pin was `0464ec126`, catalog `e391f35f6`,
  with only the sharded collector and daily dispatcher active (17:19 UTC,
  November 2 handoff). This documentation follow-up has not been published.
  Recheck remote controls before mutations.
- Next configured natural run: November 3 at 03:17 UTC / 04:17 Warsaw.
  Observe it and independently accept artifacts/publication; do not substitute
  a manual dispatch. No natural repeat has yet been observed.
- Future source publication requires review and matching exact daily repin.
- Rollout 69 is complete. Older migration/enrollment frontiers below are
  historical and must not restart completed rollout planning.

### Historical continuation boundary — October 31

**Current frontier (2026-10-31):**

- [37](issues/37-assess-hourly-pilot.md) is closed: hourly workflow disabled,
  four successful child publications verified and archived; expiry refusal verified.
- [41](issues/41-activate-daily-refresh.md) activated six-source daily operation
  at 03:17 UTC. The subsequent reviewed notice-fix source pin is
  `1d3253c5f2a82c74319d8188b02d5361457beb7b`.
  [64](issues/64-observe-daily-refresh-and-helper.md) is resolved: normal helper
  delivery was verified October 29; successful natural daily runs on October 30
  and 31 have exact publication evidence retained. Latest observations were about
  eight hours old at verification; scheduler delivery lagged over six hours.
- [66](issues/66-scope-explicit-reinstall.md) is resolved locally: named reinstall
  selection now applies before startup discovery and child-command cleanup.
  Final 56 container scenarios, 198 catalog tests and 10 support specs pass.
  Published and repinned as `6dddde9f6`; Marek ran normal sync and installed
  manager/install-module bytes were verified against that source. No host
  reinstall was needed to verify delivery.
- [47 enrollment](issues/47-enroll-scoped-migration-sources.md) has accepted the
  utility-source stage. [Live evidence](research/am-utils-live-20261031.md) verifies
  run 41232846271, seven HTTP 200 results, exact published tree/parent and 356/356
  selectors against returned bytes. Source and daily pin are
  `c787efe3a42fac015f743255006fddd7ea9b3817`; natural seven-source repeat remains
  unobserved. Ticket 47 stays claimed/partial for separate AppImage enrollment.
- [48 executable migration](issues/48-shared-executable-am-utils-batch.md) is
  resolved locally: all 356 exact selectors now use the shared executable lifecycle.
  [Implementation/cost/evidence](design/shared-executable-lifecycle.md): net
  −13,508 production lines / −530,292 bytes; 206 catalog tests, 10 support specs and
  72 container scenarios / 257 whole commands pass. No host delivery or source push.
- [49 AppImage migration](issues/49-migrate-common-appimage-batch.md) remains
  blocked on its separate enrollment; the 50 endpoints are not approved collection.
  Next operational observation is a natural seven-source daily repeat, distinct
  from implementation and from the next reviewed source push/pin or host delivery.

Shared AppImage implementation and recipe simplifications (42–46, 52–53), installed
CLI/Termux coverage (50, 54–56), and e2e support-tool extraction (57) are resolved.
Their evidence and limitations remain in the tickets and historical progress below.
[58](issues/58-post-download-failures.md) verifies post-download filesystem
failure and retry behavior offline; no production defect was demonstrated.


Use AMREPO-owned fork catalog and managed helper/source delivery (ticket 29).
Latest verified public publication is `a113cd0aca3247111b6ba231f6a30b6477ac2c75`,
from the approved October 31 seven-source rollout; actual observation times govern
freshness. Source push, one collection/publication and daily repin completed after
acceptance. The October 29 handoff records user-driven installed-updater migration;
older unmigrated/undelivered claims are historical. No host operation occurred in
this rollout.
Upstream submission is optional future work; ticket 28's upstream-first
recommendation is superseded. Future source publication requires reviewing and
repinning the exact source revision together.
Historical entries below describe what happened, not current runtime policy.

## Fog

- [70 resolved: installed Obsidian clock refusal](issues/70-diagnose-installed-obsidian-clock-refusal.md):
  host implementation confirmed, corrected helper delivered and named retry
  succeeded. The original event remains uncaptured; no actual wall-clock step
  is established. Natural daily repeat remains to be observed.

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


2026-10-27: [18 claimed](issues/18-persist-and-publish-catalog.md). Implemented
[exact-prior remote delivery](design/catalog-delivery.md) with contents:read
collection and a separate artifact-recomputing contents:write/actions:read job.
66 offline tests pass, including real prior ZIP replay and local bare-remote
bootstrap/conditional repeat. Preparing bounded bootstrap and exact-parent repeat
under Marek's existing push/workflow authorization; no schedule or app changes.


2026-10-27: [18 resolved](issues/18-persist-and-publish-catalog.md). Exact-prior
planning and a separate contents:write/actions:read publisher now deliver to
release-catalog while collection remains contents:read (confirmed in actual logs).
Bootstrap 40533557297 -> efcaeb2f3; exact-prior repeat 40533858562 -> d612ff34b.
Both succeeded with six 200s; all repeat requests sent matching prior validators,
without a live 304 claim. [Findings/evidence](research/catalog-delivery-findings.md)
preserve exact ZIPs, both published commits, permission/isolation checks and public
pinned index/body reads. 67 final offline tests pass, including post-run ZIP metadata
allocation hardening. No schedule, retry, force push or app change. Next is a small
read-only pinned consumer before any installed-updater migration.


2026-10-27: [19 claimed](issues/19-read-only-pinned-consumer.md). Implemented
[read-only selective consumer](design/catalog-consumer.md) with shared full index
metadata/freshness validation, fixed public bounded transport, one ref resolution
and only the pinned requested body. Preparing public-catalog-only smoke checks;
no source collection, workflow change, publication or installer modification.


2026-10-27: [19 resolved](issues/19-read-only-pinned-consumer.md). Read-only API/CLI
now resolves once (or accepts a full pin), validates shared index metadata, checks
freshness/consent before and after IO and returns one exact body. 80 offline tests
pass. [Actual CLI evidence](research/consumer-read-findings.md) verifies default
Obsidian and pinned Neovim reads at d612ff34b: five catalog GETs, exact saved bytes
and existing jq tag filters. Source 046d9ebd9; no upstream collection, workflow
dispatch, new publication, schedule or app change. Next is a single explicit opt-in
app/filter read path, without executing an installer or changing installed state.


2026-10-27: [20 resolved](issues/20-obsidian-opt-in-filter.md). The x86_64 Obsidian
script now exposes an explicit --catalog-version read-only path before installer
setup, feeding verified consumer bytes to its existing release-list asset filter.
76 collector/integration tests plus eight historical churn tests pass offline;
shell syntax and diff checks pass. Verification uses retained measured bytes and
injected consumer fetch/time plus a shell-command shim; no fresh HTTP or end-to-end
live CLI claim. Full-checkout dependency and unchanged legacy filter limitations
are documented. No installer execution, installed state change, updater migration,
workflow dispatch, publication or push. Next adoption scope remains undecided.


2026-10-27: [21 resolved](issues/21-obsidian-live-read.md). Actual Obsidian
--catalog-version with explicit d612ff34b pin succeeded end to end at c9f74c7df,
without injection/shim. Two GETs on the successful invocation, fresh observation,
empty stderr, URL equal to both existing filters on retained publication bytes;
body/index hashes match retained ticket 18 artifact. Initial sandbox attempt
refused (its request count unmeasured), then approved network access succeeded.
Evidence is retained alongside the ticket. No installer, asset download, workflow,
collection, publication or installed state change. Ordinary update adoption remains
a separate design decision.


2026-10-27: [22 resolved](issues/22-update-adoption-proposal.md).
[Update adoption proposal](design/obsidian-update-adoption.md) traces actual AM
background/suppressed updater execution, early mutation, shell-only module sync and
Obsidian's appimageupdatetool bypass. Recommends coherent consumer distribution,
foreground single-app preflight and explicit supported-adapter enrollment with
visible refusal/exact stale consent. Proposal only. Next bounded code step is
local runtime packaging and offline verification; no installed migration, remote
runtime delivery, ordinary update change or schedule is enabled.


2026-10-27: Marek accepted a simplifying, shell-first adoption direction and deferred
implementation to the next session. [23 opened](issues/23-shell-consumer-and-small-recipe-migration.md)
as the unblocked frontier: shared shell reader and shell-friendly lookup metadata,
small ordinary recipe/generated-updater read changes, original selection filters
and upstream binary URLs, no new consumer language/service/trust operator. Preserve
pinning/freshness/integrity checks centrally and remove only proven displaced proxy/
quota/token logic. [Spec updated](spec.md#accepted-adoption-direction-2026-10-27);
ticket 22's Python packaging recommendation is explicitly superseded while its
source findings and historical test evidence remain intact. Documentation only;
no implementation, installed state, network experiment or workflow changes.


2026-10-27: [23 resolved](issues/23-shell-consumer-and-small-recipe-migration.md).
Implemented atomically derived shell lookup metadata and the shared POSIX-shell
reader, with full pins, exact stale consent, measured freshness, bounded transfers
and body integrity checks. Ordinary Obsidian recipe/generated updater retain their
asset filter and upstream binary URL; removed the Python query branch and optional
alternate updater bypass. AM embeds its managed helper path and routes a single
marked updater in the foreground before legacy mutation; optional binary-digest
verification remains afterward. 89 offline tests, syntax, reader ShellCheck and
recipe warning-level ShellCheck pass. [Cost/caller audit and public validation plan](design/shell-consumer.md)
record +139 net client lines, remaining legacy callers and GNU-tool scope. The
fixed upstream AM publication is not yet adopted/live-validated. No installed
state, collection, workflow, publication, schedule or push was changed.


2026-10-27: [24 resolved](issues/24-shell-publication-roundtrip.md). Continued
offline after Marek deferred the yadm/Git-metadata issue. Cross-boundary checks now
exercise the actual bounded ZIP parser, publisher recomputation/local bare-remote
push, commit-pinned shell reads during branch movement, conditional repeat and
exact stale consent across publication commits. Actual module inventory/sync and
obsolete cleanup replace/deliver the helper while preserving a generated updater.
92 tests pass; README no longer advertises the retired query flag. No production
code defect was exposed. No source collection, live publication/workflow, installed
state or schedule changed. Git commit/push remain authorized but deferred pending
writable metadata; all work is saved in this AM working tree.


2026-10-27: [25 resolved](issues/25-review-shell-adoption.md). Separate standards
and spec reviewers examined the complete uncommitted slice against 0a21fef3c,
including new files. Four P2 spec findings exposed missing manager-entrypoint
coverage despite the prior passing suites: failed-download retry deadlock,
same-version checksum repair bypass, installation mutation before acceptance,
and unrelated launcher refusal. Fixed and rechecked all four, including the
unavailable replacement-recipe case and standard debug handling. Actual install.am
dispatch/functions now run in temporary-root refusal and successful repair tests.
100 final tests, syntax checks, reader/recipe lint and documentation/diff checks
pass. Updated current cost to +179 net client lines; +139 and previous test counts
above are historical. No live workflow/publication, source collection, installed
migration or schedule occurred. Changes remain saved in the working tree while
Marek handles Git metadata access.


2026-10-27: [26 resolved: prepare bounded fork shell validation](issues/26-prepare-fork-shell-validation.md).
[Concrete candidate and approval plan](research/fork-shell-validation-plan.md)
preserves the current fork publication's index/bodies/times and adds only derived
lookup.tsv. Exact child `a0fdd125558c4629a07c7edd0d7f6f7f96b1dcc1` is bundled;
parent was confirmed read-only as `d612ff34b492b337fe51128f769ec9d262d0ee86`.
Local bundle/hash/body/filter checks and temporary bare-Git push pass. An explicit
fork-only reader copy keeps the installed upstream trust target unchanged.
No remote publication/live shell read, collection, workflow, schedule or app
operation; the proposed publication and two-GET pinned read await approval.


2026-10-27: [27 resolved: fork publication and public shell read](issues/27-publish-fork-shell-validation.md).
[Real HTTP findings and evidence](research/fork-shell-public-read-findings.md):
with Marek's explicit approval, published exact prepared child a0fdd1255 atop
confirmed d612ff34b, then the fork-only reader made exactly two pinned catalog
GETs (both 200), returned exact retained bytes and the identical Obsidian URL,
exit 0 and empty stderr. No clock/response substitution or stale override.
The installed upstream owner is unchanged; upstream acceptance and installed
migration remain separate. No source branch push, collection, workflow, schedule
or host app operation.


2026-10-28: source/evidence through b6892ff2f pushed to origin/main-marek.
[28 resolved: upstream adoption readiness](issues/28-upstream-adoption-readiness.md).
[Concrete boundary audit and rollout order](design/upstream-adoption-readiness.md)
records fork-specific collector/publisher/artifact guards and Python reference
identity; the shell production owner is already upstream. Offline exact-child
prior planning preserves all six bodies/validator tuples and existing context
refusals. Upstream publisher/provenance and sustained freshness must precede
ordinary recipe activation. No guard changes, workflow, collection, publication,
upstream submission or installed operation.


2026-10-28: [29 resolved: respect configured catalog repository](issues/29-respect-configured-catalog-repository.md).
Marek corrected the upstream-only interpretation: our fork follows AMREPO and
must not silently read upstream AM. Actual source-selection regression reproduced
the defect before repair. Reader validation, persistent standalone source embedding
and explicit managed update handoff now pass 107 tests, syntax and lint. Current
spec/map/design/README and all affected tickets/historical plans identify this
correction; ticket 28's upstream-first recommendation is withdrawn. Historical
archives/JSON retain their original bytes/source revisions. No live requests,
collection, workflow, publication, app execution, installed migration or schedule.


2026-10-28: [30 resolved: current helper public read](issues/30-current-helper-public-read.md).
Unmodified 3a843e656 helper with explicit fork AMREPO and a0fdd1255 pin made two
HTTP 200 GETs, passed real freshness without stale consent, and returned exact
retained lookup/body bytes and the unchanged recipe filter URL. Initial sandbox
DNS refusal and approved network run are separately retained in
[findings/evidence](research/current-helper-public-read-findings.md).
No publication, collection, workflow, schedule, binary download or app execution.


2026-10-28: [31 resolved: installed pilot preparation](issues/31-prepare-installed-obsidian-pilot.md).
Read-only host inspection and [four-file payload/rollback plan](pilot/plan.md)
are complete. Installed Obsidian is 1.14.4, so execution against retained 1.14.5
metadata would change the app. Proposed first pilot is delivery only; host writes
and actual app update are not performed. Payload syntax checks pass.


2026-10-28: [32 open, ready-for-human: approved installed delivery](issues/32-installed-obsidian-delivery-pilot.md).
Hash/syntax prechecks passed, but backup ownership preservation failed EPERM
before any installed replacement. sudo requires interactive authentication.
Partial backups are retained; checked delivery script is saved. Resume the same
approved pilot after sudo authentication; no app/update operation has run.


2026-10-28: [32 resolved: installed delivery and user-run update](issues/32-installed-obsidian-delivery-pilot.md).
Marek completed sudo delivery, then pinned `am -u obsidian`; original upstream
1.14.5 binary downloaded. Read-only inspection confirms payload hashes, version,
binary size/hash and absent tmp. Evidence distinguishes delivery-only backup from
subsequent app replacement; no app launch or independent authenticity claim.


2026-10-28: [33 resolved: freshness-run preparation](issues/33-prepare-manual-freshness-run.md).
Read-only remote checks confirm manual collector alone active and exact source/
publication pins. Retained prior prepares offline; 107 tests pass. Concrete
[six-source manual run and publication plan](research/manual-freshness-run-plan.md)
is ready; [34](issues/34-one-manual-freshness-run.md) awaits explicit run approval.
No collection, dispatch, publication, schedule or app operation in preparation.


2026-10-28: [34 resolved: manual freshness refresh](issues/34-one-manual-freshness-run.md).
One approved run 40606441534, six conditional 200s, exact-prior child e8e5cf962
published; full artifact/tree/permission verification and two pinned public helper
GETs pass. [Persistent evidence](research/manual-freshness-run-findings.md).
Obsidian fresh through 2026-10-29T00:05:15.676301Z; no recurring schedule or app run.


2026-10-28: [35 resolved: hourly pilot preparation](issues/35-prepare-hourly-refresh-pilot.md).
Inert workflow/controller and [bounded 24-hour plan](design/hourly-refresh-pilot.md)
prepared; 111 tests pass. Default branch is now main-marek. Existing collector
unchanged; exact-source/window/overlap/count refusal guards checked offline.
[36](issues/36-activate-hourly-refresh-pilot.md) awaits explicit schedule activation;
no schedule, remote variable, collection, publication or app change occurred.


2026-10-28: [36 activation armed, verification pending](issues/36-activate-hourly-refresh-pilot.md).
Approved schedule/controller pushed at 466e1facc; only collector and dispatcher
active, six other workflows disabled. Variables verified for exact revision and
2026-10-28T00:12:16Z to exclusive 2026-10-29T00:12:16Z. No natural scheduled event
listed yet at 00:19:04Z; no extra dispatch or app operation. Activation evidence
saved locally so source pin remains stable. [37](issues/37-assess-hourly-pilot.md)
tracks expiry shutdown/assessment without implicit window extension.


2026-10-28 08:56Z: [36 resolved: first natural scheduled path verified](issues/36-activate-hourly-refresh-pilot.md).
Scheduled controller 40640684033 -> child 40640700123 -> publication 2dd9db2bd.
Six conditional 200s, prior tuples, exact artifact/tree/parent and permission logs
verified and archived. Only one scheduled event so far; hourly cadence is not
established. Obsidian fresh through 2026-10-29T05:54:45.963442Z. Ticket 37 remains
open for expiry shutdown/assessment; no extra dispatch, app operation or extension.


2026-10-28: [38 resolved: second recipe migrated](issues/38-sqlitebrowser-catalog-recipe.md).
SQLite Browser now consumes its already enrolled catalog alias through the shared
reader. Both filters/original binary URLs preserved; alternate updater removed.
Actual installer/generated updater/manager handoff, stale/refusal and repair paths
verified with retained bytes and isolated roots. Full suite 116 passes before the
final additional install-dispatch test; six final SQLite tests, syntax and lint pass.
No shared runtime/collector change, live source request, installed migration or
push that would disturb the running hourly pilot's source pin.


2026-10-28: [39 resolved: sparse schedule diagnosis](issues/39-diagnose-scheduled-cadence.md).
Ten nominal slots, one scheduled event across both API query scopes; no failed,
skipped or queued run. Existing dispatcher/job start promptly and child succeeds.
Remote cron/default/source/window/state/history correct. Gap is before workflow
execution; documented GitHub schedule delay/drop fits, internal reason unproven.
[Replayable evidence and alternatives](research/scheduled-cadence-diagnosis.md).
No cron change, repin, extra dispatch/collection, app operation or extension.


2026-10-28: [40 resolved: daily refresh/48-hour policy](issues/40-daily-refresh-48-hour-freshness.md).
Marek accepted final daily collection and 48-hour freshness. Local workflow now
03:17 UTC daily; final controller drops pilot-only window/count machinery while
retaining source/ref/event/isolation/overlap/rerun guards. Both readers use inclusive
48-hour measured age and exact consent beyond it. 118 tests, syntax, lint, YAML
and diff checks pass. [41](issues/41-activate-daily-refresh.md) is already authorized
but waits for ticket 37's planned pilot shutdown. No mid-pilot remote/source change
or installed app/helper mutation. Historical 24-hour evidence retains its meaning.


2026-10-28: recorded accepted shared-lifecycle direction and opened
[42](issues/42-shared-appimage-lifecycle.md) as ready-for-agent, unclaimed next
implementation. Added dependent 43–45 for nvim, normal mixed/batch updates and
recipe-family inventory. Spec and current continuation priority updated. This
supersedes the earlier batch-first/read-call-only continuation recommendation;
historical implementation evidence remains unchanged. Documentation only; no
runtime, source push, workflow, collection or installed-state changes.


2026-10-28: [42 resolved](issues/42-shared-appimage-lifecycle.md). Obsidian and
SQLite Browser share managed AppImage install/update mechanics, each retaining
one selector and a saved trusted recipe behind a three-line standalone updater.
[Interface/delivery/cost audit](design/shared-appimage-lifecycle.md) records 50 fewer
source lines, with an honest 87-line increase in the two-app installed footprint
including shared runtime. 124 catalog + 8 historical probe tests, syntax, warning
ShellCheck and diff checks pass. No source push, live request, host app/helper
migration or workflow change; timed 37/41 obligations remain, followed by 43–45.


2026-10-28: [43 resolved](issues/43-migrate-nvim-shared-lifecycle.md). nvim is the
third caller of the unchanged shared AppImage implementation, retaining its exact
stable/architecture selector and upstream URL in one small recipe. Removed 56
source lines / 2560 bytes and its alternate updater bypass. [Incremental cost and
delivery audit](design/shared-appimage-lifecycle.md#third-caller-nvim-ticket-43).
132 catalog tests, syntax, warning ShellCheck and diff checks pass. No network,
source enrollment/push, host migration or workflow change. Timed 37/41 obligations
remain independent; 44 is the next coding frontier.


2026-10-28: [44 resolved](issues/44-normal-batch-catalog-updates.md). Normal no-arg,
all-app and explicit mixed batches now continue sequentially with visible per-path
results and aggregate failure status, including through actual command/color
filter dispatch and post-app sync. One source-bound command publication pin/lookup
is reused, with per-app freshness/exact consent/integrity. Migrated paths avoid
legacy preprocessing/global cleanup; legacy child/checksum status is preserved.
[Semantics, delivery and cost](design/normal-batch-updates.md): 149 catalog + 8
historical tests, syntax/lint/baseline warnings and diff checks pass; production
-61 lines / -2149 bytes. No live requests, installed migration, source push or
workflow changes. Timed 37/41 obligations remain; 45 is the next coding frontier.


2026-10-28: [45 resolved](issues/45-recipe-inventory-and-migration-batches.md).
[Static recipe inventory](research/recipe-family-inventory.md) scans all 10,716
architecture recipes, with a hashed reproducible JSON report and independent
[exception/caller audit](research/recipe-exceptions-and-callers.md). Only three
remaining Neovim AppImages are fully exact-covered. Opened 46 for that batch and
47–49 for separate reviewed enrollment and real larger families: 356 plain
executables / one source; 124 AppImages / 50 sources. Projected deletion is kept
separate from implemented/installed savings. Existing six-request/8 MB/300 s/50 MB
guards require measured incremental enrollment, not a blind manifest expansion.
Independent AWK token comparison, repeated output, path/partition checks, Python
compilation and diff checks pass. No runtime/recipe/filter execution, live requests,
installed changes, collection, workflows or source push. Timed 37/41 remain.


2026-10-28: [50 resolved](issues/50-container-cli-e2e.md), taking user-requested e2e
coverage ahead of the migration frontier. The [container runner](../../../test/e2e/README.md)
passes eight whole-installed-command scenarios / 21 invocations on each of Debian
and Fedora, without extracted manager functions or stubbed sync/verification.
[Findings and actual run evidence](research/container-cli-e2e-findings.md) record
real fixes for quiet-grep SIGPIPE under pipefail and stale configured module source.
The regression repairs an older installed module and preserves app failure through
real no-argument sync. 149 catalog tests, syntax/lint/baseline warning checks and
diff checks pass. Runtime networking disabled; retained observations/inert binaries,
not live upstream assets. No host delivery, production workflow or source push.
Ticket 46 remains next; timed 37/41 remain independent.


2026-10-28: [46 resolved](issues/46-migrate-remaining-neovim-appimages.md)
migrates the three remaining Neovim recipes with exact selectors and retained
assets. A demonstrated mutable nightly URL requires one trusted refresh flag;
explicit nightly updates now redownload after acceptance. Container whole-command
matrix passes 18 scenarios / 56 commands, and existing real stable/nightly
AppImages pass isolated startup on both distributions. Host updaters/configuration
remain untouched. [51](issues/51-prepare-neovim-host-delivery.md) tracks legacy
payload rehearsal, copied-config compatibility and rollback before live delivery.
182 catalog + 8 historical probe tests, syntax/lint and unchanged manager warning
baseline pass. [Checks/evidence](research/neovim-migration-46-checks.txt) retain
actual successful runs. Timed 37/41 and no-source-push restriction remain independent.


2026-10-28: [51 resolved: prepared Neovim delivery](issues/51-prepare-neovim-host-delivery.md).
Private delivery/rollback rehearsal and isolated configuration startup checks pass
on Debian/Fedora. Host-specific inventories, payloads, paths/hashes, plugin lists
and logs are retained locally outside publishable history. Added Git to container
environments; the public fixture matrix passes 18 scenarios / 56 commands.
No host delivery, upstream binary download, source push or operational change.
Timed 37/41 remain independent. Earlier unpublished inclusion of host metadata
was removed by rewriting the unpublished commits before publication.


2026-10-28: [52 resolved: compact AppImage recipes](issues/52-compact-appimage-recipes.md).
Six recipes drop eight repeated setup lines each, leaving app identity, exact
catalog alias, selector and genuine exceptions. Shared defaults and installer-owned
persistent bindings preserve AppMan/standalone behavior and older expanded recipes.
132 -> 84 recipe lines; production source -30 lines. Catalog verification covers
all 182 cases after affected-module fixture corrections, eight historical probes,
and 18 Debian/Fedora whole-command scenarios / 56 commands. No host delivery,
source push or workflow change; private payload manifests require rechecking and
37/41 obligations remain independent.


2026-10-28: [53 resolved: shared asset selection](issues/53-share-asset-selection.md).
Six recipes declare URL/include/exclude patterns; shared tokenization/filtering/
first-match logic preserves exact selection and case policy, with custom selectors
still supported. 184 catalog tests pass, including 126 differential selector cases;
18 Debian/Fedora whole-command scenarios / 56 commands pass. Recipe lines 84 -> 82,
production net +8 lines: centralization rather than a large size reduction. No host
delivery, source push, collection or workflow change; 37/41 remain independent.


2026-10-28: [54 resolved: native Termux command tests](issues/54-termux-container-cli.md).
Native Android/Bionic userland runs seven scenarios as uid/gid 1000 without FHS
compatibility links: direct AppMan, local AM auto-mode, read-only fallback,
privilege refusal, transfer/catalog preservation and a real native CLI ELF.
Fixed the demonstrated sudo-before-fallback ordering defect. [Findings](research/termux-container-findings.md)
retain exact red/green evidence and limits. Full matrix 25 scenarios / 70 commands
and all 184 catalog tests pass; final Termux rerun 7/14 also passes. No host delivery,
production collection, source push/repin or workflow change; timed 37/41 remain.


2026-10-28: [47 partially prepared](issues/47-enroll-scoped-migration-sources.md).
[Offline review package](design/migration-enrollment-plan.md) and
[exact queue](design/migration-enrollment-queue.json) freeze 356 utility paths plus
50 deferred endpoints / 49 identity requests. The first proposal is one bounded
unauthenticated am-utils identity GET; unknown IDs remain null. Existing six-source
manifest/guards, pilot pin and publication remain unchanged. No live request or
enrollment occurred; 48/49 remain blocked pending actual accepted availability.


2026-10-28: [47 identity stage completed](research/am-utils-enrollment-findings.md).
One user-approved unauthenticated GET confirmed public am-utils ID 1225768109,
HTTP 200, 4965 body bytes / 1323 header bytes in 0.557 s. Exact evidence committed
as `4a9aadb90`; candidate numeric descriptor recorded afterward, without validators.
No release request, operational enrollment, source push or schedule change; 48/49
remain blocked pending actual accepted release availability.


2026-10-28: [47 numeric release evidence](research/am-utils-release-findings.md).
One separately approved bounded GET succeeded (HTTP 200, 2.72 MB, 1.777 s).
All 356 original selectors audited offline: 354 choose saved assets; both c++filt
recipes miss GitHub's encoded-plus URLs. No filter changes; whole-family
compatibility and operational enrollment remain incomplete. Existing guards/pilot
pin unchanged, no push or workflow/host operation; 48/49 stay blocked.


2026-10-28: [47 offline implementation prepared](design/am-utils-seven-source-preparation.md).
Commit `033ed3d57` fixes both c++filt install/update selectors; all 356 now select
actual retained assets. A separate seven-source manifest preserves the exact six
original rows, with coordinated planner/manifest/transport/storage/publisher counts.
Seven-source ZIP/recomputation/temporary local publication and shell/reference
reader checks preserve refusal/freshness/conditional contracts. Measured candidate
tree 7.62 MB, ZIP 554 KB, local object growth 147 KB; unchanged byte/time caps.
Operational manifest/workflow/controller still select six sources. No live request,
source push/repin, schedule change or host delivery; 47 remains partial/ready-for-human
and 48/49 remain blocked. Pilot closure/daily switch retain their separate scope.


2026-10-28: [48 offline preparation](design/shared-executable-preparation.md).
Static audit confirms one lifecycle body across all 356 utility recipes, identifies
the two identity-validation exceptions and records the proposed shared interface,
installer integration and verification sequence. No production implementation,
live enrollment, host delivery or pilot change; 48 remains blocked by 47.


2026-10-28: [55 resolved: partial transfer and removal e2e](issues/55-e2e-partial-download-removal.md).
Added truncated-transfer preservation/retry and AM/AppMan removal/reinstall with
configuration preservation. Full Debian/Fedora matrix: 22 passing scenarios, zero
unexpected requests. Production unchanged; no host delivery or operational change.


2026-10-28: [56 resolved: source/freshness/Termux e2e](issues/56-e2e-source-freshness-termux.md).
Real installed commands verify manager source switching versus embedded standalone
source and the exact inclusive 48-hour freshness edge. Termux gains truncated
transfer and AppMan removal/reinstall coverage. Final 34 scenarios pass across
three targets; zero unexpected requests, unchanged production and pilot state.


2026-10-28: [57 resolved: specified e2e tools](issues/57-ground-e2e-tools.md).
Applied three myground findings: download destination parser, independent
filesystem snapshot and incremental transport-record reader. Nine focused specs
and 34 container scenarios / 108 commands pass; no repairs/reverts or production
changes. Initially uncommitted per skill; Marek subsequently authorized the local
commit. No source push or pilot/host operation.


2026-10-28: [58 resolved: post-download filesystem failures](issues/58-post-download-failures.md).
Updated the current frontier and added chmod/replacement/version-write failure
and retry coverage through real recipes and standalone updaters, including fresh
installation retries. No production fix needed; version-write failure reports
partial completion after binary replacement, without an atomic rollback claim.


2026-10-28: [59 resolved: offline daily-switch review](issues/59-daily-switch-offline-review.md).
Daily workflow/controller still match ticket 40; collector workflow and operational
six-source manifest match cached origin. Candidate enrollment remains separate;
known private delivery paths and removed commits are absent from queued history.
Five focused checks pass. Live closure/assessment and final source/pin verification
remain 37/41; no push, live request, workflow change or host delivery occurred.


2026-10-28: [60 resolved: installed AppMan batch failures](issues/60-appman-mixed-batch-failures.md).
Whole installed user-mode batches now cover catalog refusal, legacy failure,
transfer failure and successful retry, with continuation and aggregate statuses.
Final Debian/Fedora 28 scenarios / 100 commands pass, zero unexpected requests;
nine support-tool specs and lint/diff checks pass. Corrected one new test's
updated-versus-unchanged expectation; production unchanged. No host delivery,
source push, live collection, enrollment or pilot/schedule change.


2026-10-28: [61 resolved: interrupted AppMan commands](issues/61-interrupted-install-retry.md).
Actual SIGKILL after partial staging now covers fresh installation and existing-app
update, followed by normal retries and preservation checks. Final Debian/Fedora
30 scenarios / 108 commands pass, zero unexpected requests; nine support-tool specs
and lint/diff checks pass. No production fix, host delivery, source push, collection,
enrollment or pilot/schedule change; interruption coverage is one controlled point.

2026-10-29: [62 resolved: ground review tools](issues/62-ground-review-tools.md).
Shared recipe replacement encoding and source-file fingerprinting with focused
specs; both platform callers migrated. Focused checks passed, no reverts.

2026-10-29: [37 resolved](issues/37-assess-hourly-pilot.md). Full pilot evidence
retained; 24 HTTP 200 requests, 19.51 MB bodies, 19.60 MB uncompressed history
growth. No post-expiry child; daily activation under 41 is unblocked.

2026-10-29: [63 resolved](issues/63-repair-extracted-installer-test.md). Fixed
missing encoder dependency in extracted test harness. Full catalog suite 198 passes,
10 support specs and 38 Termux/Debian/Fedora container scenarios pass.

2026-10-29: [41 activated](issues/41-activate-daily-refresh.md). Verified source
pushed/pinned, daily workflow active, old window removed. Natural execution and
host delivery remain [64](issues/64-observe-daily-refresh-and-helper.md).

2026-10-29: [65 resolved](issues/65-configured-sync-notice-links.md). Sync notices
show actual configured recipe/manager source URLs. Reporting-only change; syntax,
diff and three-source rendering checks pass. Local commit, not delivered or pushed.

2026-10-31: [64 resolved](issues/64-observe-daily-refresh-and-helper.md).
Read-only verification of October 30/31 natural daily runs: twelve conditional
HTTP 200 outcomes, validated candidates, exact published Git blobs and chained
parents. [Evidence retained](research/daily-refresh-20261030-31.md). Latest
observations were about eight hours old; controllers arrived over six hours late.
The prior host delivery and ticket-65 source push/repin are historical user actions
recorded in the October 29 handoff, superseding earlier local-only claims.

2026-10-31: [66 resolved](issues/66-scope-explicit-reinstall.md).
Reproduced unwanted unrelated-app reinstall, then caught startup's additional
incomplete-app cleanup path. One command-wide named selection now constrains
discovery before cleanup, including child removals/installations; removed forced
saved-recipe edits. Six new whole-command cases across AM/AppMan and native Termux;
final 56 scenarios, 198 catalog tests and 10 support specs pass. No host operation,
source push/repin, manual collection or enrollment in this continuation.

2026-10-31: [47 rollout prepared](design/am-utils-seven-source-rollout.md).
After the approved push/repin of `6dddde9f6` and Marek's normal sync, read-only comparison
verified installed manager/install-module bytes. Prepared exact seven-source local
manifest/controller binding, preserved original six-source test evidence, and
specified one guarded first publication, acceptance, daily repin and bounded
fast-forward rollback. Full 199-test suite passes; all 356 retained selector results
match; tree/ZIP replay remains within unchanged caps. Local preparation only:
no upstream metadata request, source push/repin, dispatch or host operation.
Ticket 47 remains partial/ready-for-human; 48/49 remain blocked.


2026-10-31: [47 utility-source stage accepted](research/am-utils-live-20261031.md).
Approved exact source `c787efe3a`, run 41232846271 and publication `a113cd0ac` pass
seven-source recomputation, complete Git tree/parent, 356 actual asset selections,
pinned shell/Python readers and unchanged resource caps. Artifacts retained;
daily source repinned after acceptance with isolation verified. 48 unblocked;
47 remains partial and 49 blocked. Natural repeat evidence remains outstanding.
No recipe migration, host operation or second manual run.


2026-10-31: [48 resolved: shared utility lifecycle](issues/48-shared-executable-am-utils-batch.md).
All 356 utility recipes preserve original selectors and use the existing managed
module with a closed executable kind. Real installer integration skips desktop
post-processing; container tests caught and fixed its icon fallback. Net production
−13,508 lines / −530,292 bytes; 206 catalog tests, 10 support specs and 72 container
scenarios / 257 whole commands pass, zero unexpected requests. Actual installed
control-file costs and [retained evidence](research/utility-migration-evidence.tar.gz)
are recorded. Local implementation only; no host delivery, source push, collection,
workflow change or repin. 47 remains partial; 49 remains separately blocked.

2026-10-31: [48 published](issues/48-shared-executable-am-utils-batch.md).
User-authorized fast-forward through `7b31340a818a226c399130a776c5b03e78241438`
and matching daily pin verified. Collector/workflow production is unchanged;
only collector/dispatcher remain active, no unfinished runs observed, publication
remains `a113cd0ac`. No manual collection or host delivery. Natural seven-source
repeat remains outstanding. This post-publication record is local/uncommitted.

2026-10-31: [47 next-subset offline preparation](design/brave-enrollment-preparation.md)
freezes Brave's six recipe fingerprints and unchanged install/update selectors
(462 lines / 19,164 bytes), with syntax verified. Read-only checks show no natural
seven-source repeat yet. No new source requests, enrollment or operations; 49
remains blocked. Preparation remains local/uncommitted.

2026-10-31: [47 Brave bounded evidence](research/brave-enrollment-findings.md).
User approved advancing identity/release evidence before natural repeat. Exactly
two HTTP 200 GETs establish public ID 947512058 and a 639,169-byte release body;
12/12 original install/update selectors choose actual assets across six recipes.
Candidate queue updated; no operational enrollment, migration, push/repin or host
operation. 49 remains blocked; eight-source offline preparation is next. Earlier
wait-before-evidence notes are superseded by this explicit sequencing decision.

2026-10-31: [47 Brave eight-source offline contract](design/brave-eight-source-preparation.md)
adds a separate exact eighth-source candidate while preserving operational seven.
Measured replay: 8.26 MB tree, 509 KB ZIP and 45 KB temporary object growth within
unchanged caps. Six-file activation patch passes 22 affected tests in a temporary
copy. Retained identity/release evidence is committed locally as `104b06682`.
No push, collection, repin, recipe migration or host operation; 49 remains blocked.
Final eight-source preparation validation: [212 catalog tests and 22 isolated
activation checks pass](research/brave-eight-source-checks.json). Separate local
`prep/brave-eight-source` supplies the exact activation review candidate; remote
source/daily operation remain unchanged pending a separate rollout authorization.

2026-11-02: [47 remaining-batch offline preparation](design/remaining-appimage-preparation.md)
freezes 49 endpoints / 118 recipes and 48 distinct identity requests. All 236
original selectors and recipe fingerprints are retained; syntax and inventory
hash checks pass. Full 57-source activation needs a capacity decision under the
unchanged 300-second deadline. No metadata requests, source push, repin or host
operation; 47/49 remain partial.

2026-11-02: [Approved identity batch](research/remaining-identities-20261102-findings.md)
stopped at its first attempted transfer on local DNS failure (curl 6, zero response
bytes). No identity collected; 47 URLs unattempted. Failed evidence retained;
fresh network-enabled retry prepared, requiring scoped retry approval under the
stop-on-first-failure contract. No operational or host change.

2026-11-02: [Network-enabled identity retry](research/remaining-identities-20261102-network-findings.md)
verified 11 public identities (12 candidate release endpoints / 42 recipes), then
stopped on NaturalGroundingPlayer HTTP 301 without following it. Thirty-six
identity URLs remain unattempted. Offline evidence hashes, scope and descriptor
checks pass; no release requests, operational changes or host delivery.

2026-11-02: [Substantial AppImage batch](research/appimage-batch-20261102.md):
107 local recipe migrations, 214 unchanged selectors against 44 real responses,
and −7,196 production lines / −334,946 bytes including supporting changes.
Five endpoint exceptions preserve 11 legacy paths. Offline 52-source contract
keeps time/byte caps; activation/publication and host delivery remain separate.

2026-11-02: migration batch committed locally as `2496e90e4`;
[two-stage activation preparation](design/appimage-52-source-rollout.md) separates
52-source enrollment from the subsequent 107-recipe delivery. Current parent
9f4e356e validated/replayed; remote source/pin remain cc2ba588d. No remote mutation.

2026-11-02: [Four redirect identities / eight candidates](research/appimage-exceptions-20261102.md)
prepared offline after eight bounded public metadata GETs. Four exact original
aliases map to verified numeric public repositories; eight replacement recipes
remove 544 lines / 25,702 bytes. 37 affected tests and five candidate checks pass.
aarch64/tiddlydesktop selects an x86 asset and stays unchanged, alongside the two
payloader 404 paths. No 56-source activation, push, repin or host operation.

2026-11-02: User prioritizes migration speed beyond the original 124-recipe slice.
[67](issues/67-expand-appimage-migration-throughput.md) freezes 1,000 further
candidate replacements from a 2,549-recipe lexical pool; 732 exact endpoints,
730 identity requests, 67,776 static lines displaced. Syntax/patch checks pass;
metadata and actual assets remain unverified. Collector/publication capacity is
the next throughput boundary; the eight redirect leftovers are a side batch.

2026-11-02 continuation: [67 capacity audit](issues/67-expand-appimage-migration-throughput.md#capacity-audit-and-evidence-queue--2026-11-02-continuation)
adds an offline, fingerprint-checked 15-cohort evidence queue for all 1,000 paths.
Four focused checks pass, including a real storage replay proving that rotating
replacement manifests retires earlier sources. The 784-source union's synthetic
manifest exceeds the current parser cap; actual body capacity remains unmeasured.
Recorded conditional incremental/sharded alternatives pending actual metadata;
no production changes, source acquisition or operational delivery.

2026-11-02 substantial continuation: [67](issues/67-expand-appimage-migration-throughput.md#verified-identities)
now has 922 locally migrated recipes, 78 unchanged exceptions and exact metadata
for the full bounded acquisition queue. Recipe reduction: 62,630 lines / 2,927,077
bytes. Fourteen bounded shards retain the original 52 plus 667 new descriptors
under one atomic root with unchanged shell reader paths. Actual saved-body
ZIP/recomputation/Git replay passes; final focused runtime checks fix the discovered
`icalingua++` name rejection. All 82 installed-command container scenarios pass.
The 252-test catalog result predates the final focused additions/fix; retained logs
identify the one initial all-batch failure and its passing targeted replacement.
[Rollout package](research/appimage-next-large-batch-20261102/rollout.md) is ready
for the home-instruction push decision. No push, workflow switch, dispatch, repin
or host operation occurred; operational delivery remains unfinished.
