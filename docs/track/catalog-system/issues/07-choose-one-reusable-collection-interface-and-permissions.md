# Choose one reusable collection interface and permissions

Type: grilling
Label: wayfinder:grilling
Status: open
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
