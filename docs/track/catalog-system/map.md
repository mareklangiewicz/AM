# Understandable catalog system and educational browser

Label: wayfinder:map

## Destination

An agreed system specification and dependency-linked implementation roadmap for
one transparent collection pipeline with simple rerun recovery, a coherent public YAML interface,
and excellent app browsing that also teaches users how the system works.
The route is complete when implementation can proceed without unresolved product,
contract, storage, compatibility or acceptance decisions.

## Notes

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

Start with [the planning brief](spec.md). It separates accepted requirements from
open designs and defines completion; it is not a finished implementation spec.
Answers live in their tickets. Update the brief to reference accepted answers as
the map advances; avoid copying whole resolutions into multiple documents.
No decision ticket is hand-resolved during charting.

Marek subsequently accepted name-first app-map references to repository YAML
files; the examples and remaining contract choices live in
[Choose public YAML contracts and revision consistency](issues/03-choose-public-yaml-contracts-and-revision-consistency.md#accepted-app-to-file-references--november-7-2026).
That broader ticket remains open.

This map coordinates the existing [release-catalog history](../release-catalog/map.md)
and [browser map](../catalog-pages/map.md); it does not replace their evidence.
[Choose the catalog browsing experience](../catalog-pages/issues/03-review-browser-experience.md)
continues to own the app-directory/detail/release layout verdict, A/B/C prototype
feedback and Vim-like navigation. Its existing claim is preserved.
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

## Not yet specified

Detailed field names, wire examples and schema documents will follow the public
contract and health-definition decisions. Do not invent a parallel browser model.

The final design may expose additional failure, credential or checkpoint lifecycle
questions. Ticket them when precise; interruption before confirmed publication
may lose runner-local acquisition and require repeating work, as accepted above.

Concrete experiments, measurements and implementation tickets depend on the
chosen storage and interfaces. Larger verified cohorts and rollout packages follow
measured compatibility/capacity gates, not an arbitrary target count.

Enrichment acquisition/cache/provenance details may need new decisions after the
educational prototype; existing metadata research remains evidence.
Search depth, all-releases exploration and chart interactions may expose further
questions after human prototype review.

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
