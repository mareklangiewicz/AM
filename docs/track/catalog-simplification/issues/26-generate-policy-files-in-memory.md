# Generate the policy files in memory, not commit them

Type: task
Label: implementation:task
Status: claimed
Triage: ready-for-agent
Blocked by: none

## Outcome

As decided in [Derive the collector's inputs](25-collector-inputs-from-catalog-and-recipes.md) (item 3): the collector,
the tests and `tools/upstream-merge` build `recipe-url-policies.json`'s and
`appimage-policies.json`'s rows in memory from `programs/` with the existing
generator. The committed files and `tree_generated_policy` go.

Measure first: time the in-memory build on the collector's runner shape. If it
adds enough to an hourly run to matter, stop and keep the committed copies
until [the script conversion](30-convert-inline-form-scripts-to-declarations.md);
record the numbers here either way, with a script under `scripts/26/`.
