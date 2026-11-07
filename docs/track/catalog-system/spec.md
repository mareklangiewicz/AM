# Planning brief: a catalog people can use and understand

Status: accepted product requirements; architecture and implementation sequence open.
Canonical decision index: [Understandable catalog system and educational browser](map.md).

## Outcome and audience

A Linux user can find an app, understand what is available for their platform,
inspect releases and assets, and understand what AM would execute or why an
installation choice is unavailable. A curious user can follow the same app from
upstream facts through observation, client selection and recipe execution.
A maintainer can understand and operate the supported collection pipeline from
one short overview, with detailed evidence behind links.

App discovery is the primary journey. Contextual explanations and a short system
overview serve newcomers without obstructing experienced users. Public catalog
health explains what succeeded, what failed, what remains unattempted and what
is unknown. Visitors need no GitHub token.

This brief captures Marek's confirmed direction, not acceptance of a particular
layout, new schema or storage mechanism. The map's questions must settle those.

## Accepted requirements

### Browse and learn through real apps

Preserve searchable app discovery, app/release detail, all upstream assets,
platform matching and shareable links. Distinguish an inferred platform match,
AM installation support and catalog-only inclusion. Stable/nightly identities
sharing a numeric source must not be silently collapsed.
Reuse the existing browser prototypes and preserve all three until Marek chooses.
Maintain Vim-like navigation alongside native keyboard operation.

Offer progressive explanations of upstream source → observed release →
client selection → installation recipe, with a revision-bound trail where facts
permit it. Do not imply this whole trail exists for catalog-only or unknown cases.
Explain credentials, whose quota maintenance consumes, installation execution,
trust boundaries, freshness and partial coverage in plain language.
A shared installer does not establish binary authenticity or safety.

Recipe presentation must use evidence-bound classification with an explicit
unknown state. Unknown is not custom. Custom does not mean malicious.
Custom recipes need a prominent “Review installation recipe” link to the exact
revision; the provenance decision must settle architecture/path and snapshot
relationships before any label or review link is asserted.

Desktop, mobile, accessibility and keyboard behavior are acceptance dimensions.
Browser tests must exercise real DOM, fetch/CORS, focus and interactions;
parser/Node tests alone do not establish these.

### Publish a coherent public YAML interface

Use simple versioned YAML contracts within the supported grammar for browser-facing
facts, provenance, limits/policy, job summaries, progress and bounded statistics.
Do not require visitors to scrape logs, supply credentials, or build a competing
model from unrelated revisions. Publish only sanitized, explicitly allowed fields.

Keep latest attempt, latest successful publication, source collection time and
individual release observation time distinct. A failed/partial attempt cannot
freshen retained data. Make absent, unavailable and unmeasured information explicit.
A file cannot include its own enclosing commit hash; the consistency decision
must define pin relationships rather than using a self-reference.

The existing reader's path whitelist and domain validation are compatibility
constraints. Separate supported YAML grammar from domain schemas without weakening
catalog validation. Do not add health files to the publication tree by assumption.

### Collect once, checkpoint and resume

Evolve useful existing scheduling, retained merges and discovery checkpoints.
One supported pipeline must support saved-response replay, collection/preflight
and explicit publication responsibilities. Publication is not an implicit side
effect of a general collection action.

Keep discovery/identity verification distinct from release refresh. Persist useful
progress during a run, recover completed work after ordinary interruption, isolate
source failures, and apply explicit request/byte/time/document/storage budgets.
Use safe quota reserves, recorded stop outcomes and controlled retry/backoff.
Define fairness between enrollment discovery and freshness maintenance.
An enrolled identity is not proof of successful collection or publication.

Choose scalable reads/writes, checkpoint storage and bounded retained/history
behavior from measurements. Deleting files from a Git tree does not erase history.
Do not solve capacity by merely raising ceilings. Preserve the last good catalog
through validation failure and exact-parent publication conflicts.

### Keep the core understandable and reusable

