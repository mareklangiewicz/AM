# Choose one reusable collection interface and permissions

Type: grilling
Label: wayfinder:grilling
Status: claimed
Assignee: codex-interface
Blocked by: 03, 04, 05

## Question

What minimal CLI/module interface makes one pipeline serve saved-response replay,
fresh acquisition, preflight and explicit publication, with clear permissions?

Specify responsibilities around source adapter → normalized records →
validation/merge → YAML output. Place scheduling, budgets, checkpoint/storage,
credentials and publication explicitly. Reuse maintained modules; avoid parallel
experiment paths and an abstract plugin framework without a second use case.
Domain-specific schemas remain explicit; generic primitives need not depend on AM.

Define local no-credential operations, workflow read acquisition, write publication,
token exposure/checkout/dependency boundaries and supported shell/Lua consumer
requirements. Publication must be explicit, never an implicit collection Action
side effect. Specify a thin custom Action and whether a reusable orchestration
workflow actually removes duplication. Choose the supported entry points and
retirement path for any superseded ones with Marek; do not implement them here.

## Current input — accepted simpler recovery, November 7, 2026

Marek accepted redoing unfinished work after runner loss and final-summary-only
public health, with no public start update. No separate store, cross-run journal,
lease service or special publication gate is required. Use the resolved recovery
ticket's single-active-run, scheduled-retry and stop-on-conflict policy. Publication
still validates its candidate and checks the exact parent.

Attempt final summary publication after every normal outcome, including collection,
validation and publication failures. Abrupt termination or summary publication
failure may leave the previous timestamped “last reported run”; no guaranteed
delivery queue or public registration. Include links to the specific Actions run
and recent collection runs. Actions may require sign-in; reading the public summary
must not. Keep this finalization path small and make unreported outcomes explicit
as a limitation. The older input below is historical, not a requirement.

## Historical superseded progress input — November 7, 2026

[Durable progress and fair scheduling](../progress-and-scheduling-decision.md)
requires an explicit publication gate that validates owner fences, serializes
write initiation with takeover, persists write intent and reconciles ambiguous
remote results. A token check followed by an unguarded push is insufficient.
Coordinate the realization with storage and define how public registration,
private checkpoints and read-only acquisition use separate permissions. A failed
public progress projection must not destroy acknowledged private evidence.

## Prepared interface proposal — November 8, 2026

Pending Marek's decision. Source inspected at `eedf3b9c2`: the maintained
`host_catalog.py` already shares HTTP/saved-response normalization but also creates
a local commit before writing its report; the workflow then pushes. The workflow
grants contents-write permission for the entire job. Reuse these modules, not a
parallel collector. No source/interface changes are implemented here.

### Recommended supported interface

Keep `tools/catalog-collector/host_catalog.py` as the documented command, with
explicit `collect`, `validate` and `publish` subcommands. Exact flags follow in
implementation; these responsibilities and defaults are the decision:

- `collect`: resolve explicit source/policy/recipe inputs and exact prior catalog,
  choose oldest-first scope, acquire once, normalize, merge/retain, validate and
  write a run-local candidate plus sanitized outcome evidence. Saved-response mode
  uses this same path, original receipt times, no credentials and no network.
  Fresh mode uses read-only credentials. No remote publication or ref advancement.
  Preflight is collection plus validation with publication omitted, not another
  code path. Explicit scope/settings expose full versus selected-source work;
  defaults must fit normal thousands-of-apps updates, not truncate to today's 500.
- `validate`: check the bounded candidate and input bindings without credentials
  or network, independently of acquisition. Reuse the strict writer/shell-reader
  and domain checks. Accept unchanged-blob reuse only with matching validated-parent
  evidence keyed to exact commit and validation rules. If unavailable, validate the
  parent fully (streaming where practical) and create run-local evidence, then
  validate changed blobs and whole-candidate references. Never trust arbitrary
  receipt files or a descriptor's own claim; verify evidence origin or fall back
  to validation. Do not add a persistent trust/recovery service. Measure full-check
  cost and optimize within the accepted integrity rules if scale requires it.
- `publish`: an explicit write operation, independently validating its candidate
  and exact input revisions/parent before any remote update. Reuse the remote-free
  local publisher internally. Confirm remote acceptance before reporting success;
  stop on confirmed parent conflict, leave ambiguous results unknown. Finalize and
  attempt the separate status publication after every normal outcome, including
  refused catalog publication or no valid candidate. Health fields/outcome details
  come from ticket 08. No automatic merge, retries, journal or durable report queue.

Use the existing acquisition adapter, budget accounting, retained merge, writer,
Git and validation modules behind this command. Keep GitHub release facts explicit;
no generic adapter/plugin framework until a second concrete use case. Status is
independent of catalog success. Discovery stays the existing manually invoked
`catalog_sources.py scan/verify`, never automatic enrollment. Policy generation,
recipe refresh and host-cutover maintenance tools retain their separate scope.

### Recommended workflow and permissions

Use one orchestration workflow with two jobs: read-only acquisition/preflight,
then the small explicit write publisher/finalizer. A thin local custom Action
wraps collection only; it never pushes or embeds write credentials. No reusable
workflow in addition to this workflow yet: there is only one orchestration caller.
The Action and local CLI invoke the same maintained code. Do not add a second
implementation in Action YAML.

Check out an exact trusted maintained source revision with credentials persistence
disabled. Pin external Actions/dependencies and install them before supplying
step-scoped acquisition credentials. Give the acquisition job contents-read and
the publisher job contents-write. Treat the transferred run-local candidate/report
artifact as bounded untrusted data: bind workflow run/attempt, input commits and
content hashes, reject unexpected paths/size, and revalidate before publication.
No artifact-provided executable code, recipe evaluation, tokens, raw headers or
arbitrary diagnostic dumps. Write credentials are confined to the publisher job;
that job checks out its own trusted publisher rather than executing artifact code.
Artifacts are temporary transport, not a separate recovery/history store; set
short explicit retention during implementation.

Use a finalizer path that runs after normal acquisition/validation failure and
attempts a truthful final report even if there is no catalog candidate. Missing
artifacts cannot establish source outcomes; report only known workflow facts.
Abrupt termination/reporting failure may still leave no report, as accepted.
Share one workflow concurrency group across scheduled/manual collection, without
cancelling the active run. Keep twice-daily/manual cadence; concrete cron and
budget values follow operating measurements, respecting real quotas.

### Compatibility and retirement

Installed clients stay shell/awk; collector Python dependencies remain maintainer/
CI-only. Offer pinned format-3 YAML and explicit schemas to Lua consumers without
requiring Python/jq at consumption time; this decision adds no Lua runtime or
mandatory new Lua library. Reader API migration remains ticket 09.

During transition, map the old `host_catalog.py` invocation to documented explicit
operations only where behavior can remain compatible; never silently turn a
formerly local operation into a remote push. Move the maintained workflow to the
new commands in one reviewed change. Retire the monolithic entry path after its
callers/tests migrate, retaining historical evidence in Git. Do not reintroduce
already retired experimental collectors. Ticket 09 owns activation/rollback;
this proposal changes no workflow or installed reader now.

Decision requested: accept the single CLI, collection-only Action and two-job
permission split together. Routine flag/artifact naming and focused fixtures are
implementation mechanics, not separate product approval rounds.
