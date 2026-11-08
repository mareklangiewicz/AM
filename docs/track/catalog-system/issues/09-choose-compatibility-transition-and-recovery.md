# Choose compatibility transition and recovery

Type: grilling
Label: wayfinder:grilling
Status: resolved
Assignee: codex-compatibility
Blocked by: 03, 05, 06, 07, 08

## Question

How can the selected contracts, storage and pipeline replace the present system
without silently breaking existing shell/browser consumers or losing last-good data?

Specify producer/reader compatibility, ordered rollout, old pinned snapshot access,
checkpoint migration/invalidation, recipe/policy revision handling, concurrent
publication and rollback/recovery boundaries. Address public operational summaries
when collection/validation/publication fail independently.
Include the transition from the separately deployed prototype branch to the
accepted main-marek website-code home without losing preview/recovery capability.
Preserve AM app identities, numeric source identities, retained release IDs and
effective release observations. Avoid promising binary rollback from catalog rollback.

Include the accepted app-map transition from numeric values and source filenames
to explicit readable YAML paths, as recorded in
[Choose public YAML contracts and revision consistency](03-choose-public-yaml-contracts-and-revision-consistency.md#accepted-app-to-file-references--november-7-2026).
Cover source/app renames, old numeric-path consumers and old pinned snapshots;
do not silently require existing installed readers to understand the new map.

Compare a small reversible end-to-end summary/browser slice with alternatives.
Identify old code and operational procedures that can actually retire, evidence
that must remain, and unknowns needing a bounded rehearsal. Agree migration gates
and recovery ownership with Marek. This is a plan, not deployment authorization.

## Answer — November 8, 2026

Marek accepted the prepared migration and rollback plan with “yes.” The complete
proposal below is selected; its initial pending wording records its earlier status.
Use a small local end-to-end slice, temporary dual-format output from shared
acquisition, reviewed main-owned browser activation, separate installed-host
delivery and consumer-gated format-2 retirement at an agreed date.

Preserve each format's own merge/retention semantics during transition and compare
common facts losslessly, explicitly reviewing intentional selection differences.
Publish format 2, then format 3, then final status under separate exact-parent
checks; this is not atomic. Preserve already accepted writes on later failure.
Prepare one exact rollout/rollback package, reusing applicable evidence and focused
checks. Recover through checked pins, retained site/host before-images and validated
corrective direct-child publications, without history rewrites or binary-rollback
claims. The detailed gates and recovery ownership below apply.

Browser layout/acceptance and final measured system targets remain with their
owning tickets. This accepts the migration plan only: source push, remote channel
creation/publication, Pages activation and installed-host operations still need
the concrete authorization described in the plan. None occurs in this decision.

## Process steering — November 7, 2026

Consumer-scope clarification, November 9, 2026: Marek confirmed that there are no
unknown external readers/consumers. Retirement concerns the maintained consumers
only; no external-consumer discovery, compatibility notice or waiting period is
required. The earlier inventory receipt's external-reader limitation records what
that source scan measured, not an additional retirement gate. Maintained-consumer
migration, rollback and the agreed retirement date remain the accepted route.

Marek wants a substantially faster migration with less ceremony. Produce one
concrete cutover/rollback plan, reusing existing evidence and focused compatibility
checks. Batch material choices for review; select routine mechanics autonomously.
Avoid turning every rehearsal parameter into a human approval gate. Preserve
explicit push/deployment authorization boundaries.

## Prepared cutover and rollback proposal — November 8, 2026

Pending Marek's decision. Planning only, with no push, workflow dispatch, ref
creation, Pages deployment, installed-host change or yadm operation. Reuse the
existing catalog, collector modules, original-template/family evidence and A/B/C
prototype; do not start another migration implementation or layout selection.
Source inspected at `b0d01f2d1`; existing receipts remain historical evidence.

### Recommended route: a small end-to-end slice, then staged activation

1. Implement the shared format-3 contract/reader and collect/validate/publish
   interfaces locally. From one acquisition/normalized input produce separate
   format-2 and format-3 candidates, validating each under its own rules. Start
   with saved evidence; add the independent final-summary/status path and a small
   browser health/context slice before broad UI polish. Existing format-2 production
   and installed readers continue unchanged while these candidates are private.
2. Move reviewed browser code from the preserved prototype into main-marek,
   retaining all A/B/C variants, native/Vim navigation and preview capability.
   Main owns maintained website source; use a reviewed public asset allowlist and
   existing same-repository Pages hosting. The current workflow reads the moving
   `prototype/catalog-pages` branch even when dispatched from main: replace that
   with an exact approved main source revision at the eventual site switch. Do
   not merge the research/tracker tree wholesale into the public artifact.
3. Complete focused compatibility, scale/history and real-browser checks below.
   Prepare one reviewable rollout package containing exact code/policy/schema
   revisions, candidate pins, workflow/ref changes, known consumer inventory,
   retained last-good catalog/site artifacts and rollback commands. Ask for the
   concrete source push and remote publication/deployment operations together;
   authorization for that package does not include installed-host changes.
4. On separate rollout authorization, introduce `release-catalog-v3` and
   `catalog-status-v1`; keep `release-catalog` serving format 2. During transition,
   use one collection pipeline and acquisition to maintain both output formats.
   Publish format 2 first while old consumers depend on it, then format 3, then
   final status. Check each exact parent separately and record each actual outcome;
   the sequence is not atomic. A confirmed conflict stops further catalog writes;
   never undo an already accepted earlier write to pretend both channels advanced
   together. Status distinguishes compatibility publication from target C/S.
5. Activate the main-owned browser against format 3/status after the checked
   channels are usable. Capture exact deployed source/artifact and readback
   evidence. Then migrate maintained shell/Lua consumers in separately scoped
   deliveries; installed-host recipe/module/config refresh needs its own explicit
   authorization and before-images. Do not bundle binary updates into this work.
6. Retire format-2 publication only after inventoried maintained consumers have
   migrated, rollback is rehearsed and Marek agrees the retirement date. Publish
   the compatibility/old-pin policy before freezing the old channel; do not leave
   old consumers silently reading ever-staler data. Retain old refs/history and
   reader evidence; remove duplicate active orchestration and the old monolithic
   CLI after callers migrate. The prototype remains preserved for comparison and
   rollback, with automatic prototype deployment disabled at the site switch so
   a later prototype push cannot overwrite the main-owned site.

This is faster than a one-shot producer/browser/installed-host switch because the
working old channel protects existing clients while one small new path is proved.
A permanent pair of independent collectors would duplicate acquisition and drift;
the transition uses shared acquisition and temporary dual output, not two systems.
No arbitrary number of live runs or repeated per-app approval gates is required.

### Compatibility invariants and focused gates

Format 2 retains numeric app references/filenames, whitelist, grammar, reader and
existing retention semantics while it remains supported. Format 3 uses the
accepted stable readable paths, numeric identities, compact encodings and
32-plus-stable/exact-tag rules. Build each merge from its own exact parent; do not
truncate legacy retained records by translating the already-pruned v3 output.
The shared normalized acquisition input, not an incidental wire projection, feeds
both. Account for the temporary dual-output resource cost at the supported scale.

Compare common retained records losslessly: app/source/release/asset IDs,
effective observations, URLs/media types, settings and selection policies. List
intentional v3 retention/same-tag supersession differences explicitly; do not
claim whole-set equivalence across those policy changes. Check maintained
consumer selections against saved evidence. Any changed selection required by
retention/policy must be reported and reviewed, not hidden as encoding compaction.

Require shared positive/negative grammar/schema fixtures, shell/browser exact
integer and URL/MIME round trips, identity/reference validation, pinned reads,
unknown-version refusal, source-isolated failures and exact-parent/ambiguous-write
cases. Include the seed-plus-three offline rehearsal and the representative
thousands-of-apps/history check from storage/roadmap. Reuse valid existing evidence;
rerun only affected tests, not every historical per-app payload/lifecycle suite.

Require actual browser fetch/CORS/DOM, pin/race/cache consistency, mobile/native
and Vim keyboard/focus/accessibility, stale/partial/unknown states and review-link
checks. Parser/Node results are insufficient. Browser layout, grouping verdict
and final delivery targets remain with the existing claimed browser tickets;
this route does not resolve them. Ticket 10 consumes those verdicts before the
final implementation roadmap is declared ready.

Allocate readable names by verified numeric identity; change all new-format
references consistently. Old numeric filenames remain valid in old snapshots.
App/source renames follow the selected registry rules and do not retarget old
pins or silently change stable/nightly policy. Bind each classification/recipe
link to its own architecture/path/source pin, not the data commit. Preserve shared
observations and overrides exactly. Discard incompatible runner-local candidates/
validation receipts and reacquire/revalidate; no checkpoint migration service is
needed under the accepted rerun recovery model.

### Rollback and recovery ownership

Marek authorizes remote activation and installed-host delivery; the implementing
agent prepares/rehearses the package and records exact results. On failed gates,
stop activation and keep the currently supported channel/site. During live
activation, stop further rollout on unknown publication, invalid data, broken
maintained consumer selection or failed browser/health checks; first establish
which writes actually succeeded. Attempt a truthful final summary independently.

Restore browser deployment/configuration from the retained exact last-good source
and artifact. Readers may be explicitly pinned back to a checked old catalog while
investigating; never mix documents from old/new pins or silently fall back across
formats after validation fails. Preserve both data refs and their history. Resume
publication with corrected code against the actual current parent; if content
restoration is required, validate and publish it as a new direct child with truthful
provenance and unchanged effective observation times. No force rewind/history
rewrite or automatic merge. A failed status update leaves the old last-reported
summary; it does not justify rolling back valid catalog facts.

Restore separately delivered shell/config/module before-images only within their
explicit delivery scope. Metadata/recipe rollback does not roll back installed
binaries or prove historical downloads remain available. Keep recovery evidence
and historical pins even after obsolete active code is retired.

Decision requested: accept temporary shared-acquisition dual-format publication,
main-owned browser activation, separate installed-host delivery and explicit
consumer-gated format-2 retirement, with the rollback boundaries above. Specific
commit pins, measured operating values and ordinary command flags belong to the
concrete implementation/rollout package, not another product approval round.
