# Implement incremental publication and final health

Type: task
Label: implementation:task
Status: claimed
Assignee: codex
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

## Progress — November 8, 2026

Local incremental/publisher/finalizer implementation and prepared workflow exist.
17 shared contract/publication tests pass (60.120 seconds), including disposable
remote publication, v2 success/v3 conflict, ambiguous writes, reporting failure,
newer C with unchanged older S, artifact refusal, run/input/hash checks, unknown
counts and 64-summary retention. 30 affected legacy test invocations pass
(46.293 seconds); workflow/action permissions, pinned Actions, credential
persistence, concurrency, bash syntax, shellcheck and whitespace checks pass.
No dispatch, remote write, enrollment or installed-host change occurred.

Parent validation now streams the exact pinned tree and retains source metadata;
selected sources decode lazily. Candidate validation reuses unchanged blob/metadata
only under an in-memory exact-parent/rule binding, and checks whole-tree identities.
A new process streams full validation again; no imported receipt/trust store is
accepted. Status uses a separate 100,000-file / 32 MiB tree-listing allowance to
fit complete 8-attempt detail at the intended workload without applying the
catalog's 20,000-file bound. Representative capacity remains ticket 14 work.

The prepared hourly/manual workflow has contents-read acquisition, a collection-only
Action, one-day inert artifacts, and separately checked-out contents-write
publisher/finalizer. `CATALOG_V3_ENABLED` remains unset/false until reviewed rollout.
Collection profile settings are exposed; existing production source is not pushed.
Status distinguishes known/absent/unknown input C and counts reports with unknown
source totals explicitly in daily aggregates. Publication confirms actual remote
acceptance; local commits and ambiguous results never count as confirmed.

The required saved 500-source seed rehearsal stopped at a real contract conflict:
[inspection receipt](../mime-conflict-12.json) records **6,691 assets across 10
sources** whose original `content_type` is the bare literal `raw`. The accepted
v3 contract refuses unknown bare MIME aliases, so it cannot preserve these facts.
No replacement MIME or alias expansion was invented. All preserved evidence is
untouched. Asked Marek whether to add an explicit `media_type_literal` escape
(recommended, preserving arbitrary original values including alias collisions)
or keep the current source-refusal policy. Continue the complete saved seed plus
three updates after this decision; do not claim rehearsal/capacity acceptance now.
This ticket remains claimed, not resolved. Ticket 13 remains dependent on it.

### Committed CLI smoke check

At `d36b16f7beaa75cd645784e825865ad1ab9535df`, the actual unmocked
`host_catalog.py collect` → `publish --enable-targets` path passed against
three channels in a disposable local bare remote, with no credentials or HTTP.
One synthetic saved empty response was selected from the real 500-source
configuration. Status correctly reports E=500, Q=1, zero HTTP attempts, absent
input target C and confirmed local v2/v3/status outputs. Target tree is 2,377 bytes;
its publisher-local object store is 1,581 bytes, explicitly not remote storage.
Collection left its parent ref unchanged. Temporary data/repos were removed on
normal exit. This is CLI/protocol wiring evidence, not real acquisition, coverage,
capacity or public activation. The MIME decision/rehearsal above remains pending.
