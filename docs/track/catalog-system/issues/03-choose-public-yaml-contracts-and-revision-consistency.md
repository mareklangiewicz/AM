# Choose public YAML contracts and revision consistency

Type: grilling
Label: wayfinder:grilling
Status: open
Blocked by: 01

## Question

What versioned document boundaries and revision relationships provide one coherent
public YAML interface while preserving existing catalog readers?

Decide catalog versus operational-summary placement, schema/version negotiation,
grammar/domain-validator separation, unknown/missing/refused data, snapshot
resolution, and source/recipe/policy/run revision bindings. Existing browser reads
remain pinned and lazy unless explicitly reopened through evidence.
Handle the whitelist that currently accepts only apps.yaml and repositories/*.yaml.

Specify how the latest failed attempt is discoverable while the last good catalog
stays unchanged, including unavailable summaries and publication races. A file
cannot embed its enclosing commit hash. Define cross-revision consistency without
silently mixing unrelated facts, and distinguish all four time concepts.

Compare bounded alternatives with Marek. Own document/consistency contracts here;
[Choose truthful health summaries and bounded statistics](08-choose-truthful-health-summaries-and-bounded-statistics.md)
owns metric meanings and summary contents. Produce linked contract sketches
and compatibility requirements, not production schemas or reader implementation.
