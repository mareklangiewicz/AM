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
