# Implement incremental publication and final health

Type: task
Label: implementation:task
Status: open
Blocked by: 11

## Outcome

The shared pipeline creates validated incremental candidates and explicitly
publishes catalogs/status, with isolated acquisition and publisher permissions.
Provide the small saved-evidence collection → candidate → final-health slice.

## Accepted inputs

[Storage](05-choose-scalable-snapshot-and-history-storage.md),
[interface](07-choose-one-reusable-collection-interface-and-permissions.md),
[health](08-choose-truthful-health-summaries-and-bounded-statistics.md),
[cutover](09-choose-compatibility-transition-and-recovery.md),
[targets](10-agree-system-acceptance-and-implementation-roadmap.md#answer--november-8-2026).

## Work and acceptance

- Reuse exact-parent Git blobs/index entries for untouched sources without routine
  full decoded-tree materialization. Validate changed bytes and whole-candidate
  references. Bind trusted-parent evidence to exact commit/rules; fall back to
  full validation when evidence is absent/untrusted or rules change. Stream where
  practical and measure the fallback; do not create a durable trust/recovery store.
- Complete explicit publication, exact-parent conflict refusal and confirmed versus
  ambiguous remote outcomes. In local tests model remote operations with disposable
  repositories/transports. Preserve last-good state, do not merge/retry automatically.
- Implement final status independently of catalog advancement, stage outcomes and
  denominators, sanitized fields, run/attempt identity, C/S confirmation lag,
  explicit missing measurements and truthful 64/8/90 retention/aggregates.
- Implement one collection-only thin Action and read-only acquisition plus trusted
  write-publisher/finalizer jobs, step-scoped credentials, disabled checkout
  credential persistence and pinned dependencies. Validate bounded transferred
  artifacts and input/run/hash bindings; never execute artifact-supplied code.
- Prepare hourly/manual oldest-first orchestration without active-run cancellation,
  safe quota reserves, no in-run retries/sleep, and settings exposed for measurement
  rather than hardcoded 500-source ceilings. A batch remains partial full-catalog
  coverage. Keep discovery manual and enrollment explicit.
- Test source/whole-run failures, schema rejection, interrupted acquisition/rerun,
  wrong-parent races, ambiguous writes, v2 success followed by v3 failure, missing
  candidate evidence, final-summary failure and newer C with older S. No public
  start record or guaranteed report delivery. Clean run-local temporary files on
  normal exit; disposable runner teardown handles interruption.

## Evidence and boundary

Record focused tests, bytes/counts, changed/reused blobs, timings and memory scope.
Run the accepted saved seed-plus-three rehearsal when these slices are usable;
share its receipt with ticket 14, do not repeat it merely because tickets differ.
Code/workflow preparation remains local. No dispatch, fresh acquisition, remote
write, enrollment, installed-host operation or deployment is authorized here.
