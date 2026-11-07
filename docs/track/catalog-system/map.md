# Understandable catalog system and educational browser

Label: wayfinder:map

## Destination

An agreed system specification and dependency-linked implementation roadmap for
one transparent, resumable collection pipeline, a coherent public YAML interface,
and excellent app browsing that also teaches users how the system works.
The route is complete when implementation can proceed without unresolved product,
contract, storage, compatibility or acceptance decisions.

## Notes

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

## Not yet specified

Detailed field names, wire examples and schema documents will follow the public
contract and health-definition decisions. Do not invent a parallel browser model.

The final design may expose additional failure, credential or checkpoint lifecycle
questions. Ticket them when precise; interruption recovery must include the window
between durable acquisition and accepted publication.

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
