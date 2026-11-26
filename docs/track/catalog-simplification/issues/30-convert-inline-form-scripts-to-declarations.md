# Convert the inline-form scripts to recipe declarations

Type: task
Label: implementation:task
Status: open
Triage: needs-triage
Blocked by: 26

## Outcome

As decided in [Derive the collector's inputs](25-collector-inputs-from-catalog-and-recipes.md) (item 3): the 1,072
x86_64 scripts that still call `catalog-yaml.am` (count from
`scripts/25/measure.py` on `ab4d305ae`) become recipe declarations in
kitty's form, in batches. After
[ticket 26](26-move-policy-rows-into-recipes.md) their selection facts are
already `CATALOG_*` lines in each script; what's left is the install body. This is the step before
recipes become yamx YAML. Needs its own grilling for batch size and for the
scripts that don't fit a declaration module.