Target source adapter → normalized records → validation/merge → YAML output,
with explicit scheduling, budgets, checkpointing, credentials and publication
boundaries. Reuse core code for local evidence and workflow acquisition.
Keep GitHub/domain schemas explicit and avoid speculative plugin abstractions.
After the interface is settled, specify a thin collection Action and consider a
reusable orchestration workflow only where it removes duplication.

Preserve supported shell/Lua consumer requirements; installed AM readers remain
shell-based without a new Python/jq runtime requirement. No recipe execution or
app payload execution is allowed for public metadata collection.

### Show operational health truthfully

Start with successful/failed/unattempted sources, source observation ages,
requests/bytes/duration against configured limits, snapshot/history growth and
meaningfully measurable deferred work. Include definitions and measurement times.
Source ages cannot substitute for retained-release freshness.
Distinguish configured limits, observed usage and unverified capacity.
Bound statistics and show gaps; do not interpolate missing success.

## Existing decisions and evidence to preserve

- [Publish normalized release facts; clients select releases](../../adr/0001-catalog-facts-and-client-selection.md).
- [Merge scoped collections into retained release observations](../../adr/0002-retained-release-observations.md).
- [Choose the Pages home and existing-site coexistence](../catalog-pages/issues/05-choose-hosting-and-coexistence.md):
  same-repository Pages, website code on main-marek, lazy YAML reads at one exact
  catalog pin. Generated/copied indexes are not the accepted starting approach.
  If measurement requires revisiting it, do so explicitly.
- [Choose the catalog browsing experience](../catalog-pages/issues/03-review-browser-experience.md):
  deployed A/B/C prototype and keyboard iteration are evidence, not a layout verdict
  or real-browser acceptance result.
- [Catalog operation](../../catalog-operating-policy.md),
  [collector entry points](../../../tools/catalog-collector/README.md),
  [format 2](../../catalog-format-v2.md), and
  [domain language](../../../GLOSSARY.md) describe the current supported system.
- [Establish the supported pipeline and operating constraints](issues/01-establish-supported-pipeline-and-operating-constraints.md)
  links the source-audited short overview and current official constraint table;
  read its exact report context with git show. Its findings are evidence for the
  open decisions, not acceptance of the target architecture.

Local planning baseline observed November 7, 2026: clean main-marek at a149fe60a.
Recorded publication: 509 apps / 500 verified sources at
cbda9fb78ce4a6f29bdabd63d57f3c0085e8744f.
[Real 500-source publication](../release-catalog/research/next-500-publication.md)
measured 500 attempts, 341,439,276 response bytes, 518.95 seconds collector
command, 63,690,470 YAML bytes and a 1,372,340-byte largest document.
This is historical evidence, not a fresh remote-head or health check.

Recorded profile: 500 attempts hourly; 512 MiB/run; 900-second cooperative
acquisition; 30-minute job; 16 MiB/response; 2 MiB/document; 1,024 reader
files; 256 MiB local history guard; 48-hour selected-release freshness.
Thousands of sources remain unqualified. Quota headers observed 5,000 while the
documented planning baseline was 1,000/hour; do not infer a durable entitlement.
The research ticket rechecks official facts before new operating decisions.
No natural hourly-trigger success is established by these planning reads.

## Completion and handoff

The final specification links each accepted design to its owning resolution,
defines public contracts and consistency, progress/recovery, storage/retention,
credentials, reader compatibility, browser/learning behavior and recipe provenance.
It includes realistic successful, partial, failed, stale, unknown and interrupted
scenarios, plus migration/rollback and exact-parent conflict behavior.

The roadmap then divides implementation into dependency-linked, independently
reviewable slices with behavior-based acceptance, evidence needs and rollout gates.
Prefer a small end-to-end summary/browser slice when decisions support it; do not
lock that sequence before the interfaces and compatibility are settled.
Set concrete performance/accessibility/capacity targets with Marek, based on
measurements rather than invented promises.

A new maintainer should need this brief, the eventual short overview and named
decision links to understand the system; historical receipts remain drill-down
evidence rather than required onboarding. Implementation tickets are created after
their prerequisite decisions; this map initially holds decision tickets only.
