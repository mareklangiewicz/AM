# Understandable catalog system and educational browser

Label: wayfinder:map

## Destination

An agreed system specification and dependency-linked implementation roadmap for
one transparent collection pipeline with simple rerun recovery, a coherent public YAML interface,
and excellent app browsing that also teaches users how the system works.
The route is complete when implementation can proceed without unresolved product,
contract, storage, compatibility or acceptance decisions.

## Notes

Planning completed November 8, 2026: Marek accepted the final system targets and
[five-slice implementation roadmap](issues/10-agree-system-acceptance-and-implementation-roadmap.md#answer--november-8-2026).
Start with the accepted [system specification](spec.md), then implementation
11–15 below. No implementation is started by this planning acceptance. Normal
updates at thousands of sources must fit the measured design with headroom.
Hourly quota-aware batches explicitly supersede the earlier twice-daily target;
actual production settings remain unchanged by these documents.

Latest capacity steering, November 8, 2026: normal full-catalog updates at thousands
of apps must not predictably hit internal resource limits. Size safeguards for the
supported workload with headroom; existing numerical caps are baselines to reassess,
not fixed design ceilings. Preserve correctness and honor real service/host
constraints. The [accepted capacity target](issues/05-choose-scalable-snapshot-and-history-storage.md#accepted-capacity-target-normal-full-catalog-updates--november-8-2026)
supersedes requiring every rehearsal to fit today's caps. The saved 500-source
rehearsal remains useful but cannot alone qualify the intended scale. No production
limit change or expanded enrollment is authorized by this planning clarification.

Latest process steering, November 7, 2026: Marek wants this migration substantially
faster and with less ceremony than the previous one. Agents choose routine
experiment/implementation mechanics and consolidate reviewable changes; do not
ask for approval of every small parameter. Ask about material product, contract,
scope or rollout decisions. Reuse existing evidence and run checks tied to concrete
risks, without speculative machinery or repeated unrelated suites. This does not
authorize implementation, pushes or deployment beyond the existing planning scope.

Git is a firm project foundation for transparency, simplicity and trust. The
[accepted Git foundation](issues/05-choose-scalable-snapshot-and-history-storage.md#accepted-git-foundation--november-7-2026)
constrains storage/capacity planning to Git-based designs; another backend is not
an option to revisit after measurements. The [storage resolution](issues/05-choose-scalable-snapshot-and-history-storage.md#answer--november-8-2026)
selects the processing/read/history approach and a small future rehearsal; actual
capacity and supported operating defaults remain to be measured.

Latest steering, November 7, 2026: prioritize simplicity of implementation.
Marek rejected the separate checkpoint-store proposal, permits relaxing recovery
guarantees, and requests simple questions before further design decisions.
The resolved recovery ticket records Marek's live answers: lost unpublished work
may repeat; oldest-first batches retry on later scheduled runs; discovery stays
manual; one collection runs at a time without automatic cancellation; publication
conflicts stop rather than merge. Public health attempts a final summary for every
normal outcome, with no public start record. A run or reporting failure may leave
no report: show the previous timestamped “last reported run”, never imply latest
attempt coverage. Link to the specific Actions run and recent collection runs;
Actions may require sign-in, while public summaries do not. Prior separate-store/
durability/fencing/gate and start/finish designs are superseded. Ask simple questions
before further decisions; implementation simplicity remains the priority.

Marek confirmed this destination and the audience on November 7, 2026:
app discovery leads; Linux newcomers and experienced AM users are both served;
maintainers get deeper explanations. Education follows real app examples, with
a short system overview and progressive access to detail. Public health is
understandable without Actions logs or credentials. Accessible mobile/desktop
browsing, keyboard navigation, shareable links and truthful stale/partial/unknown
states are required. Guided lessons, quizzes and simulations are optional later work.

This is planning. No production implementation, workflow dispatch, enrollment
increase, recipe migration, installed-host change or deployment is part of charting.
Commit completed planning locally; ask Marek before pushes and deployment.
Consult wayfinder, grilling and domain-modeling for decision sessions; use
prototype for human-reviewed experience exploration and research for facts.
Do not decide architecture by treating a research recommendation as human acceptance.

The [system specification](spec.md) consolidates accepted requirements and links
the owning decisions; executable field/schema details and measured implementation
results follow in the implementation tickets. Answers live in their tickets;
avoid copying whole resolutions into multiple documents.

Marek subsequently accepted name-first app-map references to repository YAML
files; the examples and accepted contract live in
[Choose public YAML contracts and revision consistency](issues/03-choose-public-yaml-contracts-and-revision-consistency.md#accepted-app-to-file-references--november-7-2026).
That broader ticket is resolved.

This map coordinates the existing [release-catalog history](../release-catalog/map.md)
and [browser map](../catalog-pages/map.md); it does not replace their evidence.
[Choose the catalog browsing experience](../catalog-pages/issues/03-review-browser-experience.md)
continues to own the app-directory/detail/release layout verdict, A/B/C prototype
feedback and Vim-like navigation. Its accepted result is recorded there.
[Agree the implementation route and acceptance criteria](../catalog-pages/issues/04-agree-delivery-and-acceptance.md)
continues to own browser-specific delivery/acceptance decisions; the final system
ticket consumes its result. New tickets own cross-system and educational decisions,
not duplicate verdicts on those existing questions.
[Scale catalog coverage to GitHub-backed apps](../release-catalog/issues/138-scale-github-catalog-coverage.md)
remains the execution/evidence record for broader enrollment; its next storage and
pipeline architecture choices are coordinated here before further expansion.

Tracker adaptation: child issues live in this directory's issues/; Type and Label
express wayfinder type, Status and Assignee express claims. No triage labels.
Blocked by entries are same-directory ticket numbers or explicit relative issue
paths for cross-effort dependencies, resolved from the ticket's directory.
The frontier is open, unassigned children whose blockers are resolved, ordered
numerically; also inspect the linked browser work without taking its existing claim.
For a claim set Status: claimed and Assignee before work. Append Answer on
resolution, set Status: resolved, and add one named link below. Research may resolve
during charting; other decisions require their subsequent session and live exchange.
Research uses isolated local branches, committed reports and exact context pointers;
branches are not merged or pushed automatically (home push guidance applies).

## Decisions so far

- [Establish the supported pipeline and operating constraints](issues/01-establish-supported-pipeline-and-operating-constraints.md): source audit identifies reusable seams, missing automatic resume/public failure summaries and official operating constraints; linked report is on an isolated local research branch, not an accepted architecture.
- [Choose contextual education and health navigation](issues/02-choose-contextual-education-and-health-navigation.md#answer--november-7-2026): accepted contextual explanations, a short system overview and dedicated public health destination, with observation age and known refresh failures visible directly.
- [Choose public YAML contracts and revision consistency](issues/03-choose-public-yaml-contracts-and-revision-consistency.md#answer--november-7-2026): under explicit decision delegation, selected separate pinned catalog/status channels, format-3 boundaries and lossless encodings, revision/race rules, editor schemas and format-2 compatibility gates.
- [Choose durable progress and fair scheduling](issues/04-choose-durable-progress-and-fair-scheduling.md#answer--simplified-recovery-and-final-reporting-november-7-2026): live answers select simple reruns, oldest-first scheduled refresh, manual discovery, single active collection and stop-on-conflict publication; final summaries describe only the last reported run, with investigation links.

- [Choose scalable snapshot and history storage](issues/05-choose-scalable-snapshot-and-history-storage.md#answer--november-8-2026): exact-parent incremental Git snapshots, lazy pinned reads, accepted source retention and run-local cleanup; seed plus three offline update cases and a later representative scale/history check. Existing numerical caps are baselines, not fixed ceilings; no capacity claim or implementation authorization.

- [Choose evidence-bound recipe classification and provenance](issues/06-choose-evidence-bound-recipe-classification-and-provenance.md#answer--november-8-2026): accepted four evidence-bound labels, architecture-specific immutable review links and revalidation of changed inputs; enrollment, recipe availability, support and authenticity remain separate.

- [Choose one reusable collection interface and permissions](issues/07-choose-one-reusable-collection-interface-and-permissions.md#answer--november-8-2026): accepted explicit collect/validate/publish CLI, shared live/offline pipeline, collection-only Action and read-only acquisition plus write-enabled publisher/finalizer jobs.

- [Choose truthful health summaries and bounded statistics](issues/08-choose-truthful-health-summaries-and-bounded-statistics.md#answer--november-8-2026): accepted stage-specific outcomes, explicit unknowns/denominators, 64 summaries / 8 full-detail reports / 90 daily aggregates, and freshness/resource/history views with coverage gaps.

- [Choose compatibility transition and recovery](issues/09-choose-compatibility-transition-and-recovery.md#answer--november-8-2026): accepted shared-acquisition dual-format transition, main-owned browser activation, separate installed-host delivery, consumer-gated format-2 retirement and pinned/corrective-publication rollback. Remote operations remain separately authorized.

- [Agree system acceptance and implementation roadmap](issues/10-agree-system-acceptance-and-implementation-roadmap.md#answer--november-8-2026): accepted 5,000-app/source reference workload, 12-hour healthy-source refresh through hourly batches, 25% measured headroom and 12-month history horizon; five dependency-linked implementation slices.

## Implementation route

Planning is complete. Marek started local implementation on November 8; tickets 11–12
are resolved locally, and ticket 13 is resolved with [recorded evidence and accepted limitations](issues/13-integrate-main-owned-catalog-browser.md#answer--november-8-2026). Ticket 14 is claimed for qualification. Routine implementation mechanics follow the accepted
spec without repeating product interviews. Remote operations keep their explicit
approval boundaries.

| Ticket | Depends on | Deliverable |
| --- | --- | --- |
| [11 resolved](issues/11-implement-contracts-readers-and-collection-interface.md) | 10 | Contracts, strict readers and shared collection/validation interface; [focused local acceptance](implementation-11.md), with format 2 preserved. |
| [12 resolved](issues/12-implement-incremental-publication-and-final-health.md) | 11 | Incremental Git publication, final health and isolated workflow permissions; [local acceptance and shared rehearsal](implementation-12.md), with one explicit saved-source refusal. |
| [13 resolved](issues/13-integrate-main-owned-catalog-browser.md) | 11, 12 | Main-owned A/B/C browser and real-browser checks; device/comprehension deferred and timing misses retained by Marek's explicit acceptance. |
| [14 claimed](issues/14-verify-scale-compatibility-and-rollback.md) | 11, 12, 13 | Shared scale/history, compatibility and rollback evidence. |
| [15](issues/15-prepare-reviewed-catalog-rollout-package.md) | 14 | Exact rollout/rollback package for explicit remote-operation review. |

Latest implementation evidence, November 8: Chromium desktop/narrow and Firefox
checks pass; physical-device/comprehension limits remain with 13. Independent
[scale preflight](preflight-14.md) exposes an oversized central provenance document
at 5,000 apps, corrected by Marek’s accepted per-source partition layout.
The same preflight records partition-size checks, synthetic scheduling, current v2 consumer inventory and
corrective old-pin recovery. Ticket 14 was then open/unclaimed; these were preparatory
results rather than full workload/history qualification.
The [schema-transition follow-up](preflight-14.md#collectorschema-revision-transition--november-8-2026)
also reproduces and fixes a collector/publisher HEAD default that could publish
retained source documents the lazy browser refused. Mixed bindings now refuse
before catalog publication; ordinary unchanged-schema runs retain the trusted
parent binding.

## Execution evidence and optional follow-ups

November 9 capacity review: the [operating recommendation](qualification-14.md#capacity-recommendation-for-review--november-9-2026)
recommends holding current coverage while correcting dual-output history and
full-path throughput. A narrow v2 packing sample exposes a 92.012 GB annual
dual-output scenario, with explicit nonstationarity and payload/status sensitivities.
The proposed storage envelope is unaccepted and unqualified; no accepted coverage,
refresh or compatibility guarantee changes. Ticket 14 remains claimed.

All planning decisions are resolved. Actual processing/capacity, live acquisition,
workflow/publication, browser/performance/accessibility and educational-comprehension
claims require the scoped implementation/rollout evidence above. A synthetic count
alone does not qualify real sources or acquisition capacity.

Executable schemas and wire examples implement the accepted contracts, without a
parallel browser model. Additional enrichment, deeper global search, guided lessons
or new charts remain optional follow-ups unless a concrete implementation finding
requires a material decision. No speculative recovery infrastructure is needed.

## Out of scope

Executing the implementation roadmap during charting; deployments and pushes
without separate authorization; app installation/update, installed-host changes,
yadm pointer bumps and routine recipe migration.

Accounts, ratings, submissions, binary hosting, a broad plugin framework without
a second concrete use case, non-GitHub source adapters, and an upstream integration
commitment. Reusability must not turn GitHub release facts into a universal schema.

Mandatory tours, quizzes and simulations for the first complete experience.
They can become a separate effort after contextual education is validated.

Reopening accepted facts/client-selection and retained-observation semantics by
accident. Any deliberate incompatible change needs an explicit decision and migration.
