# Shell consumer and one simplifying recipe/updater migration

> **2026-10-28 ownership correction:** [Ticket 29](29-respect-configured-catalog-repository.md) supersedes
> this record's fixed-upstream ownership assumption. This fork's catalog follows
> AMREPO and must not fall back to upstream AM. Upstream acceptance/publication
> is not a prerequisite for this fork. Results and archived bytes below retain
> their historical source/revision meaning; they do not define current policy.

Type: task
Status: resolved
Triage: ready-for-agent

## Accepted direction and next-session scope

2026-10-27: Marek explicitly prioritized simplifying AM, removing independent
proxy/source trust, avoiding a new consumer language such as Python, and keeping
upstream-facing recipe diffs small and simpler. He agreed to start implementation
next session. This ticket is the next open frontier; do not implement it merely
while updating the tracker.

The authoritative acceptance criteria are below, alongside the
[accepted adoption direction](../spec.md#accepted-adoption-direction-2026-10-27).
They supersede ticket 22's proposed Python runtime/zipapp packaging step, not its
findings about actual AM distribution/update behavior. Python collection/validation
in CI may stay; the Python consumer and Obsidian --catalog-version branch are
reference/test scaffolding, not the final installed consumer architecture.

## Concrete work

1. Implement a small shared shell catalog reader using AM's existing supported
   utilities. Audit the actual mandatory/optional dependency set first: no new
   Python runtime, jq dependency, checkout requirement or runtime download service.
   Make the reader usable from both the installer and generated standalone updater,
   without sourcing all of APP-MANAGER or depending on a repository-relative path.
   Reuse existing AM shell distribution/ownership mechanisms where practical.
2. Make the published metadata easy for that reader to consume. A small validated
   shell-readable lookup table alongside unchanged original response JSON is a
   candidate; choose the smallest safe format in the implementation, rather than
   duplicating the Python index parser in shell. Do not source/eval catalog data.
   Preserve aliases, exact descriptors, hashes and measured observation times.
   Keep one canonical publication snapshot; any lookup table must be generated and
   validated from it atomically, not maintained as another drifting data source.
3. Share commit pinning, freshness, integrity, bounded reads and clear refusal in
   that reader. Preserve the accepted inclusive 24-hour boundary, future/unmeasured/
   unavailable/retired/removed-alias refusals and exact commit/request/body stale
   acceptance. Read index/lookup and selected body from the same full commit; no
   upstream/proxy fallback on failure and no blanket stale override. Do not trade
   away these checks just to achieve a URL-only substitution.
4. Choose one actual app (Obsidian is the existing test case), inspect its real
   installer and generated updater, then migrate their metadata read with a small
   shared-helper call while keeping their existing selection filter initially.
   Aim for a one-line read substitution at each call site, not a new flag/mode,
   Python path, per-app freshness branch or duplicated fallback code. Replace or
   retire the checkout-only --catalog-version scaffolding where it is superseded;
   preserve its evidence and add checks for the intended simpler path.
5. Keep foreground failure propagation and no mutation before successful preflight.
   Address the actual suppressed updater output/success reporting and optional
   appimageupdatetool bypass identified in ticket 22 without adding a per-app
   framework. Do not execute saved installer text to discover filters. Exercise the
   source/generated updater with temporary roots and stubbed install/download
   operations; do not run an installer or migrate installed state in this step.
6. Inventory the proxy rewriting, API quota probing and API-key/token injection
   displaced by this migration. Remove proven-unused paths in the bounded slice;
   preserve still-used behavior for unmigrated callers. Record remaining cleanup
   by actual callers rather than declaring the whole proxy/auth subsystem obsolete.

## Trust and adoption criteria

- **Corrected by ticket 29 (2026-10-28):** follow configured AMREPO. This fork
  reads its own mareklangiewicz/AM publication; upstream installations would use
  their own selected repository. Missing/unsupported source or catalog refuses
  without switching to upstream AM. Upstream adoption is not a fork-use dependency.
- Download binaries from original upstream URLs; do not introduce a binary mirror.
  Users still trust GitHub, AM maintainers and publication code. A same-repository
  catalog avoids an independent operator but does not eliminate metadata trust or
  provide independent upstream binary authenticity.
- Keep recipe diffs easy to review and reduce total client complexity, not merely
  conceal a large new runtime/framework behind a short helper call. Document the
  helper/format cost and what existing code/dependencies can actually be removed.
- Stage an upstream-friendly slice: one shared reader, the minimal publisher-format
  addition and one app plus its generated updater; keep unrelated installer cleanup
  and later fleet migration out of the initial change.

## Verification and done boundary

Use retained catalog/publication bytes for the bulk of verification. Check shell
syntax and the behavior of the actual shared reader/recipe/generated updater:
pinned exact bytes, unchanged selection, stale/future/integrity refusal, missing
helper/unsupported state, visible nonzero failure, no implicit fallback, no extra
trust host and no installer/update mutation before acceptance. Test supported
shell/tool assumptions and invocation outside a checkout. Audit actual diff size,
dependency changes and net removed/added client logic; do not use test counts or
one-line recipe diffs alone as proof of simplification.

Prepare any necessary public-read/publishing validation within a concrete bounded
plan; no schedule, fleet expansion, installed migration or automatic workflow run
is implied by this ticket. Do not run new collection just to answer shell/filter
questions already covered by saved evidence. Record results and remaining adoption
limits here and in the map. This ticket is implementation work, not another
throwaway prototype or Python packaging exercise.

## Inputs

- [22 findings and superseded recommendation](../design/obsidian-update-adoption.md)
- [20 opt-in filter evidence](20-obsidian-opt-in-filter.md) and
  [21 actual pinned read](21-obsidian-live-read.md)
- [Consumer reference](../design/catalog-consumer.md) and
  [delivery](../design/catalog-delivery.md)
- tools/catalog-collector, programs/x86_64/obsidian, APP-MANAGER and modules/install.am

## Answer

Implemented the bounded shell-first slice. See [implementation, format, dependency
and caller audit, tests and public validation plan](../design/shell-consumer.md).
`modules/catalog.am` reads the atomically derived lookup and one pinned original
body; Obsidian's ordinary recipe and newly generated standalone updater use it
with their unchanged asset filter. AM embeds its owned module path and runs one
marked app in the foreground before legacy update mutations. Refusals propagate
without fallback or success reporting; optional upstream binary-digest verification
remains after successful managed update. Python query scaffolding and the updater's
appimageupdatetool bypass are removed from this recipe.

At the ticket-23 source revision the publication target was incorrectly fixed to
upstream ivan-hc/AM. Ticket 29 corrects that defect; this fork uses AMREPO ownership
and requires no upstream publication/acceptance. The implementation evidence below
is historical.
No host installation/migration, workflow dispatch, publication, schedule or release
collection occurred. Only temporary app roots and stubbed app operations ran.
The first-app client diff is +139 net lines, including the 96-line shared reader;
there is no claim of a net line-count reduction or broad portability proof.
Remaining legacy proxy/quota/token callers are identified in the implementation
record rather than removed speculatively.

Validation: **89 collector/storage/delivery/consumer/recipe tests passed** on the
final implementation; `bash -n` for APP-MANAGER/install.am and `sh -n` for the
reader/recipe passed. ShellCheck passed for the reader and at warning severity
for the recipe (its two existing informational findings are unchanged). Diff and
new local documentation links were checked. No live API experiment was run;
GitHub's public API documentation was consulted for the SHA response media type.

## Review correction

The initial passing suite missed manager-entrypoint recovery and preflight gaps.
[Ticket 25](25-review-shell-adoption.md) records four independently reviewed spec
findings and their fixes, including real installation-dispatch refusal/recovery
checks. The initial +139 client-line measurement is historical: after fixes and
preserving the manager's debug option, the current bounded slice is **+179 net
client lines**. These changes do not prove the broader simplification goal or
live/upstream readiness; those claims remain intentionally limited.
